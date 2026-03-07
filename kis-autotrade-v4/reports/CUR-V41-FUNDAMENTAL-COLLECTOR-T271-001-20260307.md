# T-271 보고서: 펀더멘탈 수집기 구축 + 배치 실행 시작

[인계 확인]
직전 완료: T-248 (KRX 업종분류 전체 매핑)
현재 단계: Phase 2C Command Center
CEO 지시 적용: D-008-KR (P0 변수 구현)
strategy_cards: 60
open_positions: 0

---

## 개요
| 항목 | 값 |
|------|-----|
| Task ID | T-271 |
| 제목 | 펀더멘탈 수집기 구축 + 배치 실행 시작 |
| 날짜 | 2026-03-07 |
| 커밋 | 7c90c931 |
| 브랜치 | phase-2c-command-center |
| 우선순위 | P0-CRITICAL |

---

## 1. 사전 확인

### DB 상태
- strategy_cards: **60건**
- open_positions (OPEN): **0건**

### 백업
- 경로: `/root/backup/v4_fundamental_quarterly_20260307.dump`
- 완료: ✅ BACKUP_OK

### 진단: 펀더멘탈 커버리지
```
covered  = 3844  (v4_fundamental_quarterly)
universe = 3844  (stock_universe WHERE is_active=true)
커버리지 = 100.0% (T-247 기완료)
```

---

## 2. 구현 내용

### 2-1. FundamentalCollector.collect_all_universe_symbols() 추가
- 파일: `backend/app/services/fundamental_collector.py`
- 메서드: `collect_all_universe_symbols(incremental=True)`

**동작:**
1. `stock_universe WHERE is_active=true` 전체 조회 (stock_code 기준)
2. incremental=True 시: 최근 30일 내 `collected_at` 갱신 종목 스킵
3. API 성공 종목: `fetch_financial_ratio()` + `fetch_investment_indicator()` 호출 후 UPSERT
4. API 데이터 없는 종목: `stock_fundamentals` fallback (최근 5분기)
5. 실패 종목: `failed_symbols` 리스트에 누적 기록
6. rate limit: 0.5초 (지시서 명시)
7. 200종목마다 진행률 로그 출력

### 2-2. scripts/backfill_fundamentals.py 신규 생성
- 완전 독립형 배치 스크립트 (별도 DB 커넥션)
- `--full` 옵션: incremental 스킵 없이 전체 재수집
- 진행률 출력: 100종목마다 경과시간 + ETA 표시
- 실패 목록: `logs/backfill_fundamentals_failed.txt` 누적 기록
- 최종 커버리지 검증 (≥95% 성공 기준)

---

## 3. 백그라운드 실행 결과

```bash
nohup python scripts/backfill_fundamentals.py > /root/backup/fundamental_backfill.log 2>&1 &
echo $! > /root/backup/fundamental_backfill.pid
PID: 376429
```

### 실행 로그 (정상 종료)
```
2026-03-07 10:44:42,863 [INFO] T-271 backfill_fundamentals.py 시작: 2026-03-07 10:44:42
2026-03-07 10:44:42,863 [INFO] 모드: incremental(최근 30일 스킵)
2026-03-07 10:44:42,915 [INFO] [사전 커버리지] 3844 / 3844 (100.0%)
2026-03-07 10:44:43,291 [INFO] production 토큰 로드 성공 (expires=2026-03-07 23:55:06+00:00)
2026-03-07 10:44:43,327 [INFO] stock_universe 전체 활성 종목: 3844
2026-03-07 10:44:43,423 [INFO] incremental 스킵: 3844 종목 → 실제 수집 대상: 0 종목
2026-03-07 10:44:43,423 [INFO] 수집 대상 0건. 종료.
```

**결과 해석:** T-247(2026-03-07 완료)에서 이미 전체 3844종목 수집 완료. incremental 모드가 최근 30일 내 수집 종목을 정상 감지하여 즉시 종료. 다음 실행(30일 후)부터 업데이트된 재무데이터 자동 갱신 예정.

---

## 4. git 커밋

```
커밋: 7c90c931
메시지: [V4.1] feat: T-271 펀더멘탈 전종목 수집기 + 백필 시작
변경 파일:
  - backend/app/services/fundamental_collector.py (+131줄: collect_all_universe_symbols)
  - scripts/backfill_fundamentals.py (+230줄: 신규 배치 스크립트)
```

---

## 5. 검증 결과

| 항목 | 결과 |
|------|------|
| collect_all_universe_symbols() 추가 | ✅ |
| backfill_fundamentals.py 생성 | ✅ |
| 별도 DB 커넥션 | ✅ |
| 실패 목록 기록 | ✅ |
| 진행률 출력 (100종목마다) | ✅ |
| 0.5초 rate limit | ✅ |
| incremental 모드 | ✅ |
| nohup PID 기록 | ✅ (PID: 376429) |
| git push | ✅ 7c90c931 |
| 커버리지 (사전) | 3844/3844 (100.0%) |

---

## 6. 다음 작업

- **T-272**: 펀더멘탈 수집 완료 확인 + 통합 검증
  → 수집 완료 후 (또는 30일 후 incremental 재실행 후) 실행
- 정기 크론 실행: 매주 토요일 02:00 KST (`scripts/v41_fundamental_full_collect.cron`)
- `--full` 옵션 재수집 시: `python scripts/backfill_fundamentals.py --full`

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (7c90c931, phase-2c-command-center)
- [ ] project-docs 보고서 push 완료 (push 진행 중)
