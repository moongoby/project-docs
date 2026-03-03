# rank API 수정 및 신호 생성 복구 보고서

**작업일**: 2026-03-03 (오후)
**담당**: Claude

---

## 1. 발견된 버그 (API 문서 정밀 분석 결과)

### 버그 1: rank API TR_ID 오기재
| 항목 | 기존 (잘못됨) | 수정 (올바름) | 출처 |
|------|-------------|--------------|------|
| TR_ID | `FHKST03010100` | `FHPST01710000` | KIS API 문서 거래량순위.md |
| 실제 용도 | 국내주식기간별시세(일봉) | 거래량순위 | — |
| 모의투자 지원 | 미지원 | 미지원 | 문서 확인 |

### 버그 2: 필수 파라미터 누락
- `FID_INPUT_DATE_1: ""` (공란) 필수 — 문서 Required=Y
- 기존: 파라미터 없음 → OPSQ2001 에러

### 버그 3: KISAuth 암호화 키 미복호화 (`dynamic_stock_scanner.py`)
- DB에서 KISAuth 생성 시 `cfg.app_key` (Fernet 암호문) 직접 사용
- KIS API에 암호문이 AppKey로 전달 → 인증 실패 → fallback
- 수정: `decrypt_value(cfg.app_key/app_secret/access_token)` 적용

### 버그 4: rank API 실계좌 우선 선택 안됨
- 기존: `KISConfig.is_verified == True` → VTS 계정이 먼저 선택될 수 있음
- 수정: `is_production == True` 우선 → VTS fallback

### 버그 5: `ImprovedKISAPIClient`를 `get_top_100_stocks`에 직접 전달 시 실패
- `data_miner.get_top_100_stocks(auth)`가 `auth.request_with_retry()` 호출
- `ImprovedKISAPIClient`에 해당 메서드 없음 → AttributeError
- 수정: `hasattr(_get_headers)` 분기로 `requests.get` 직접 사용

### 버그 6: SQLite datetime() 문법 → PostgreSQL 에러
- `datetime('now', '-2 minutes')` → PostgreSQL 미지원
- 수정: `NOW() - INTERVAL '2 minutes'`

### 버그 7: VTS rate limit EGW00201
- VTS 초당 3~4건 제한 (실전 20건 대비 훨씬 엄격)
- `ImprovedKISAPIClient`의 `RateLimiter(max_calls=15)` → VTS 한도 초과
- 수정: `is_production=False` 시 `max_calls=3` 적용

---

## 2. 수정 파일 목록

| 파일 | 수정 내용 |
|------|----------|
| `/root/webapp/backend/data_miner.py` | TR_ID 수정, FID_INPUT_DATE_1 추가, `_get_headers` 분기 |
| `/root/webapp/backend/app/services/strategy/dynamic_stock_scanner.py` | decrypt_value 추가, is_production 우선 선택 |
| `/root/webapp/backend/app/services/kis/improved_client.py` | VTS rate limit 3/초, get_current_price retry 명시값 제거 |
| `/root/webapp/backend/realtime_signal_generator_fixed.py` | datetime 문법 수정, VTS skip 로직, use_fallback 분기 |

---

## 3. 검증 결과

### rank API (실계좌 74032243)
```
FHPST01710000 + FID_INPUT_DATE_1="" → 200 OK → 30개 종목 반환 ✅
```

### get_candidate_stocks
```
실KIS rank API → 50개 후보 종목 반환 ✅ (기존: fallback 88개)
```

### 신호 생성기 전체 실행 (16:47 KST)
```
VTS 사용자 (moong123, dlrud7466, moongoby@gmail): 즉시 스킵 ✅
실계좌 사용자 (moongmimi, moongoby@naver): 50종목 스캔 ✅
신호 생성: 2개 (moongoby@naver.com, 실계좌)
  - 136545: 252710 TIGER 200선물인버스2X BUY
  - 136546: 251340 KODEX 코스닥150선물인버스 BUY
```

---

## 4. 내일 아침 검증 항목

- [ ] 09:00~09:10 신호 생성 정상 완료 (240s 이내)
- [ ] 실계좌 50개 후보 종목에서 신호 발생
- [ ] auto_trade 스크립트 신호 픽업 → 잔액 확인 → 주문 시도
- [ ] trading_signals 신규 삽입 확인
- [ ] autotrade_positions 신규 체결 확인 (매매 활성화 시)

---

## 5. 잔여 과제

1. **실KIS EGW00201 rate limit**: 동시 사용자 처리 시 발생 → 사용자 간 딜레이 추가 필요
2. **search-stock-info VTS 에러**: risk_filter가 VTS 호출 → 실KIS 계정으로 변경 필요  
3. **DRY_RUN 전환**: 실매매 활성화는 대표님 승인 후 적용
