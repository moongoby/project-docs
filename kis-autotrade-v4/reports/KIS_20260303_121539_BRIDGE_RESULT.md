---
project: GO100
task_id: CUR-GO100-PAPER-FIX-001
completed_at: "2026-03-03T12:18:45+09:00"
---

[인계 확인]
직전 완료: CUR-V41-DIRECTIVE-AUTOMATION-002
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001, D-002, D-007
strategy_cards: 60
open_positions: 14

# CUR-GO100-PAPER-FIX-001 실행 결과

## 작업1: 스냅샷 스케줄러 확인 및 백필

### 조사 결과
- `/data/go100-api` 디렉토리: **존재하지 않음**
- crontab snapshot 크론: **등록 없음** (root 및 현재 사용자 모두)
- 스냅샷 로직 위치: `backend/app/services/go100/paper_trading/paper_engine.py`의 `_save_snapshot()` 메서드

### 백필 실행
- **대상 portfolio_id**: 6 (user_id=3, go100_card_id=15)
- **기존 스냅샷**: 2026-02-24, 2026-02-25 (2건)
- **누락 기간**: 2026-02-26 ~ 2026-03-03 (거래일 기준)
- **paper_trades 건수**: 0건 (변동 없음 → 02-25 상태 그대로 복사)

### 삽입된 스냅샷 (4건)
| snapshot_date | total_equity | current_cash | total_invested | total_eval | open_positions | total_return_pct |
|--------------|-------------|-------------|---------------|-----------|----------------|-----------------|
| 2026-02-26 | 9,999,700.42 | 8,002,525.42 | 1,997,175.00 | 1,997,175.00 | 1 | -0.0030 |
| 2026-02-27 | 9,999,700.42 | 8,002,525.42 | 1,997,175.00 | 1,997,175.00 | 1 | -0.0030 |
| 2026-03-02 | 9,999,700.42 | 8,002,525.42 | 1,997,175.00 | 1,997,175.00 | 1 | -0.0030 |
| 2026-03-03 | 9,999,700.42 | 8,002,525.42 | 1,997,175.00 | 1,997,175.00 | 1 | -0.0030 |

- 제외일: 2026-02-28(토), 2026-03-01(일/삼일절 공휴일)
- **결과**: INSERT 4건 성공 (ON CONFLICT DO NOTHING)

## 작업2: 중복 세션 정리

### 작업 전 상태
| session_id | strategy_card_id | status | created_at |
|-----------|-----------------|--------|-----------|
| 1 | 35 | ACTIVE | 2026-02-27 15:53:53 |
| 2 | 35 | ACTIVE | 2026-02-27 15:54:41 |

### 실행
```sql
UPDATE go100_paper_trading_sessions SET status='CANCELLED' WHERE session_id=1;
```

### 작업 후 상태
| session_id | strategy_card_id | status |
|-----------|-----------------|--------|
| 1 | 35 | **CANCELLED** |
| 2 | 35 | ACTIVE |

- **결과**: UPDATE 1건 성공

## 작업3: 검증

```
     tbl      | count |              max
--------------+-------+-------------------------------
 snapshots    |     6 | 2026-03-03
 sessions     |     1 | 2026-02-27 15:54:41.526362+09
 paper_trades |     0 |
```

### 검증 결과
- ✅ snapshots: 6건 (02-24/02-25 기존 + 02-26/02-27/03-02/03-03 신규), max=2026-03-03
- ✅ sessions ACTIVE: 1건 (session_id=2만 활성)
- ✅ paper_trades: 0건 (정상, 모의 거래 없음)

## 추가 발견사항

- `go100_portfolios` 테이블과 `go100_paper_trading_sessions` 테이블은 별개 구조:
  - portfolios (신규): portfolio_id 6 (user_id=3), portfolio_id 7 (user_id=2)
  - sessions (구조): session_id 1,2 (user_id=2)
- Portfolio 7 (user_id=2, card_id=13): 스냅샷 없음 → 향후 생성 필요
- snapshot 자동 크론 미등록 → `paper_engine.py` 로직이 트레이드 실행 시에만 생성

## 완료 체크포인트
- [x] DB 작업 완료 (스냅샷 백필 4건 + 세션 취소 1건)
- [x] 검증 쿼리 PASS (3항목 전체)
- [ ] project-docs 보고서 push (done_watcher.sh가 자동 처리 예정)
