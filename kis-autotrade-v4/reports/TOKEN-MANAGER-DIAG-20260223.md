# TOKEN-MANAGER 진단 보고서

**작업일:** 2026-02-23  
**대상:** KIS + 키움 통합 토큰 매니저 (읽기 전용 진단)  

---

## 1. 파일 위치 및 구조

- **경로:** `backend/app/core/token_manager.py` (작업지시서의 `backend/app/services/auth/token_manager.py` 아님)
- **라인 수:** 367줄

### 클래스/함수 목록

| 라인 | 정의 |
|------|------|
| 57 | class TokenManager |
| 61 | async def get_token(broker, account_id, credentials) |
| 104 | async def _get_cached_token(broker, account_id) |
| 116 | async def _is_token_valid(token_data) |
| 126 | async def _needs_renewal(token_data) |
| 134 | async def _acquire_reissue_lock(broker, account_id, key_index=None) |
| 146 | async def _issue_token_kis(account_id, credentials) |
| 192 | async def _issue_token_kiwoom(account_id, credentials) |
| 238 | async def _save_token(broker, account_id, token_data) |
| 246 | async def revoke_token(broker, account_id, credentials=None, key_index=None) |
| 278 | def get_token_manager(redis_client=None) |
| 289 | def get_kis_token_sync(...) (동기 경로) |

---

## 2. 토큰 발급/갱신/캐시 흐름

1. **get_token**  
   - Redis에서 `_get_cached_token` → 있으면 `_is_token_valid` (만료 1시간 이상 남음) → 유효하면 그대로 반환.  
   - 만료 1시간 미만이면 `_needs_renewal` True → `_acquire_reissue_lock`(1분 락) → KIS/키움 발급 → `_save_token` (TTL 23시간).  
   - 캐시 없으면 바로 발급 후 저장.

2. **KIS 발급**  
   - `_issue_token_kis`: POST `{base_url}/oauth2/tokenP`, grant_type/client_credentials, appkey/appsecret.  
   - 반환: access_token, expires_at(Asia/Seoul 파싱), issued_at.

3. **키움 발급**  
   - `_issue_token_kiwoom`: POST `{base_url}/oauth2/token`, appkey/secretkey.  
   - 반환: token, expires_at, issued_at.

4. **상수**  
   - RENEW_BEFORE_EXPIRY = 1시간, REISSUE_LOCK_TTL = 60초, TOKEN_REDIS_TTL = 23*3600.

---

## 3. revoke_token 분석

- **위치:** 246~269행.  
- **동작:**  
  - `_redis_key_token(broker, account_id, key_index)` 로 Redis 키 결정. KIS는 key_index 미사용(None).  
  - 해당 키에서 raw 조회 → json 파싱 → `token` 또는 `access_token` 추출.  
  - **항상** `await self.redis.delete(key)` 실행 (Redis 삭제).  
  - broker == "kiwoom" 이고 credentials 있으면 revoke API POST 호출; KIS는 revoke API 없음.  
- **결론:** Redis 삭제 후 키움만 revoke API 호출. “line 253” 특정 버그는 현재 코드에서 재현되지 않음. (과거에 key_index 미전달로 키움 멀티키 시 잘못된 키 삭제 가능성은 CUR-TOKEN-MANAGER-FIX로 key_index 전달하도록 정리된 상태.)

---

## 4. 실계좌/모의계좌 분기 로직

- **token_manager 자체:** 실/모의 구분 없음. `credentials`(base_url, app_key, app_secret 등)만 사용.  
- **호출처:**  
  - `kis_order_service._get_token()`: `_get_kis_config(user_id, prefer_production)`으로 kis_configs에서 config 선택.  
  - `prefer_production` = True면 실전(is_production=True) config, False면 모의.  
  - base_url: 실전 `https://openapi.koreainvestment.com:9443`, 모의 `https://openapivts.koreainvestment.com:29443`.  
  - account_id = `f"kis:{config['id']}"` → Redis 키 `token:kis:kis:4` 형태.

---

## 5. Redis 키 / TTL

- **키 패턴:**  
  - KIS: `token:kis:{account_id}` (account_id 예: "kis:4").  
  - 키움: `token:kiwoom:{account_id}` 또는 멀티키 `token:kiwoom:{key_index}:{account_id}`.  
  - 락: `token_lock:kis:{account_id}` 등, TTL 60초.  
- **확인 결과 (2026-02-23):**  
  - `KEYS "token:*"` → `token:kis:kis:4` 존재.  
  - `TTL "token:kis:*"` → -2 (키 없음/만료). 정확한 키 `token:kis:kis:4`에 대해 TTL 확인 시 만료 시 -2.

---

## 6. 호출 관계

| 호출처 | 용도 |
|--------|------|
| kis_order_service | get_token_manager().get_token("kis", account_id, credentials) — 주문 시 토큰 |
| broker_kiwoom_client | get_token_manager().get_token("kiwoom", ...) |
| KISAPIClient (data_pipeline) | get_kis_token_sync() — 동기 경로 (수집 등) |
| (직접 revoke 호출) | API/관리 기능에서 계좌 비활성화 시 |

오케스트레이터/order_executor는 kis_order_service 경유로 토큰 사용. bridge는 executor/서비스 레이어 통해 간접 사용.

---

## 7. 권고 사항 (수정 시 검수 필수)

1. **토큰 저장 실패 시 재시도/로깅:** `_save_token` 실패 시 현재 warning만 로그; 필요 시 재시도 또는 상위에서 예외 전파 검토.  
2. **revoke_token 호출처 정리:** revoke_token을 호출하는 API/스크립트 목록 문서화 및 키움 revoke 실패 시 알림 여부 검토.  
3. **Redis TTL과 KIS 만료 시간 정합성:** Redis TTL 23시간 vs KIS 24시간이면 1시간 차이; 만료 직전 갱신 정책과 일치하는지 확인.  
4. **account_id 규칙:** 현재 "kis:4" 형태로 config_id 사용; 다중 실전/모의 계좌 확장 시 키 충돌 없도록 규칙 유지.

---

**진단 완료.** 서비스 재시작 및 .env 수정 없음.
