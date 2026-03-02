# DESK-OPT-STATUS 보고 (DESK 최적화 현황 및 예정)

**작업일**: 2026-02-22  
**서버**: [SERVER-IP]  
**경로**: /root/kis-autotrade-v4  
**작업 성격**: 읽기 전용 조사 (DB/파일 수정 없음)

---

## ★ 사전 확인 결과 (기준 충족)

| 항목 | 기준 | 결과 |
|------|------|------|
| strategy_cards COUNT | 59 | **59** ✓ |
| v4_positions OPEN | 5 | **5** ✓ |
| kis-v41-api | active (running) | **running** ✓ |
| kis-v41-monitor | active (running) | **running** ✓ |
| kis-v41-scheduler | active (running) | **running** ✓ |
| df -h / | 여유 확인 | **45% 사용, 52G 여유** ✓ |

---

## [DESK별 최적화 현황 요약]

| DESK | 전략수 (live/total) | 백테스트 ROI (대표 세션) | 최적화 상태 | 다음 작업 |
|------|---------------------|--------------------------|------------|-----------|
| DESK1 | 10/10 | 세션47 +28.42% (3M) | 완료 | 호가 수집·분봉 커버리지 점검, 실거래 연동 검증 |
| DESK2 | 10/16 | 세션61 +7.48% (3M), 세션62 -23.25% (2M 분봉) | 진행중 | 분봉 BT(62) 결과 반영·파라미터 튜닝, 3M 일봉 전략 유지 |
| DESK3 | 9/11 | 세션46 +26.92% (DESK3 11카드), 세션60 요약 없음 | 완료 | 수익 기여도 모니터링, 리밸런스 가중치 검토 |
| DESK4 | 6/9 | 세션50 +6.99% (3M) | 완료 | 기여도 ≈13% 유지, Calmar/리밸런스 반영 검토 |
| DESK5 | 1/10 | 세션51 +3.64% (3M) | 예정 | 자본 효율 개선, live 확대 시 CEO 승인 후 진행 |

- **desk_id NULL**: 전략 3건 (live 0, active 2) — DESK 미배정.

---

## [백테스트 세션 현황]

- **최근 주요 세션 (session_id DESC)**
  - **62** [DB] V2_BT-MIN-DESK2-2M: **COMPLETED** — ROI -23.25%, 승률 34.24%, MDD 23.32%, 거래 1,171건 (분봉 2개월).
  - **61** [DB] V2_BT-TUNE-DESK2-3M: **COMPLETED** — ROI **+7.48%**, 승률 41.55%, MDD 7.38%, 거래 503건 (일봉 3개월).
  - **60** [DB] V2_BT-TUNE-DESK3-3M: **COMPLETED** — `v4_backtest_summary`에 요약 없음 (ROI 등 미집계).
  - **59** [DB] V2_BT-TUNE-DESK2-3M: FAILED.
  - **58** [DB] V2_BT-TUNE-ALL-3M: COMPLETED (요약 없음).
  - **57~47** 이전 DESK별/전체 OPT·튜닝 세션 다수 (DESK1 세션47 +28.42% 등).

- **세션 62 (DESK2 분봉 BT)**  
  - status: COMPLETED, completed_at: 2026-02-22 03:36.  
  - `v4_backtest_trades` 건수: 1,171 (세션 62 기준).  
  - `run_backtest` 프로세스: 현재 실행 중인 프로세스 없음.

---

## [Promotion 현황]

- **v4_position_transfers**: 테이블 존재. **현재 건수 0** (유형별 집계 0건).
- 인계(Promotion) 이력 없음 — 추후 DESK2→3→4→5 인계 발생 시 해당 테이블에 기록됨.

---

## [OPEN 포지션 5건]

| id | desk_id | ticker | entry_price | current_price | pnl_pct | status | created_at |
|----|---------|--------|-------------|---------------|---------|--------|------------|
| 49 | 1 | 221800 | 19,070 | 19,070.00 | 0.00% | OPEN | 2026-02-20 08:59 |
| 51 | 2 | 001510 | 1,579 | 1,869.00 | 0.00% | OPEN | 2026-02-20 09:01 |
| 53 | 2 | 001290 | 1,175 | 1,287.00 | 0.00% | OPEN | 2026-02-20 09:01 |
| 55 | 3 | 373110 | 1,619 | 1,671.00 | 0.00% | OPEN | 2026-02-20 09:03 |
| 61 | 4 | 360140 | 12,935 | 13,285.00 | 0.00% | OPEN | 2026-02-20 09:05 |

- pnl_pct는 조회 시점에 0.00%로 적재됨(current_price는 갱신됨). 실시간 미실현 수익률은 모니터/API 기준으로 확인 필요.
- DESK5 OPEN 포지션 없음.

---

## [자금 배분]

- **테이블**: `v4_desk_fund` (v4_desk_fund_allocation / v4_desk_funds / v4_fund_pools 미사용 또는 없음).

| desk_id | desk_name | allocation_pct | allocated_amount | used_amount | 잔여(allocated−used) | current_positions |
|---------|-----------|----------------|------------------|-------------|----------------------|-------------------|
| 1 | DESK1_초단기 | 25% | 483,904,076 | 34,707,400 | 449,196,676 | 1 |
| 2 | DESK2_데일리 | 15% | 89,977,268 | 38,510,307 | 51,466,961 | 2 |
| 3 | DESK3_단기스윙 | 25% | 149,962,113 | 20,391,305 | 129,570,808 | 1 |
| 4 | DESK4_중기스윙 | 20% | 150,927,427 | 25,934,675 | 124,992,752 | 1 |
| 5 | DESK5_장기스윙 | 15% | 124,976,536 | 0 | 124,976,536 | 0 |

- 배분 비율: DESK1 25%, DESK2 15%, DESK3 25%, DESK4 20%, DESK5 15%.
- 모니터 로그와 일치 (총 투자금 119,543,687, DESK별 잔여 위와 동일).

---

## [Adaptive Engine 설정 현황]

- **파일**:  
  - `backend/app/schemas/adaptive_engine.py`, `adaptive.py`  
  - `backend/app/services/system/adaptive_bridge.py`  
  - `backend/app/services/adaptive/weekly_scoring.py` (scoring_weights, load_weights_from_db, v4_scoring_weights)  
  - `backend/app/services/adaptive/fund_rebalancer.py` (desk_allocation, rebalance, min_desk_allocation_pct, rebalance_cooldown_hours, _calculate_desk_weight)
- **키워드**:  
  - `desk_allocation` / `min_desk_allocation_pct`: fund_rebalancer에서 DESK별 최소 배분 비율·재배분 cooldown 사용.  
  - `weight` / `rebalance`: weekly_scoring의 가중치 정규화·복합 점수, fund_rebalancer의 재배분 타입·가중치 계산.  
  - Calmar는 본 조사 범위 내 grep 미노출(별도 모듈 가능).

---

## [최적화 예정 작업]

1. **DESK2 분봉 전략** — 세션 62 결과(-23.25%) 반영, 손절/진입 규칙·기간 재검토, 3M 일봉(세션61 +7.48%)과 병행 정리. (예상: 단기)
2. **DESK3** — 세션 60 요약 미존재 이슈 확인(재집계 또는 세션 46 등 기존 결과 활용). 수익 기여도 40–68% 구간 모니터링. (예상: 단기)
3. **DESK1** — 스캘핑 유니버스 708종목, 호가 수집기·분봉 데이터 커버리지 점검 및 실거래 연동 검증. (예상: 중기)
4. **DESK5** — 자본 효율 개선 후 live 전략 확대 시 CEO 승인 하에 strategy_cards UPDATE. (예상: 중기)
5. **Adaptive/자금 재배분** — v4_desk_fund 기반 배분과 fund_rebalancer·weekly_scoring 연동 점검, Calmar/리밸런스 주기 반영 검토. (예상: 중기)

---

## [DESK별 전략 카드 요약]

- **DESK1 (10장)**: S01~S04, M03, H01, class_b, 초단타모멘텀, 갭메우기, 뉴스반응스캘핑 — 전원 live.
- **DESK2 (16장)**: D01, S05, M00, M001, M002, 종가매매, 장초반레인지돌파, 갭상승후하락베팅, 거래량스파이크, 변동성확대 등 — live 10, 비 live 6.
- **DESK3 (11장)**: class_d, MACD크로스오버, 이동평균크로스, 지지저항반등/돌파, 채널돌파, MACD다이버전스, 볼린저밴드반등, M02 볼린저스퀴즈 등 — live 9, 비 live 2.
- **DESK4 (9장)**: class_e, 피보나치, 엘리어트, 일목, ParabolicSAR, 켈트너채널 등 — live 6, 비 live 3.
- **DESK5 (10장)**: class_f, 모멘텀팩터만 live, 나머지 9건 비 live.

---

- **strategy_cards COUNT: 59** ← 기준 충족  
- **v4_positions OPEN: 5** ← 기준 충족  

--- 보고 끝 ---
