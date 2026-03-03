---
project: KIS
task_id: CUR-V41-DESK2-REMAINING-FIX-002
completed_at: 2026-03-03T10:22:00+09:00
---

[인계 확인]
직전 완료: CUR-V41-DIRECTIVE-AUTOMATION-002
현재 단계: Phase 2c (DESK2 정상화 + Virtual Run 운영)
CEO 지시 적용: D-001, D-002, D-003, D-007
strategy_cards: 60
open_positions: 14

---

# [CURSOR-KIS] DESK2-REMAINING-FIX-002 결과

## Phase 1 — 실시간 수집 전수 점검 (12개 테이블)

| 테이블 | rows | 최신 날짜 | 종목수 | 상태 |
|--------|------|-----------|--------|------|
| ohlcv_daily | 2,615,744 | 2026-02-27 | 3,844 | ✅ 정상 |
| v4_ohlcv_minute | 95,831,733 | **2026-03-03** | 3,623 | ✅ 오늘 수집 중 |
| v4_investor_daily | 275,846 | 2026-02-27 | 3,943 | ✅ 정상 (T+1) |
| v4_trade_strength | 234,727 | 2026-03-03 15:30 | 3,760 | ✅ 정상 |
| v4_orderbook_rt | 1,671,439 | 2026-03-03 10:18 | 20 | ✅ 실시간 수집 중 |
| v4_tick_data | 1,131,642 | 2026-03-03 10:18 | 21 | ✅ 실시간 수집 중 |
| v4_regime | 1,116 | 2026-02-27 | — | ✅ 정상 |
| v4_vkospi | 1,510 | **2026-02-26** | — | ⚠️ 02-27 갭 지속 |
| v4_theme_daily | 34,122 | 2026-02-27 | — | ✅ 정상 |
| v4_sector_daily | 15,086 | **2026-03-03** | 32 | ✅ 오늘 수집 완료 |
| v4_mock_trades | 49 | 2026-03-03 | — | ✅ 오늘 신호 기록 중 |
| news_items (go100) | 2,156,079 | 2026-03-02 17:10 | — | ✅ 정상 |

**총평**: 11/12 정상. v4_vkospi만 02-27 갭 잔존 (API T+1~T+2 지연 원인, 해소 불가)

---

## Phase 2 — DESK2 전용 테이블 활성화 방안

### DB 테이블 현황
| 테이블 | 존재 | 행수 | 코드 참조 |
|--------|------|------|-----------|
| v4_desk2_candidates | ✅ | 0 | desk2_feeder.py (INSERT 코드 존재) |
| v4_desk2_signals | ✅ | 0 | **참조 코드 없음** |
| v4_desk2_trades | ✅ | 0 | **참조 코드 없음** |
| v4_desk2_daily_summary | ✅ | 0 | **참조 코드 없음** |

### 핵심 발견
1. **v4_desk2_candidates**: `desk2_feeder.py`의 `feed_to_desk2_pool()` 함수가 INSERT 코드를 가지고 있으나 `scheduler.py`에서 호출되는 것으로 확인됨. 단, 실행 이력 없음(0행) → 스케줄러가 실제로 실행되지 않고 있음
2. **v4_desk2_signals**: CTE 파이프라인 신호 결과를 v4_desk2_signals로 INSERT하는 로직 **미존재** → 신규 코드 추가 필요
3. **v4_desk2_trades**: mock_trades → desk2_trades 동기화 로직 **미존재** → 신규 코드 추가 필요
4. **v4_desk2_daily_summary**: DCS 등급(A/B/C) 집계 로직 **미존재** → 신규 코드 추가 필요

### 필요 작업 목록 (P2 우선순위)
- [ ] `desk2_feeder.py` 스케줄러 연동 확인 및 강제 실행 (v4_desk2_candidates 데이터 생성)
- [ ] `cte_pipeline.py` → v4_desk2_signals INSERT 로직 추가 (신호 발생 시 연동)
- [ ] `order_executor.py` → v4_desk2_trades INSERT 로직 추가 (체결 시 연동)
- [ ] v4_desk2_daily_summary 집계 스크립트/크론 신규 작성

---

## Phase 3 — 오케스트레이터 MARKET_OPEN 전이 + 매매 활성화

### 오케스트레이터 상태
- **현재 상태**: IDLE (health endpoint 응답)
- **v4_system_state_log**: 0행 (상태 전이 이력 없음)
- **원인**: 오케스트레이터 자동 MARKET_OPEN 전이 코드가 스케줄러에 등록되어 있으나 미실행 상태. 직접 `run_unified_engine.py` 호출 방식으로 운영 중

### run_unified_engine.py signal 실행 결과 (2026-03-03 10:21)
```
통과: 2건
  - D7  221455 @ 112,901원 (CS=87, EQS=60)
  - D-ORB 343669 @ 21,897원 (CS=66, EQS=68)

차단: 5건
  - D6  407082: L3.3_SUPPLY synthetic_BLOCK
  - D5  371185: L3.3_SUPPLY synthetic_BLOCK
  - D4  190619: SIGNAL_COMBO (1/2)
  - D2  237768: GATE 반등확인 미통과 (1조건)
  - S1  349605: L3.3_SUPPLY synthetic_BLOCK
```

### VTS 주문 체결 확인
- **2026-03-03 v4_mock_trades**: 총 49건 (오늘 신호 2건 포함)
- D7(221455), D-ORB(343669) 신규 BUY 포지션 기록 완료
- 오케스트레이터가 IDLE이더라도 크론 → run_unified_engine.py 직접 호출 구조라 **매매 신호 생성은 정상 작동**

---

## Phase 4 — vkospi 02-27 갭 재시도

```bash
collect_vkospi.py --start 20260227 --end 20260227
결과: 저장=0, 실패=0
```

- **API T+1~T+2 지연**으로 02-27 데이터 아직 미제공 (기존 분석과 동일)
- **vkospi 최신 날짜: 2026-02-26** (갭 지속)
- 02-28 이후 자동 수집 크론이 보완할 예정 (잔존 갭 미해소)

---

## 매매 정상화 여부

**CONDITIONAL YES** — 조건부 정상화

- ✅ run_unified_engine.py 직접 실행 → 신호 생성 및 v4_mock_trades 기록 정상
- ✅ D7/D-ORB 2건 통과, 5건 정상 차단 (L3.3 필터 작동 확인)
- ⚠️ 오케스트레이터 자동 MARKET_OPEN 전이 미작동 (IDLE 유지)
- ⚠️ v4_desk2_signals/trades/daily_summary 0행 — DESK2 고유 파이프라인 미연결
- ❌ vkospi 02-27 갭 미해소 (API 한계)

**이유**: 크론 기반 run_unified_engine.py 직접 실행으로 매매 사이클 자체는 정상 작동하나, DESK2 전용 테이블 파이프라인 연결이 필요함. 오케스트레이터 자동 전이 문제는 별도 P2 작업으로 처리 필요.

---

## 후속 작업 권고
1. **P1**: desk2_feeder.py 스케줄러 강제 실행으로 v4_desk2_candidates 데이터 생성
2. **P1**: CTE 신호 결과 → v4_desk2_signals INSERT 로직 추가
3. **P2**: 오케스트레이터 MARKET_OPEN 자동 전이 스케줄러 점검
4. **P3**: vkospi 02-27/02-28 갭 크론 재시도 (T+2 이후 자동 해소 기대)
