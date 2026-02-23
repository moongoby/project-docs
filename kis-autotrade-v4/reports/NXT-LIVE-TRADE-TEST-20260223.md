# NXT-LIVE-TRADE-TEST 보고서

| 항목 | 내용 |
|------|------|
| 작업 ID | NXT-LIVE-TRADE-TEST |
| 일시 | 2026-02-23 16:30~17:10 KST |
| 서버 | root@211.188.51.113 |
| 프로젝트 | /root/kis-autotrade-v4 |
| 브랜치 | phase-2c-command-center |
| 승인 | CEO 승인 (실계좌 실매매 테스트) |

---

## Phase A: 환경 확인 결과

| 항목 | 결과 |
|------|------|
| .env KIS_ACCOUNT_MODE | virtual (사전) |
| .env KIS_REAL_* | 비어 있음 (credentials는 DB kis_configs 암호화 저장) |
| kis_configs 실계좌 | id=2, 4 (실계좌 74***, is_production=true) |
| order_executor NXT 파라미터 | execution/order_executor.py에는 NXT 미사용. v4_order_executor는 order-cash 정규장 TR_ID만 사용 |
| kis_api_registry NXT | 웹소켓 nxt_price, nxt_overtime_price 등 조회용만 등록. 주문 TR_ID NXT 미등록 |
| strategy_cards | 65 |
| v4_positions OPEN | 5 |
| 현재 시각 | 2026-02-23 16:37 KST (NXT 애프터마켓 15:40~20:00 진행 중) |

---

## Phase B: 실계좌 전환

- .env 백업: `.env.bak.20260223_163900` 생성
- .env 수정: `KIS_ACCOUNT_MODE=real` (한 줄만 변경)
- V4_CONFIG_ID는 3 유지 (스케줄러는 모의 유지, 수동 테스트만 config_id=4 사용)

---

## Phase C: 서비스 재시작

- kis-v41-api 재시작 1회 (실계좌 전환)
- kis-v41-monitor, kis-v41-scheduler 재시작 없음
- 헬스체크: `{"status":"ok","database":"connected","redis":"connected"}`

---

## Phase D: 실계좌 잔고 확인

- config_id=4 (실계좌) 기준 V4OrderExecutor.get_balance() 호출
- 예수금(cash): 262,593원
- 평가총액(total_eval): 606,889원
- 보유종목: 6건 (002630, 003530, 004060 등)

---

## Phase E: NXT 실매매 테스트 결과

- 종목: 056190 (에스에프에이), 지정가 3,000원 1주
- 매수 주문: 정규장 TR_ID(TTTC0012U) 사용 → KIS 응답: **「장운영시간이 아닙니다.(정규시장(112) 시간 주문불가)」**
- 매도 주문: 동일 TR_ID(TTTC0011U) → 동일 사유로 주문 불가
- **실제 체결 없음.** 주문번호 없음. 포지션 정리 불필요.

**결론**: NXT 애프터마켓 시간대에는 정규장 현금주문 TR_ID(TTTC0012U/0011U)로는 주문이 불가하다. NXT/시간외 전용 TR_ID(예: 시간외 단일가 등) 및 파라미터 적용이 필요(Phase B-ALT).

---

## Phase F: 모의계좌 복원

- .env: `KIS_ACCOUNT_MODE=virtual` 복원
- kis-v41-api 재시작 2회 (모의 복원)
- 헬스체크: OK

---

## Phase G: DB 무결성 최종

| 테이블 | 건수 |
|--------|------|
| strategy_cards | 65 |
| v4_positions OPEN | 5 |

---

## 결론 및 후속 조치

1. **실계좌 전환·복원**: 정상 수행. API 재시작 2회만 사용.
2. **NXT 실체결**: 미달성. 원인: NXT 시간대에 정규장 TR_ID 사용 → KIS에서 거절.
3. **후속**: NXT/시간외 주문용 TR_ID 및 거래소구분 파라미터를 KIS 개발자 문서에서 확인 후, v4_order_executor 또는 별도 NXT 주문 경로 추가 시 검수 진행 권장.

---

## 체크리스트

- [x] Phase A: 환경 확인 완료
- [x] Phase B: 실계좌 전환 완료
- [x] Phase C: API 재시작 + 헬스체크 OK
- [x] Phase D: 잔고 조회 OK (예수금 > 0)
- [x] Phase E: NXT 매수/매도 시도 (정규장 TR_ID 한계로 체결 없음)
- [x] Phase F: 모의계좌 복원 완료
- [x] Phase G: DB 무결성 OK
- [x] Phase H: 보고서 작성
- [x] .env 커밋 안 함
- [x] kis-v41-monitor/scheduler 재시작 안 함

---

## 2차 테스트 (2026-02-23 17:53 KST)

| 항목 | 내용 |
|------|------|
| 시각 | 2026-02-23 17:57 KST (NXT 애프터마켓 15:40~20:00 내) |
| 작업 | NXT 실매매 테스트 절차 STEP 0 ~ STEP 8 |

### STEP 0: 사전 확인

| 항목 | 결과 |
|------|------|
| strategy_cards | 60 |
| v4_positions OPEN | 5 |
| kis-v41-scheduler / monitor / api / position-monitor | 전부 active |
| 디스크 / | 55% (43G 가용) |
| .env 모드 | KIS_ACCOUNT_MODE=virtual, DRY_RUN=false |
| 실계좌 .env 키 | KIS_REAL_APP_KEY, KIS_REAL_APP_SECRET, KIS_REAL_ACCOUNT_NUMBER 존재하나 **값 비어 있음** |

### STEP 1: .env 백업

- 백업 생성: `.env.bak.pre-nxt-live-202602231758`
- 실계좌 전환: **미실행** — REAL_APP_KEY / REAL_APP_SECRET / REAL_ACCOUNT_NUMBER 미입력으로 전환 불가

### STEP 2 ~ STEP 5

- kis-v41-api 재시작: 미실행 (실계좌 전환 없음)
- 토큰 발급·잔고 조회·NXT 매수/매도: **미실행** (실계좌 credentials 없음)

### STEP 6: .env 복원

- .env 변경 없음 → 복원 절차 검증만 수행. KIS_ACCOUNT_MODE=virtual 유지 확인.

### STEP 7: DB 무결성 최종

| 테이블 | 건수 |
|--------|------|
| strategy_cards | 60 |
| v4_positions OPEN | 5 |

OPEN 포지션: id 49(221800), 51(001510), 53(001290), 55(373110), 61(360140) — 변동 없음.

### STEP 8: 결론 (2차)

1. **실계좌 .env 미설정**: KIS_REAL_APP_KEY, KIS_REAL_APP_SECRET, KIS_REAL_ACCOUNT_NUMBER가 비어 있어 실계좌 전환 및 NXT 실매매 미진행.
2. **권장**: 실계좌 테스트 시 .env에 REAL_* 값을 설정하거나, kis_configs 실계좌(config_id=4 등) 사용 시 KIS_ACCOUNT_MODE=real만 전환하여 1차 테스트와 동일 방식으로 재실행. NXT 체결을 위해서는 1차 보고서 결론대로 NXT/시간외 전용 TR_ID 및 거래소구분(exchange_cd=NX) 적용 선행 필요.
3. **준수 사항**: monitor/scheduler/position-monitor 재시작 없음, DB ALTER/DROP/DELETE 없음, .env 백업 완료.
