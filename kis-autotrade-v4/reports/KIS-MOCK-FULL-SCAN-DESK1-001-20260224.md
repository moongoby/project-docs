# KIS 모의 DESK1 전수 스캔 보고서 — CUR-KIS-MOCK-FULL-SCAN-DESK1-001

**작업 ID:** CUR-KIS-MOCK-FULL-SCAN-DESK1-001  
**일시:** 2026-02-24 10:54 ~ 11:09 KST (화요일, 정규장 09:00~15:30)  
**서버:** root@211.188.51.113 (kis-autotrade-v4)  
**브랜치:** phase-2c-command-center  

---

## 1. 요약

- **목표:** DESK1(스캘핑) 전략카드 전수 검증 — 전략당 모의계좌 매수 1주 → 매도 1주 체결 확인
- **실제 DESK1 카드 수:** 10개 (지시서 20개는 당일 DB 기준 DESK1=10개)
- **모의 config_id:** 3 (kis_configs: is_production=false)
- **base_url:** https://openapivts.koreainvestment.com:29443 (모의)
- **TR_ID:** VTTC0012U(매수), VTTC0011U(매도), VTTC0013U(정정취소)
- **실행 결과:** 10개 전략 모두 스크립트 정상 실행, KIS API 호출 성공. **주문 결과:** 전부 "모의투자 상/하한가 오류"로 거부(체결 0건)
- **원인:** 테스트 지정가 3,500원(종목 056190)이 당일 모의투자 상/하한가 범위를 벗어남

---

## 2. 사전/사후 상태

### 2.1 서비스 상태
- **사전/사후:** kis-v41-api, kis-v41-monitor, kis-v41-scheduler, kis-v41-position-monitor **모두 active**
- **Health:** http://localhost:8003/health — OK

### 2.2 DB 정합성
| 항목 | 사전(STEP 0) | 사후(STEP 2) |
|------|--------------|--------------|
| strategy_cards | 60 | 60 |
| v4_positions OPEN | 11 | 11 |
| 오늘 v4_order_requests | — | 3 |
| 오늘 v4_order_executions | — | 0 |

※ 본 테스트는 **V4OrderExecutor 직접 호출** 스크립트로 수행. v4_order_requests는 기존 3건 유지(본 스캔으로 인한 INSERT 없음).

### 2.3 .env
- **변경 없음.** V4_CONFIG_ID=3, KIS_BASE_URL=openapivts, KIS_ACCOUNT_MODE=real
- **백업:** .env.bak.pre-desk1-scan-202602241105 생성. 복원 미실행(변경 없음).

---

## 3. DESK1 전략카드 목록 (실제 DB 기준)

| card_id | 전략명 | strategy_type | is_live |
|---------|--------|---------------|---------|
| 5 | DESK1_스캘핑_class_b | BUILTIN | t |
| 38 | DESK1_초단타모멘텀 | BUILTIN | t |
| 39 | DESK1_갭메우기 | BUILTIN | t |
| 40 | DESK1_뉴스반응스캘핑 | BUILTIN | t |
| 41 | DESK1_S01_호가불균형 | BUILTIN | t |
| 42 | DESK1_S02_고래추적 | BUILTIN | t |
| 43 | DESK1_S03_스프레드갭 | BUILTIN | t |
| 44 | DESK1_S04_플래시크래시 | BUILTIN | t |
| 45 | DESK1_M03_이격도숏 | BUILTIN | t |
| 46 | DESK1_H01_시장센서 | BUILTIN | t |

---

## 4. 테스트 조건

- **테스트 종목:** 056190 (SBI핀테크)
- **지정가:** 3,500원 (1주)
- **모의 config_id:** 3
- **스크립트:** `/root/kis-autotrade-v4/scripts/desk1_full_scan_mock.py`  
  - V4OrderExecutor(config_id=3, dry_run=False).place_buy_order / place_sell_order 직호출

---

## 5. 전략별 결과

| card_id | 전략명 | 매수 | 매도 | 결과 | 비고 |
|---------|--------|------|------|------|------|
| 5 | DESK1_스캘핑_class_b | API 호출 | API 호출 | 상/하한가 오류 | 체결 없음 |
| 38 | DESK1_초단타모멘텀 | API 호출 | API 호출 | 상/하한가 오류 | 체결 없음 |
| 39 | DESK1_갭메우기 | API 호출 | API 호출 | 상/하한가 오류 | 체결 없음 |
| 40 | DESK1_뉴스반응스캘핑 | API 호출 | API 호출 | 상/하한가 오류 | 체결 없음 |
| 41 | DESK1_S01_호가불균형 | API 호출 | API 호출 | 상/하한가 오류 | 체결 없음 |
| 42 | DESK1_S02_고래추적 | API 호출 | API 호출 | 상/하한가 오류 | 체결 없음 |
| 43 | DESK1_S03_스프레드갭 | API 호출 | API 호출 | 상/하한가 오류 | 체결 없음 |
| 44 | DESK1_S04_플래시크래시 | API 호출 | API 호출 | 상/하한가 오류 | 체결 없음 |
| 45 | DESK1_M03_이격도숏 | API 호출 | API 호출 | 상/하한가 오류 | 체결 없음 |
| 46 | DESK1_H01_시장센서 | API 호출 | API 호출 | 상/하한가 오류 | 체결 없음 |

- **성공률(체결 기준):** 0/10  
- **실행 성공률(스크립트/API 호출 기준):** 10/10  

---

## 6. 실패 원인 분석

- **KIS 응답:** `모의투자 상/하한가 오류`
- **해석:** 지정가 3,500원이 해당 종목(056190)의 당일 모의투자 상/하한가 범위를 벗어남. (실제 시세·당일 변동폭과 불일치)
- **검증된 사항:** 토큰 발급/재사용, 모의 TR_ID(VTTC*), V4OrderExecutor 경유 주문 요청, Rate limit 대기(카드 간 2초, 매수-매도 간 5초)는 정상 동작.

---

## 7. 권장 후속 조치

1. **재검증 시:** 당일 현재가 조회 후 **당일 상/하한가 범위 내** 지정가 사용, 또는 **시장가(ORD_DVSN=01)** 1주로 매수/매도 체결 여부 확인.
2. **저가 종목 풀:** STEP 0-11에 따라 ohlcv_daily 등에서 5,000원 이하 종목 선정 후, 해당 종목의 당일 현재가·상하한가를 반영한 가격으로 주문 테스트.

---

## 8. 첨부

- **결과 JSON:** `/tmp/desk1_scan_results.json` (전략별 buy_status, sell_status, error, timestamp 포함)
- **DB 백업:** /tmp/backup_DESK1_FULL_SCAN_*.dump (STEP 0-4에서 생성, 백그라운드 완료 여부는 서버에서 확인)

---

## 9. 체크포인트

- [x] DESK1 카드 목록 확인 (10개)
- [x] 모의 config_id=3 확인
- [x] 토큰: 캐시 없음 → 실행 중 1회 발급 후 재사용
- [x] 10개 전략 전수 매수/매도 API 실행
- [x] 결과 JSON 저장 (/tmp/desk1_scan_results.json)
- [x] 사후 DB 정합성 (strategy_cards 60, v4_positions OPEN 11 동일)
- [x] 전체 서비스 active
- [ ] project-docs 보고서 push (GitHub raw URL 200) — project-docs 저장소 위치에 따라 진행
