# KIS 모의계좌 실매매 테스트 보고서 — CUR-KIS-MOCK-TRADE-TEST-001

**작업 ID:** CUR-KIS-MOCK-TRADE-TEST-001  
**일시:** 2026-02-24 10:41 ~ 10:52 KST (화요일, 정규장)  
**서버:** root@[SERVER-IP] (kis-autotrade-v4)  
**브랜치:** phase-2c-command-center  

---

## 1. 요약

- **매매 방식:** V4.1 시스템 경유, KIS 모의계좌 (config_id=3)
- **base_url:** https://openapivts.koreainvestment.com:29443 (모의 도메인)
- **TR_ID:** 매수 VTTC0012U, 매도 VTTC0011U (모의)
- **결과:** 매수 1주 체결 → 매도 1주 주문 접수 완료

---

## 2. 사전/사후 상태

### 2.1 서비스 상태
- **사전/사후:** kis-v41-api, kis-v41-monitor, kis-v41-scheduler, kis-v41-position-monitor **모두 active**
- **Health:** http://localhost:8003/health — OK (database/redis connected)

### 2.2 DB 정합성 (스키마: v4_orders 테이블 없음, 절차서 대비 실제 테이블 기준)
| 항목 | 사전(STEP 0) | 사후(STEP 8) |
|------|--------------|--------------|
| strategy_cards | 60 | 60 |
| v4_positions OPEN | 11 | 11 |
| 오늘 order_requests | 3 | 3 |

※ 본 테스트는 **V4OrderExecutor 직접 호출**로 수행하여 v4_order_requests / v4_trade_executions 에 신규 기록 없음.

### 2.3 .env
- **변경 없음.** V4_CONFIG_ID=3, KIS_BASE_URL=openapivts 사전부터 동일.
- **백업:** .env.bak.pre-kis-mock-202602241047 생성 후 복원 미실행(변경 없음).

---

## 3. 모의계좌 및 토큰

- **모의 config_id:** 3 (kis_configs: account_number=50160711, is_production=false)
- **토큰:** V4OrderExecutor 내부에서 DB(kis_configs) 기반 발급 사용. Redis 캐시(token:kis:kis:3) 사전에 없음(TTL=-2). 매수 시 1회 발급 후 재사용. 잔고 조회 시 1분 미만 간격으로 재발급 시도하여 EGW00133(1분당 1회 제한) 발생 → 1분 대기 후 재조회/매도 진행.

---

## 4. 매매 내역

| 구분 | 종목코드 | 종목명 | 수량 | 주문가/체결가 | 주문번호 | 비고 |
|------|----------|--------|------|----------------|----------|------|
| 매수 | 014440 | (저가 5,000원 이하) | 1주 | 지정가 5,000원 → **체결가 4,965원** | 0000008940 | VTTC0012U |
| 매도 | 014440 | 동일 | 1주 | 지정가 5,000원 | 0000009031 | VTTC0011U |

- **매수 체결 확인:** 잔고 조회로 014440 1주, avg_price 4,965원 확인.
- **매도:** 주문 접수 완료. 체결은 호가 도달 시 처리.

---

## 5. 수수료 및 P&L

- **실현 P&L (매도 체결 가정):** (5,000 - 4,965) × 1 = **35원** (수수료 별도, 모의계좌 기준 미세)

---

## 6. 타임라인

1. **10:41~10:46** STEP 0: KST 확인, 서비스/DB 스냅샷, pg_dump 백업, kis_configs 확인, .env 확인  
2. **10:47** STEP 1: .env 백업  
3. **10:47** STEP 2: 변경 없음 → API 재시작 스킵  
4. **10:47~10:48** STEP 3: Redis 토큰 없음, 잔고 조회 성공 (cash 480,093,693, total_eval 500,200,128)  
5. **10:48** STEP 4: ohlcv_daily 기준 5,000원 이하 종목 014440 선택  
6. **10:48~10:49** STEP 5: V4OrderExecutor(config_id=3, dry_run=False).place_buy_order("014440", 1, 5000) → 주문번호 0000008940  
7. **10:49~10:51** 토큰 1분 제한 대기  
8. **10:51** 잔고 조회로 014440 1주 체결 확인, place_sell_order("014440", 1, 5000) → 주문번호 0000009031  
9. **10:52** STEP 7~8: .env 복원 스킵, DB 정합성 확인, 서비스 확인  

---

## 7. 체크포인트

- [x] 사전 DB 스냅샷 기록  
- [x] .env 백업 완료  
- [x] KIS 모의 config_id 확인 (3)  
- [x] 토큰: 캐시 없음, 매수 시 1회 발급 후 재사용  
- [x] 잔고 조회 성공  
- [x] KIS 모의 매수 체결 (TR_ID=VTTC0012U)  
- [x] KIS 모의 매도 주문 접수 (TR_ID=VTTC0011U)  
- [x] P&L 기록 (35원, 매도 체결 가정)  
- [x] .env 복원: 변경 없음  
- [x] 사후 DB 정합성 (strategy_cards, OPEN 동일)  
- [x] 전체 서비스 active  

---

## 8. 참고

- **주문 실행 경로:** V4OrderExecutor 직접 호출 (config_id=3, dry_run=False). API(trade_router) / v4_order_requests 미경유.
- **DB 백업:** /tmp/backup_KIS_MOCK_TRADE_20260224_104530.dump
