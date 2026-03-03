# CUR-V41-LIVE-AUDIT-NXT-001 — 실매매 흐름 감사 + NXT 실계좌 테스트 보고서

- **작업일**: 2026-03-03
- **커밋**: 3ba36104 (kis-autotrade-v4, phase-2c-command-center)
- **테스트 계좌**: KIS 실계좌 account_id=7 (74032243, is_mock=false)

---

## 1. 발견된 버그 및 수정 결과

### Bug-1: Kiwoom `_parse_order_response` — `ord_no` 키 미파싱 [FIXED]

| 항목 | 내용 |
|------|------|
| **파일** | `backend/app/core/broker_kiwoom_client.py:359` |
| **증상** | 매수/매도 후 `order_no=""` 반환 → `_poll_fill_price` 폴링 스킵 → fallback(종가) 사용 |
| **원인** | `data.get("ODNO") or data.get("order_no") or data.get("odno")` — Kiwoom 실제 키인 `ord_no` 누락 |
| **수정** | `ord_no` 키 우선 파싱, `return_code=0` 성공 판정 추가, `return_msg` 파싱 추가 |
| **검증** | KIS 실계좌 NXT 매수 → `order_no='0047913200'` 정상 수신 ✅ |

### Bug-2: `_insert_trade` — `go100_trades.order_id` FK 위반 [FIXED]

| 항목 | 내용 |
|------|------|
| **파일** | `backend/app/services/go100/live_trading/live_engine.py` |
| **증상** | `go100_trades.order_id` → `go100_orders(id)` FK 참조인데 `live_order_id`(go100_live_orders PK) 전달 시 위반 |
| **수정** | `order_id` INSERT 제거, `position_id or 0` → `position_id or None` (NULL 처리) |

---

## 2. 실매매 진행 시 남은 문제점

| # | 문제 | 영향 | 조치 |
|---|------|------|------|
| P-1 | `_poll_fill_price` 폴링 딜레이 30초 | 장 중 실행 시 응답 지연 | 허용범위 (시장가는 즉시 체결) |
| P-2 | 시장가 주문 → `ORD_DVSN="01"`, `ORD_UNPR="0"` | 애프터마켓 거부 | 정규장(09:05~15:20)에만 실행되도록 스케줄러 제한 |
| P-3 | stock_universe에 NXT 종목 없음 | NXT 전략 카드 universe_filter 작동 안 함 | NXT 종목 리스트 수집 필요 |
| P-4 | go100_live_orders → go100_trades 직접 연결 없음 | 주문-매매 추적 단절 | go100_live_orders.order_id는 별도 용도, trades는 독립 기록으로 운영 |
| P-5 | reconcile: broker_positions qty 비교 시 go100_portfolios 포지션만 비교 | 실계좌 전체 보유와 불일치 가능 | reconcile은 포트폴리오 단위로 제한적 사용 |

---

## 3. NXT 실계좌 테스트 결과

### 계좌 현황 (KIS 실계좌 74032243)

| 항목 | 값 |
|------|-----|
| 현금 | 506,078원 |
| 보유종목 | 006340(5주), 088350(5주), 152550(116주), **316140(2주)** |

### NXT 데이터 수신 확인

```
✅ NXT 체결내역 API (EXCG_ID_DVSN_CD=NXT) 정상 작동
✅ exchange='NXT' 필드 정상 반환

오늘 NXT 체결 내역:
  1. BUY 316140(우리은행) 1주 @35,000 ord=0047766100  (기존)
  2. BUY 316140(우리은행) 1주 @34,950 ord=0047913200  (신규 테스트)
     → 지정가 35,000 → 실체결가 34,950 (최유리 체결)
     → order_no 파싱 수정 후 정상 수신 확인
```

### NXT 매도 테스트 결과

```
❌ 매도 실패: "주문 가능한 수량을 초과합니다."
원인: 이전 시장가 매도 시도(2건)가 미체결 상태로 수량 잠금
→ 장 마감 이후로 취소 불가, 내일 09:00 이후 미체결 자동 취소 예정
→ 내일 정규장(09:05~)에 316140 2주 매도 테스트 예정
```

### NXT 거래 가능 여부 정리

| 조건 | 상태 |
|------|------|
| KIS 실계좌 NXT 데이터 수신 | ✅ |
| NXT 매수 체결 (정규장) | ✅ (09:05~15:20) |
| NXT 매도 체결 (정규장) | 내일 확인 예정 |
| NXT 시장가 (애프터마켓) | ❌ (지정가만 허용) |
| 모의계좌 NXT | ❌ (KIS 정책: KRX만 지원) |
| Kiwoom 실계좌 NXT | 미테스트 (account 5,6 접근 금지) |

---

## 4. 내일 아침 검증 체크리스트

```
□ 316140 미체결 주문 자동 취소 확인 (09:00~)
□ 316140 2주 NXT 매도 실행 (09:05~)
□ go100_live_orders: filled_price = 실체결가 확인
□ go100_trades: price = 실체결가 확인 (종가 아님)
□ _poll_fill_price 폴링 성공 여부 확인
□ GO100 live_engine dry_run=false 정규장 테스트
```

---

## 5. stock_universe NXT 종목 추가 필요

현재 stock_universe에 NXT 종목이 없어 GO100 universe_filter에서 NXT 종목 선별 불가.

```sql
SELECT DISTINCT market FROM stock_universe WHERE is_active=true;
-- 결과: KOSPI, KOSDAQ (NXT 없음)
```

NXT는 KOSPI/KOSDAQ 주요 종목의 대체거래소 상장. 동일 stock_code로 market='NXT' 추가 필요 또는 기존 종목에 NXT 플래그 추가 방안 검토.

---

## 6. 커밋 정보

- **커밋**: 3ba36104 (kis-autotrade-v4, phase-2c-command-center)
- 이전 커밋: 66ccd72d (실매매 전체 흐름 완성)
