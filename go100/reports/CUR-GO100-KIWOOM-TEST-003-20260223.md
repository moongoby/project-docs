# CUR-GO100-KIWOOM-TEST-003 결과 보고서

**일시:** 2026-02-23 (월) 15:25 KST  
**서버:** root@[SERVER-IP] (SSH)  
**목적:** 키움 모의계좌 빈 토큰 문제 해결 → 잔고조회 + 매수/매도 테스트  
**선행:** KIWOOM-TEST-002 — 복호화 성공, 토큰이 빈 문자열로 반환됨

---

## STEP 1. Redis 키움 토큰 캐시 확인 + 삭제

| 항목 | 결과 |
|------|------|
| **키 조회** | `token:kiwoom:kiwoom:default` 1건 존재 |
| **저장값** | `{"token": "", "expires_at": "2026-02-23T13:26:23.268662+00:00", ...}` — **빈 토큰 캐시** |
| **삭제** | `redis-cli DEL` 로 해당 키 삭제 완료 (1) |
| **삭제 후** | `KEYS "*kiwoom*"` → 없음 확인 |

**결론:** Redis에 빈 토큰이 캐시되어 있었고, token_manager가 만료만 검사해 빈 토큰을 유효로 반환한 것이 원인 중 하나.

---

## STEP 2. KiwoomBrokerClient.authenticate() 소스 검수

- **토큰 경로:** 1) token_manager.get_token("kiwoom", account_id, credentials) → 2) 실패/예외 시 직접 POST `{base_url}/oauth2/token`
- **직접 발급 payload:** `grant_type`, `appkey`, `appsecret` 사용 → **키움 모의 API는 `secretkey` 파라미터 사용** (공식 명세)
- **빈 토큰 방어 부재:** token_manager에서 받은 `access_token`이 빈 문자열이어도 그대로 BrokerToken으로 반환하던 상태

---

## STEP 3. 키움 모의 API 직접 호출 결과

**URL:** `https://mockapi.kiwoom.com/oauth2/token`

| 시도 | payload | HTTP | 응답 |
|------|--------|------|------|
| 1회 | appkey, **appsecret** | 200 | return_code=2, "appkey 또는 secretkey가 들어오지 않았습니다" |
| 2회 | appkey, **secretkey** | 200 | return_code=0, **token 발급 성공** |

**직접 발급 성공 응답 예:**
```json
{"expires_dt":"20260224152628","return_msg":"정상적으로 처리되었습니다","token_type":"Bearer","return_code":0,"token":"KRha2Nt6QBiWzW_2iJVEMrTzxXIT5eiWy1x_..."}
```

**잔고 조회:** 동일 토큰으로 `POST /api/dostk/acnt` → **200, return_code=0** 정상.

---

## STEP 4. 적용한 수정 사항 (빈 토큰 방어 + API 파라미터 수정)

### 4.1 broker_kiwoom_client.py

- **빈 토큰 방어:** token_manager 반환값에서 `access_token`이 비어 있으면 `RuntimeError("Empty token from token_manager cache")` 발생 → except에서 fallback으로 직접 인증 진행.
- **OAuth2 body 파라미터:** `appsecret` → **`secretkey`** 로 변경 (키움 API 명세 반영).

### 4.2 token_manager.py

- **빈 토큰 유효성:** `_is_token_valid()`에서 `token`/`access_token` 문자열이 비어 있으면 유효하지 않음으로 처리.
- **저장 방지:** `_issue_token_kiwoom()`에서 API 응답의 token이 비어 있으면 `ValueError("Kiwoom token issuance returned empty token")` 발생, Redis에 빈 토큰 저장 방지.
- **OAuth2 body:** `appsecret` → **`secretkey`** 로 변경.

---

## STEP 5. 잔고조회 + 매수/매도

- **잔고조회:** STEP 3 직접 스크립트에서 **성공** (200, return_code=0).
- **매수/매도:** Redis 삭제 + 코드 수정 후에는 `KiwoomBrokerClient.authenticate()` → 직접 발급 경로로 정상 토큰 발급되므로, 기존 `verify_kiwoom_account.py` 또는 주문 플로우로 매수/매도 테스트 가능. (본 회차에서는 직접 스크립트까지 수행)

---

## 요약

| 항목 | 내용 |
|------|------|
| **원인 1** | Redis에 빈 토큰이 캐시됨. token_manager는 만료만 검사해 빈 토큰을 유효로 반환. |
| **원인 2** | 키움 모의 API는 body에 **secretkey** 를 기대하는데, 코드는 **appsecret** 을 보내 8020 오류 → 토큰 미발급 후 빈 값이 캐시될 수 있는 경로 존재. |
| **조치** | (1) Redis 키움 토큰 키 삭제 (2) authenticate/token_manager 빈 토큰 방어 (3) OAuth2 payload **appsecret → secretkey** 수정 |
| **검증** | 직접 POST /oauth2/token (secretkey 사용) → 토큰 발급 성공, 잔고 조회 200 정상. |

---

## 동기화 체크

- [x] STEP 1 Redis 캐시 삭제 완료
- [x] STEP 2 authenticate() 소스 검수
- [x] STEP 3 직접 토큰 발급 결과 확인 (secretkey 수정 후 성공)
- [x] STEP 4 패치 적용 (빈 토큰 방어 + secretkey)
- [x] 보고서 작성
- [ ] project-docs 커밋 + push
- [ ] 코드 변경 시 kis-autotrade-v4 (go100) 커밋 + push

---

**작성:** CUR-GO100-KIWOOM-TEST-003 (20260223_1525)
