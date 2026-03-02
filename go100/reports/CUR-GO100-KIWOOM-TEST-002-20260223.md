# CUR-GO100-KIWOOM-TEST-002 결과 보고서

**일시:** 2026-02-23 (월) 15:15 KST  
**서버:** root@[SERVER-IP] (SSH)  
**목적:** 키움증권 모의계좌(account_id=4, 81201280) API 인증 + 잔고조회 + 매수/매도 테스트  
**선행:** CUR-GO100-KIWOOM-TEST-001 완료 (DB enc_app_key/enc_app_secret 존재 확인)

---

## STEP 1. .env 암호화 키 확인

| 항목 | 결과 |
|------|------|
| **ENCRYPTION_KEY** | 존재 (라인 55, 32자 이상 Fernet 유효) |
| **SECRET_KEY** | 존재 (라인 13) |
| **FERNET_KEY** | 미설정 (폴백으로 ENCRYPTION_KEY 사용) |
| **CRYPTO_KEY** | .env 내 미사용 |

**CryptoService 소스:** `backend/app/core/crypto.py`  
- 키 로드 순서: `ENCRYPTION_KEY` → `FERNET_KEY` → `SECRET_KEY` (폴백 시 SECRET_KEY SHA256 해시)  
- `encrypt()` / `decrypt()` / `decrypt_or_passthrough()` 제공, Fernet 기반

---

## STEP 2. verify_kiwoom_account 스크립트 확인

| 항목 | 결과 |
|------|------|
| **스크립트** | `backend/scripts/verify_kiwoom_account.py` 존재 |
| **검증 함수** | `account_service.verify_account_api_key(account_id, user_id, db)` (라인 303) |
| **동작** | DB에서 enc_app_key/enc_app_secret 복호화 → KiwoomBrokerClient 생성 → authenticate() → get_balance(account_number) |

`verify_account_api_key`는 broker_type=KIWOOM일 때 `KiwoomBrokerClient`로 토큰 발급 및 잔고 조회까지 수행함.

---

## STEP 3~6. 키움 API 접근토큰 / 잔고 / 매수·매도 테스트

**실행 명령:**
```bash
cd /root/kis-autotrade-v4 && source venv/bin/activate
PYTHONPATH=/root/kis-autotrade-v4 python /tmp/kiwoom_test.py
```

**테스트 스크립트:** `/tmp/kiwoom_test.py` (CUR-GO100-KIWOOM-TEST-002용으로 생성, `OrderRequest` 사용해 buy/sell 호출)

### 실행 결과 요약

| STEP | 내용 | 결과 |
|------|------|------|
| **STEP 3** | 접근토큰 발급 | **성공**으로 처리되었으나 **token 값이 빈 문자열** |
| **STEP 4** | 잔고 조회 | **실패** — `httpx.LocalProtocolError: Illegal header value b'Bearer '` |
| **STEP 5** | 매수 테스트 (005930 1주 시장가) | STEP 4 실패로 미수행 |
| **STEP 6** | 매도 테스트 | STEP 5 미수행으로 스킵 |

### 상세 로그 (요약)

- 계좌: id=4, number=81201280, is_mock=True  
- enc_app_key/enc_app_secret 길이 140, **복호화 성공** (app_key=[KIWOOM-APP-KEY-PREFIX]..., secret_key=[KIWOOM-SECRET-PREFIX]...)  
- STEP 3: `BrokerToken(token='', token_type='bearer', ...)` — **토큰 문자열이 비어 있음**  
- STEP 4: `Authorization: Bearer ` (빈 토큰) 전송으로 HTTP 헤더 규격 위반 발생

### 원인 분석

- `KiwoomBrokerClient.authenticate()`는 `token_manager.get_token("kiwoom", account_id, credentials)`를 우선 사용.
- token_manager가 **Redis 캐시**에서 기존 데이터를 반환한 경우, 과거에 빈 토큰이 캐시되었거나 **모의 API**가 200 OK이면서 `token`/`access_token`을 비워 둔 응답을 준 경우, `token_data.get("token") or token_data.get("access_token")`이 `""`가 됨.
- 이 경우에도 예외가 발생하지 않아 `BrokerToken(token="", ...)`가 반환되고, 이후 잔고/매수/매도 요청에서 `Bearer ` 만 전송되어 `Illegal header value b'Bearer '` 발생.

---

## 권장 조치

1. **token_manager 빈 토큰 처리**  
   - `get_token()` 반환값에서 `token`/`access_token`이 비어 있으면 **유효한 토큰으로 간주하지 않고** 재발급 경로로 진행하거나,  
   - `KiwoomBrokerClient.authenticate()`에서 token_manager 반환값의 token이 비어 있으면 **즉시 direct auth(직접 POST /oauth2/token) fallback** 하도록 수정 권장.
2. **Redis 캐시 초기화**  
   - 키움 모의 계정용 Redis 토큰 키(예: kiwoom:default) 삭제 후 스크립트 재실행하여 **신규 발급**만 사용하도록 확인.
3. **모의 API 응답 확인**  
   - `https://mockapi.kiwoom.com/oauth2/token` 응답 본문에 `token` 또는 `access_token` 필드가 실제로 채워지는지 확인.

---

## 동기화 체크리스트

- [x] STEP 1~2 결과 확인
- [x] /tmp/kiwoom_test.py 실행 → STEP 3~6 결과 확인
- [x] 보고서 작성: `/root/project-docs/go100/reports/CUR-GO100-KIWOOM-TEST-002-20260223.md`
- [ ] git commit + push (project-docs)
- [ ] 코드 변경 시 kis-autotrade-v4 repo 커밋 + push (본 테스트에서는 스크립트만 생성, 코드 변경 없음)

---

## 참고

- **절대규칙 준수:** kis-v41-* 서비스 재시작 없음, strategy_cards ALTER/DROP/DELETE 없음, .env/.bak 커밋 없음.
- **Git:** 코드 repo `kis-autotrade-v4` (branch: phase-2c-command-center), 문서 repo `project-docs` (branch: master).
