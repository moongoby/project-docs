# 실거래 현황 종합 점검 보고서

**작성일**: 2026-03-03 14:40 KST
**담당**: Claude
**요청**: 매매 가능 여부, 계좌 실시간 동기화 여부, 실제 KIS API 데이터 여부 전면 점검

---

## 1. v4_desk2_trades — 시뮬레이션 데이터 (실매매 아님)

오늘 `v4_desk2_trades`에 6건이 있으나 **실제 KIS 주문 체결이 아님**.

| 항목 | 실제 값 |
|------|---------|
| created_at (6건 전부) | **2026-03-03 11:27:04** (동시 일괄 삽입) |
| kis_order_id 컬럼 | 존재하지 않음 (KIS 주문번호 추적 불가) |
| 생성 경위 | 시뮬레이션 스크립트가 실제 시장 가격 기반으로 일괄 삽입 |

실시간 체결이라면 각 종목마다 09:37, 09:47... 서로 다른 시각에 생성되어야 함.
→ **결론: v4_desk2_trades는 가상(시뮬레이션) 거래 기록**

---

## 2. 실계좌 실매매 현황 — 오늘 실주문 0건

### 실제 매매 엔진 상태

| 엔진 | 서비스 | 상태 | 실제 주문 |
|------|--------|------|----------|
| V4.1 Scheduler | `kis-v41-scheduler` | 실행 중 | ❌ `.env: DRY_RUN=true` 설정 → KIS API 주문 없음 |
| Webapp AutoTrade | `kis-trading-engine` | 실행 중 | ❌ 신호 생성기 60s timeout 매번 실패 (KIS VTS 500 에러) |
| Scalping | `kis-scalping` | 실행 중 | ❌ SQLAlchemy Session 에러 (`Instance not bound to Session`) |
| DESK2 AutoTrader | `desk2_auto_trader.py` | 크론 없음 | ❌ 자동 실행 스케줄 미설정 |

### DB 확인 (오늘 실주문)
- `autotrade_positions` WHERE DATE(created_at)='2026-03-03': **0건**
- `v4_positions` WHERE DATE(created_at)='2026-03-03': **0건**
- 마지막 실주문: `autotrade_positions` → 2026-02-13, `v4_positions` → 2026-02-25

### 원인 요약
1. **V4.1 스케줄러**: `DRY_RUN=true` 환경변수로 실주문 차단
2. **webapp 엔진**: KIS VTS 500 에러 → 신호 생성기 60s timeout → 신호 없음 → 주문 없음
3. **scalping**: ORM Session scope 버그로 모든 종목 처리 실패

---

## 3. 계좌 데이터 실시간 수집/동기화 — 미수행

| 항목 | 실제 상태 |
|------|----------|
| `account_snapshots` 최신 업데이트 | **2026-02-04** (28일 전, 동기화 안됨) |
| 실시간 잔액 조회 | `realtime_general_market_auto_trade.py` 실행되나 timeout으로 DB 저장 안됨 |
| moong123 실잔액 (오늘 직접 확인) | 492,955,708원 (스크립트 직접 실행 확인, DB 반영 안됨) |
| moongoby@gmail 실잔액 | 452,752,417원 (동일) |

**계좌 데이터는 28일째 갱신 안 되고 있음. 실시간 동기화 서비스 없음.**

---

## 4. KIS API 실제 데이터 수집 현황

| 수집 항목 | 서비스/스크립트 | 최신 데이터 |
|----------|----------------|-----------|
| 분봉 OHLCV | `kis-v41-minute-collector` | ✅ 실계좌(74032243) 기준 수집 중 |
| DESK2 후보종목 | `desk2_prescoring.py` (08:55 크론) | ✅ 오늘 10종목 수집됨 |
| DESK2 실시간 신호 | `desk2_realtime_signal.py` (5분 크론) | ✅ 12:32 마지막 수집 (KIS 실API) |
| 일봉 OHLCV | `kis-v41-scheduler` | ✅ 수집 중 |
| **계좌 잔액** | 없음 | ❌ 실시간 동기화 서비스 없음 |
| **주문 체결** | 없음 | ❌ 실주문 미발생 |

---

## 5. 총 정리

| 질문 | 사실 |
|------|------|
| v4_desk2_trades는 실제 KIS 매매인가? | ❌ 아님. 시뮬레이션 데이터 일괄 삽입 |
| 오늘 실계좌 매매가 있었나? | ❌ 없음 (0건) |
| 매매가 가능한 상태인가? | ❌ 전체 엔진 실주문 불가 상태 |
| 계좌 잔액이 실시간 동기화되나? | ❌ 28일째 미갱신 |
| KIS API 시세 데이터 수집은 되나? | ✅ 분봉/일봉/DESK2 신호는 수집 중 |

---

## 6. 해결 필요 과제

### 즉시
1. **V4.1 `DRY_RUN=false` 전환**: `.env` 수정 필요 (서비스 재시작 포함)
2. **webapp 엔진 timeout 240s 반영**: `unified_trading_scheduler.py` 수정했으나 서비스 재시작 필요 (현재 60s timeout 유지 중)

### 계좌 동기화
3. **`account_snapshots` 갱신 서비스**: KIS API 잔액 조회 후 DB 저장 스크립트/서비스 신규 구현 필요

### KIS 연결 오류
4. **KIS VTS 500 에러**: KIS 서버 측 문제. VTS 서버 정상화 전까지 webapp 엔진 신호 생성 불가
5. **kis-scalping Session 에러**: SQLAlchemy Session 스코프 버그 수정 필요
6. **dlrud7466 AppKey**: Fernet 키 불일치로 복호화 실패 → 재등록 필요

---

*이 보고서는 실제 코드/DB/로그 전수 확인 결과임*
