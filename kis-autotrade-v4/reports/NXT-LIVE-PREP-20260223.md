# NXT LIVE TRADE TEST 사전 준비 보고서

**작업일:** 2026-02-23  
**실행 예정:** 2026-02-24 (월) NXT 프리마켓 08:00 이후  
**본 문서:** 사전 준비만 수행 (실행 없음)  

---

## 1. .env 실계좌 관련 변수 존재 확인 (읽기만)

- **확인 결과:** 아래 변수명이 .env 및 .env.example에 존재함. (값은 읽지 않음, 수정 금지.)
  - KIS_REAL_APP_KEY
  - KIS_REAL_APP_SECRET
  - KIS_REAL_ACCOUNT_NUMBER
  - KIS_REAL_ACCOUNT_PRODUCT_CODE
  - KIS_REAL_RATE_LIMIT (일부 백업에만 있음)
- **참고:** 실전 주문 시 kis_configs 테이블의 실전 계좌(config_id=4 등) 사용. .env의 KIS_REAL_* 는 레거시/스크립트용일 수 있음.

---

## 2. KIS API 실전 도메인 접속 가능 여부

- **실전 base_url:** `https://openapi.koreainvestment.com:9443`
- **확인 방법:** `curl -s -o /dev/null -w "%{http_code}" https://openapi.koreainvestment.com:9443/oauth2/tokenP` 또는 health 엔드포인트 (실제 구현에 따라).
- **비고:** 실행일(2/24) 장전에 실제 curl/health 한 번 더 수행 권장. (본일은 사전 준비만.)

---

## 3. token_manager 실계좌 토큰 발급 경로

- **파일:** `backend/app/core/token_manager.py`
- **실계좌 경로:**  
  - `kis_order_service._get_token()` → `_get_kis_config(user_id, prefer_production=True)` → kis_configs에서 is_production=True 인 계좌 선택.  
  - base_url = `https://openapi.koreainvestment.com:9443`  
  - credentials = app_key, app_secret, base_url (kis_configs 암복호화 값).  
  - `get_token_manager().get_token("kis", account_id, credentials)` → Redis 키 `token:kis:kis:{config_id}`.  
- **결론:** 실계좌는 kis_configs의 실전 행 + 위 base_url로 토큰 발급 가능. NXT 주문 시 동일 토큰/클라이언트 사용.

---

## 4. NXT 주문 코드 (거래소구분 NX) 파라미터 확인

- **OrderRequest (broker_base.py):**  
  - `exchange: str = "KRX"` — "KRX" | "NXT" | "SOR" 지원.
- **키움 클라이언트 (broker_kiwoom_client.py):**  
  - `EXCHANGE_MAP = {"KRX": ("KRX", ""), "NXT": ("NXT", "_NX"), "SOR": ("SOR", "_AL")}`  
  - NXT 시: dmst_stex_tp = "NXT", 종목코드 접미사 "_NX" (stk_cd = stock_code + "_NX").  
- **KIS 주문:**  
  - KIS 본체 주문 API에서 거래소/종목 구분 파라미터가 있다면 NXT용으로 동일한 개념 적용 필요.  
  - kis_api_registry에 NXT 실시간/호가/체결통보 등 6종 등록됨.
- **실행 시 권장:**  
  - NXT 1주 매수·즉시 매도 테스트 시 OrderRequest.exchange = "NXT" 로 전달.  
  - 사용 브로커가 KIS이면 KIS API 스펙상 NXT 구분 필드(dmst_stex_tp 등) 확인 후 호출.

---

## 5. 사전 준비 체크리스트

| 항목 | 상태 |
|------|------|
| .env 실계좌 변수 존재 | 확인됨 (읽기만) |
| token_manager 실계좌 경로 | kis_configs + openapi.koreainvestment.com:9443 |
| NXT exchange 파라미터 | OrderRequest.exchange = "NXT", 키움 시 _NX 접미사 |
| KIS API 실전 도메인 | 2/24 장전 curl/health 재확인 권장 |
| 실행 | 2/24 08:00 이후 수행 예정 |

---

## 6. 불변 확인

- strategy_cards: 변경 없음 (65건 유지).  
- v4_positions OPEN: 5건 유지.  
- 서비스 재시작: 없음.  
- DB 변경: 없음.  
- .env 수정: 없음.

---

**사전 준비 완료.** 실제 NXT 매매 실행은 2026-02-24 NXT 프리마켓 08:00 이후 진행.
