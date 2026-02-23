# DESK1-BACKTEST-VERIFY 최종 보고서 (2026-02-23)

## 작업 개요
- **작업명**: DESK1-BACKTEST-VERIFY
- **서버**: 211.188.51.113
- **목적**: DESK1 라이브 10/10 카드에 대한 백테스트 검증 — 월요일 실매매 투입 전 최소 검증 (DESK2 -23.25% 교훈 반영)
- **DB/서비스 변경**: 없음 (v4_backtest_sessions, v4_backtest_trades INSERT만)

---

## 사전 확인
| 항목 | 결과 |
|------|------|
| strategy_cards | 62 |
| v4_positions (OPEN) | 5 |
| kis-v41-* 재시작 | 없음 |
| strategy_cards / v4_positions 직접 수정 | 없음 |

---

## Phase A — 백테스트 실행 요약

- **명령**: `scripts/backtest/run_backtest.py --start 20251101 --end 20260221 --capital 5000000 --name "DESK1-BT-VERIFY-20260223" --engine v2 --desk-strategies '[{"desk_id":1,"card_id":5},…,46}]'`
- **세션명**: `[CFG] V2_DESK1-BT-VERIFY-20260223`
- **session_id**: **66**
- **설정**: DB에서 DESK1 카드 전략 로드를 시도했으나, 해당 카드에 대한 **v4_desk_strategy_mapping** 매핑이 없어 **config.py fallback** 발생. config에서 DESK1 allocation 0%로 설정되어 있어, 실제 엔진은 **DESK2~5** 위주로 실행됨 (DESK1 전용 자금 배분 없음).

---

## Phase B — 결과 분석

### 세션 66 요약 (진행 중 일부 집계)
| 항목 | 값 |
|------|-----|
| session_id | 66 |
| 상태 | RUNNING (보고 시점; 완료 시 COMPLETED로 갱신) |
| BUY 건수 | 1,269 |
| SELL 건수 | 1,270 |
| 총 PnL (누적) | 706,721원 |

### desk_id별 SELL 거래 (session_id=66)
| desk_id | 거래 수 | 승수 | 평균 PnL(원) |
|---------|---------|------|-------------|
| 2 | 490 | 227 | 309 |
| 3 | 445 | 193 | 877 |
| 4 | 259 | 131 | 572 |
| 5 | 49 | 30 | 360 |
| **1 (DESK1)** | **0** | **0** | — |

### DESK1 카드(5, 38, 39, 40, 41, 42, 43, 44, 45, 46) 거래
- **card_id IN (5,38,39,40,41,42,43,44,45,46) 건수**: **0건**
- **원인**: config fallback으로 DESK1 자금 배분 0% → DESK1 시그널/진입 미발생.

### 거래 0건 카드 목록 (DESK1 전 카드)
| card_id | strategy_name (참고) |
|---------|----------------------|
| 5 | DESK1_스캘핑_class_b |
| 38 | DESK1_초단타모멘텀 |
| 39 | DESK1_갭메우기 |
| 40 | DESK1_뉴스반응스캘핑 |
| 41 | DESK1_S01_호가불균형 |
| 42 | DESK1_S02_고래추적 |
| 43 | DESK1_S03_스프레드갭 |
| 44 | DESK1_S04_플래시크래시 |
| 45 | DESK1_M03_이격도숏 |
| 46 | DESK1_H01_시장센서 |

- **진입 조건 엄격 여부**: 이번 run에서는 DESK1이 alloc 0%로 실행되지 않아, “진입 조건이 너무 엄격한지”는 판단 불가. **DESK1 전용 백테스트**를 하려면 v4_desk_strategy_mapping에 DESK1 카드 매핑 추가 후 동일 기간/동일 카드로 재실행 필요. (코드 수정 없이 현상만 기록)

---

## Phase C — v4_positions OPEN ID 불일치 확인

- **CONTEXT.md 기준**: ID 49, 51, 55, 58, 61
- **DESK1-LIVE-PREP 보고서**: 49, 51, 53, 55, 61
- **실제 DB 조회 결과 (2026-02-23)**:

| id | ticker | desk_id | card_id | status | entry_date |
|----|--------|---------|---------|--------|------------|
| 49 | 221800 | 1 | (NULL) | OPEN | 2026-02-20 |
| 51 | 001510 | 2 | (NULL) | OPEN | 2026-02-20 |
| 53 | 001290 | 2 | (NULL) | OPEN | 2026-02-20 |
| 55 | 373110 | 3 | (NULL) | OPEN | 2026-02-20 |
| 61 | 360140 | 4 | (NULL) | OPEN | 2026-02-20 |

- **v4_positions OPEN 정확한 ID**: **49, 51, 53, 55, 61** (5건)
- **불일치**: CONTEXT.md의 **58** → 실제는 **53**. (DESK1-LIVE-PREP와 실제 DB 일치)

---

## DB 무결성
- **strategy_cards**: 62건
- **v4_positions OPEN**: 5건 (ID: 49, 51, 53, 55, 61)

---

## 실매매 투입 권장/비권장

| 판단 | 내용 |
|------|------|
| **권장** | **보류** |
| **이유** | 이번 run은 DESK1 **전용** 백테스트가 아니며, DESK1 카드에 대한 거래가 0건으로 나옴. v4_desk_strategy_mapping에 DESK1 카드(5,38~46) 매핑을 넣고, **DESK1만** 대상으로 백테스트를 재실행한 뒤, 거래 건수·승률·평균 PnL이 확인된 후에만 소액 테스트 또는 실매매 투입을 검토할 것을 권장. |

---

## Phase D/E — 보고서 발행 및 동기화
- 보고서 경로: `report/v41/DESK1-BACKTEST-VERIFY-20260223.md`
- 발행: `bash /root/project-docs/scripts/publish_report.sh DESK1-BACKTEST-VERIFY`
- 동기화: `bash /root/project-docs/scripts/sync_kis.sh`
