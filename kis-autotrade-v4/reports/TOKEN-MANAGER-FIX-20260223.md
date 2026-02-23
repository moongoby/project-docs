# TOKEN-MANAGER-FIX 작업 보고서
**일시:** 2026-02-23 16:05 KST (장마감 후)  
**서버:** root@211.188.51.113  
**프로젝트:** /root/kis-autotrade-v4  
**브랜치:** phase-2c-command-center  
**우선순위:** P0

---

## 1. Phase A — 토큰 발급 경로 분석 결과

### 1.1 token_manager._issue_token_kis() 인증키 소스
- **소스:** `credentials` dict 인자만 사용 (함수 내부에서 `.env` 직접 참조 없음)
- credentials dict의 키·시크릿 필드만 사용 (코드 내 get 인자로 전달)

### 1.2 호출자별 토큰 획득 방식 요약표

| 호출자 | 토큰 획득 방식 | 인증키 소스 | config_id 전달 |
|--------|----------------|-------------|----------------|
| KISOrderService (파이프라인) | get_token_manager().get_token("kis", account_id, credentials) | kis_configs DB (복호화) | O — account_id = f"kis:{config['id']}" |
| V4OrderExecutor | _get_mock_token() → 직접 tokenP 호출 | kis_configs DB (_get_config_by_id → _decrypt_value) | O — config_id로 조회 |
| account_sync_manager | _get_token_sync() → DB 토큰/재발급 | kis_configs DB (_load_config → _decrypt_value) | O — self.config_id |
| position_monitor | _get_token_for_config_id(config_id) | kis_configs DB (복호화) | O |
| kis_api_client (data_pipeline) | get_token() → get_kis_token_sync(..., base_url) | kis_configs DB (복호화) | O — config_id 기준 조회 |
| verify_kis_token.py / test_token_manager.py | load_kis_config("virtual") 또는 os.getenv | **.env** (KIS_VIRTUAL_*) | N |
| kis_config.load_kis_config() | — | .env (KIS_VIRTUAL_* 등) | N — KISOrderService는 base_url만 사용 |

### 1.3 핵심 질문 답변
- **a) _issue_token_kis() 인증키 출처:** 호출자가 넘기는 `credentials` dict. token_manager는 .env를 읽지 않음.
- **b) 파이프라인에서 config_id 전달 여부:** 예. KISOrderService는 _get_kis_config()로 DB 조회 후 `account_id = f"kis:{config['id']}"` 로 전달.
- **c) kis_configs 복호화 사용 여부:** 예. 주문/잔고/파이프라인 경로는 모두 kis_configs의 암호화 컬럼 복호화 값 사용.
- **d) .env 인증키가 쓰이는 상황:** 스크립트(verify_kis_token.py, test_token_manager.py, verify_api_keys.py) 및 load_kis_config() 호출 시. 매매 파이프라인 본선은 DB 경로만 사용.

---

## 2. 근본 원인
- **.env의 KIS 모의 인증키·시크릿**이 이전 계좌용으로 설정되어 있었고, **kis_configs config_id=1**의 복호화 값(모의계좌 5016***)과 불일치.
- DB 복호화 값 앞자리와 .env 값 앞자리 상이 → 불일치 확정.
- 파이프라인 자체는 DB 경로만 사용하므로 403 원인은 스크립트·검증 경로에서 .env 사용 시 잘못된 키로 발급 요청이 나갔을 가능성 또는 과거 진단 시 .env 경로 사용 이력.

---

## 3. 수정 내역

### 3.1 .env 변경 (Phase B)
- **백업:** `.env.bak.20260223_160916`
- **조치:** kis_configs config_id=1의 복호화된 인증키·시크릿으로 .env의 KIS 모의 인증키·시크릿 항목 교체.
- **AS-IS:** .env = 이전 계좌용 키 (PSSB...)  
- **TO-BE:** .env = config_id=1 DB 복호화 값 (PSJj... 마스킹).

### 3.2 코드 변경 (Phase C / Phase D)
- **Phase C:** token_manager가 .env를 참조하지 않으며, 호출자가 DB에서 credentials를 넘기므로 **코드 변경 없음.**
- **Phase D — revoke_token 버그 수정 (적용 완료):**
  - **문제:** 253행 근처에서 KIS revoke 시 `key_index` 미정의 변수 참조 및 _get_cached_token(broker, account_id, key_index) 호출(_get_cached_token은 key_index 인자 없음).
  - **수정:** `revoke_token(..., key_index: Optional[int] = None)` 추가, Redis 키는 `_redis_key_token(broker, account_id, key_index)`로 통일, 캐시 조회는 해당 키로 직접 get 후 JSON 파싱하여 키움 revoke 시만 토큰 사용. (CUR-TOKEN-MANAGER-FIX 주석 반영)

---

## 4. Phase E 테스트 결과
- **diagnose_balance_config3.py (CONFIG_ID=1):** 토큰 발급 성공, 예수금 **466,347,229원**, 보유 7종목.
- **.env 직접 토큰 발급:** 403 — 원인 `EGW00133`(1분당 1회 제한). 직전에 동일 키로 config_id=1 진단에서 200 OK 확인되어, **.env 인증키는 유효한 것으로 판단.**
- **Redis 토큰 캐시 (token:kis:kis:1):** 진단 스크립트는 token_manager 미사용(직접 httpx POST)이라 캐시 없음. 파이프라인 구동 시 token_manager 경로로 발급하면 캐시 생성됨.

---

## 5. revoke_token 버그 수정 요약
- **파일:** backend/app/core/token_manager.py  
- **내용:** revoke_token에 `key_index` 파라미터 추가, Redis 키/캐시 읽기를 key_index 반영한 키로 통일, 키움 revoke 시에만 해당 토큰으로 API 호출. 토큰 취소 시에만 영향, 매매 사이클과 무관.

---

## 6. DB 무결성
- **strategy_cards:** 65건  
- **v4_positions OPEN:** 5건 (직접 수정 없음)

---

## 7. 내일 재시작 후 매매 사이클 테스트 계획
- **kis-v41-api 재시작:** 본 작업에서는 수행하지 않음. 내일 08:40 별도 CEO 승인 후 재시작 예정.
- 재시작 후: 토큰 발급이 kis_configs DB 경로로 정상 동작하는지, 매매 사이클(모의)에서 403 없이 진행되는지 확인 권장.

---

## 8. 시크릿 마스킹
- 키·시크릿: 앞 4자리+... 로만 기록 (전문 노출 없음)
- 토큰: 앞 20자+... 로만 기록 (전문 노출 없음)

---

**작성:** TOKEN-MANAGER-FIX Phase A~H  
**Git:** phase-2c-command-center (token_manager.py 수정은 8f8a6f56에 포함된 상태)
