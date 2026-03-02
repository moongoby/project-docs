# TOKEN-MANAGER-FIX 진단 보고서 (읽기전용)

**작업 ID**: TOKEN-MANAGER-FIX  
**일시**: 2026-02-23  
**서버**: root@[SERVER-IP]  
**프로젝트**: /root/kis-autotrade-v4  
**브랜치**: phase-2c-command-center  
**범위**: 진단만 (코드/DB/서비스/.env 변경 없음)

---

## 1. token_manager.py 구조 요약

| 항목 | 값 |
|------|-----|
| 경로 | `backend/app/core/token_manager.py` |
| 총 라인 수 | 366 |
| RENEW_BEFORE_EXPIRY | 1시간 (timedelta(hours=1)) |
| REISSUE_LOCK_TTL | 60초 |
| TOKEN_REDIS_TTL | 23시간 |

---

## 2. 토큰 발급 경로 분석

| 호출 경로 | 함수/모듈 | 인증키 소스 | config_id 전달 | token_manager 사용 |
|-----------|-----------|----------------------|----------------|---------------------|
| 파이프라인 주문 | V4OrderExecutor | kis_configs (DB) | ✅ config_id로 조회 | ❌ (_get_mock_token 직접 tokenP) |
| kis_order_service | _get_token() | kis_configs (DB) | ✅ account_id=`kis:{config_id}` | ✅ get_token_manager().get_token("kis", ...) |
| 잔고/사전검사 | AccountSyncManager | kis_configs (DB) | ✅ config_id | ❌ (_get_token_sync 직접 tokenP+DB) |
| 데이터 수집 | kis_api_client.get_token() | kis_configs (DB) | ✅ account_id=`kis:{config_id}` | ✅ get_kis_token_sync() (동기) |
| 포지션 모니터 | position_monitor._get_token_for_config_id | kis_configs (DB) | ✅ config_id | ❌ (직접 tokenP+DB) |

- **token_manager.py 내부**: 인증키/시크릿은 항상 **caller가 넘긴 credentials dict**에서만 사용. `os.getenv`로 KIS 키를 읽는 코드 없음.
- **결론**: KIS 토큰 발급의 단일 진실 공급원은 **kis_configs (DB)**. .env의 KIS 인증키는 이 경로에서 사용되지 않음.

---

## 3. .env vs DB 키 불일치 여부

- **KIS**: 모든 진입 경로가 kis_configs에서 인증키/시크릿 조회 후 token_manager 또는 직접 tokenP 호출. **.env와 DB 불일치 가능성 없음** (KIS는 .env 미사용).
- **키움**: broker_kiwoom_client / BrokerFactory 등에서 .env 키 사용 가능. 키움 멀티키는 DB(accounts 암호화 컬럼) 사용. 본 진단은 KIS 토큰 매니저 중심이므로 키움 .env vs DB는 생략.

---

## 4. revoke_token 버그 확인 (line 253 key_index)

**확인 구간**: `token_manager.py` 245~260행.

- `revoke_token(self, broker, account_id, credentials=None, key_index=None)` 에서 **key_index는 시그니처에 정의됨** (Optional[int] = None).
- 255행: `key = _redis_key_token(broker, account_id, key_index)` 로 전달됨.
- `_redis_key_token`: broker가 "kiwoom"이고 key_index가 not None일 때만 `token:kiwoom:{key_index}:{account_id}` 사용, 그 외에는 `token:{broker}:{account_id}`.
- **결론**: **현행 코드에는 key_index 미정의 버그 없음.** KIS 경로는 key_index=None으로 호출되며, Redis 키는 `token:kis:{account_id}`로 정상 생성됨.

---

## 5. 만료 1시간 전 갱신 구현 확인

- **RENEW_BEFORE_EXPIRY**: 26행 `timedelta(hours=1)` 정의.
- **_is_token_valid**: 115~123행. `now + RENEW_BEFORE_EXPIRY <= exp` 이면 유효. 즉 만료 1시간 이상 남았을 때만 재사용.
- **_needs_renewal**: 125~131행. `now + RENEW_BEFORE_EXPIRY > exp` 이면 갱신 필요.
- **get_token 흐름**: 74~100행. 캐시 조회 → 유효하면 반환 → 만료 임박 시 락 획득 후 재발급 시도 → 실패 시 1초 sleep 후 캐시 재조회.
- **결론**: **만료 1시간 전 선제 갱신 로직 구현됨.** (규칙서 79~94행 참고와 일치)

---

## 6. Redis 토큰 캐시 상태

| 키 패턴 | 조회 결과 (2026-02-23) |
|---------|------------------------|
| token:kis:* | `token:kis:kis:4` 1건 |
| token:kis:1 | 없음 (TTL -2) |
| token:kis:kis:4 TTL | 79,241초 (약 22시간) |
| token:kiwoom:* | (조회 시 0건 표시) |
| token_lock:* | (별도 미집계) |

- config_id=4(실전) 계정에 대해서만 Redis KIS 토큰 캐시 존재. config_id=1, 3 등은 해당 시점에 캐시 없거나 만료된 상태로 보임.

---

## 7. 수정 제안 (내일 적용용)

1. **이중 경로 통일 (선택)**  
   - V4OrderExecutor._get_mock_token, AccountSyncManager._get_token_sync, position_monitor._get_token_for_config_id 는 **token_manager + Redis** 를 쓰지 않고 DB+직접 tokenP 사용.  
   - 향후 정리 시: 동일 config_id에 대해 **token_manager + Redis** 단일 경로로 통일하면 캐시 재사용·1시간 전 갱신 정책이 일관 적용됨.

2. **실패 시 단계별 재시도 (규칙서 미구현)**  
   - 규칙서: 1회 실패 60초, 2회 120초, 3회 초과 시 degraded.  
   - 현행 token_manager: 재발급 실패 시 1초 sleep 후 캐시 재조회만 있음.  
   - 제안: 60/120초 단계별 대기 및 3회 초과 시 로그 경고·degraded 플래그 등 정책 반영 검토.

3. **revoke_token**  
   - 현재 구현으로 key_index 버그 없음. 변경 불필요.

---

## 8. DB 무결성 (참고)

- 본 작업은 **읽기전용 진단**이라 DB 변경·직접 조회는 수행하지 않음.
- 기준값 (CONTEXT.md·규칙서 기준): strategy_cards 62건, v4_positions OPEN 5건 유지 권장.  
  적용 시점에 `SELECT count(*) FROM strategy_cards;`, `SELECT count(*) FROM v4_positions WHERE status = 'OPEN';` 등으로 사전 확인 권장.

---

## 9. 체크리스트

- [x] 토큰 발급 경로 분석 완료
- [x] .env vs DB 키 비교 완료 (KIS: DB 단일 소스)
- [x] revoke_token 버그 확인 (key_index 정의·전달 정상)
- [x] 만료 1시간 전 갱신 로직 확인
- [x] Redis 캐시 상태 확인
- [x] 수정 제안 작성
- [ ] 보고서 발행 + Git 동기화 (다음 단계)
- [x] 코드/DB/서비스 변경 없음 확인
