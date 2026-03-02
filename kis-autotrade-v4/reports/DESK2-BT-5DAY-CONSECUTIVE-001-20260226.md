# DESK2-BT-5DAY-CONSECUTIVE-001 — 5일 연속 백테스트 결과 보고서

- **작업 ID**: DESK2-BT-5DAY-CONSECUTIVE-001
- **일자**: 2026-02-26
- **선행**: DESK2-BT-FEEDER-PHASE1-003 (PASS)
- **목적**: 5일 연속 백테스트를 통한 DESK2 전략 통계적 유효성 검증

---

## 1. 실행 환경

- **대상 날짜**: 2026-02-19, 2026-02-20, 2026-02-21, 2026-02-24, 2026-02-25 (거래일 5일)
- **초기 자본**: 10,000,000원/일 (날짜별 독립, 이월 없음)
- **스크립트**: `scripts/backtest/desk2_live_parity_run.py`
- **서버**: root@[SERVER-IP]
- **가상환경**: `/root/kis-autotrade-v4/.venv`
- **브랜치**: phase-2c-command-center
- **DB**: localhost:5432/kisautotrade (kis_admin)

---

## 2. 사전 확인 결과 (STEP 0) — **실패로 인한 작업 중단**

지침: 아래 3개 확인 후 하나라도 실패 시 **중단하고 보고**함.

### (1) 서비스 상태

| 서비스 | 상태 |
|--------|------|
| kis-v41-api | **inactive** |
| kis-v41-monitor | active |
| kis-v41-scheduler | active |

- 재시작 금지 규칙에 따라 현황만 기록. API 비가동 상태임.

### (2) strategy_cards 카드 수

| 항목 | 목표 | 실제 | 판정 |
|------|------|------|------|
| strategy_cards COUNT | 62 | **60** | **FAIL** |

- **실패 사유**: 카드 수 60건으로 목표 62건 미달.
- **조치**: 본 작업(5일 연속 백테스트) STEP 1 이후 진행 중단.

### (3) 활성 포지션 (기록용, 수정 금지)

- **조회**: `v4_positions` 에서 `status='OPEN'` (컬럼명: `ticker` 사용, `stock_code` 아님)
- **결과**: **14건**
- **ticker 목록**: 088350, 221800, 004060, 419430, 452260, 006340, 001510, 001290, 373110, 360140, 002630, 003530, 152550, A005930

---

## 3. 중단 요약 및 다음 단계 제안

- **판정**: **STEP 0 FAIL** — strategy_cards 62건 미충족(현재 60건).
- **5일 연속 백테스트(STEP 1~5)**: 미실행(사전 확인 실패로 중단).

### 다음 단계 제안

1. **strategy_cards 62건 복구**
   - 카드 2건 부족 원인 확인(삭제/비활성화 이력 등).
   - 필요 시 카드 복구 또는 목표치(62) 재검토 후, 동일 사전 확인(STEP 0) 재실행.
2. **사전 확인 재통과 후**
   - STEP 1(5일 연속 백테스트) ~ STEP 5(검증 및 보고) 재수행.
3. **선택**: kis-v41-api inactive 원인 점검(재시작은 규칙상 금지이므로 원인 분석만 권장).

---

## 4. CEO 보고 요약

- **보고서 raw URL**:  
  https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/DESK2-BT-5DAY-CONSECUTIVE-001-20260226.md
- **푸시 검증**: HTTP 200 확인됨.
- **5일 합산**: 미실행(STEP 0 실패로 백테스트 미수행). 총 거래수·총 손익·평균 일일 수익률 산출 불가.
- **실매매 전환 기준**: 판정 불가(5일 결과 미수집).
- **다음 단계 제안**: strategy_cards 62건 확인/복구 후 STEP 0 재실행 및 5일 연속 백테스트 플로우 재진행.
