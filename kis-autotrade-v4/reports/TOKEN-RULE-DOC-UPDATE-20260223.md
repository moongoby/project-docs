# TOKEN-RULE-DOC-UPDATE 보고서 (2026-02-23)

## 작업 개요
- **작업 ID**: TOKEN-RULE-DOC-UPDATE
- **일시**: 2026-02-23 15:50 KST
- **서버**: root@211.188.51.113
- **프로젝트**: /root/kis-autotrade-v4
- **브랜치**: phase-2c-command-center
- **목적**: KIS API 토큰 관리 규칙 문서화 + 서버 코드 읽기 전용 검증 (코드/DB/서비스 변경 없음)

---

## Phase A — 토큰 코드 검증 결과

### 검증 대상 파일
- **핵심**: `backend/app/core/token_manager.py`
- **참조**: `backend/app/core/kis_api_registry.py`, `backend/app/services/data_pipeline/kis_api_client.py`, `backend/app/core/broker_kis_adapter.py`

### 5항목 검증 표

| 항목 | 구현 여부 | 파일:라인 | 구현 방식 |
|------|----------|-----------|-----------|
| 토큰 캐시 | Y | token_manager.py:31-34, 103-114, 238-244 | Redis 키 `token:kis:{account_id}`에 JSON 저장 (access_token, expires_at, issued_at), TTL 23시간 |
| 만료 1시간 전 갱신 | Y | token_manager.py:26, 80, 115-131 | RENEW_BEFORE_EXPIRY=timedelta(hours=1), _needs_renewal()에서 now+RENEW_BEFORE_EXPIRY > exp 시 True, _is_token_valid()에서 now+RENEW_BEFORE_EXPIRY <= exp 시 유효 |
| 1분 재발급 간격 제한 | Y | token_manager.py:27-28, 132-142, 317-319 | REISSUE_LOCK_TTL=60, _acquire_reissue_lock()에서 SETNX ex=60, 동기 경로 get_kis_token_sync 동일 |
| config_id별 독립 관리 | Y | kis_api_client.py:76-77, token_manager.py:31-34 | account_id = f"kis:{config_id}", Redis 키별 독립 캐시 (config_id 1/3/5 각각 별도 키) |
| 실패 시 재시도/폴백 | N | — | 60초/120초 단계별 재시도 및 3회 초과 degraded 모드 미구현. 현행: 1초 sleep 후 캐시 재조회만 존재 |

### 만료 1시간 전 갱신 구현 확인 (코드 스니펫)

**파일**: `backend/app/core/token_manager.py`

```python
# 라인 26-28
RENEW_BEFORE_EXPIRY = timedelta(hours=1)  # 만료 1시간 전 재발급
REISSUE_LOCK_TTL = 60  # 재발급 락 1분
TOKEN_REDIS_TTL = 23 * 3600  # Redis TTL 23시간

# 라인 115-131
async def _is_token_valid(self, token_data: dict) -> bool:
    """만료 1시간 이상 남았고, 토큰 문자열이 비어 있지 않으면 True"""
    ...
    return datetime.now(timezone.utc) + RENEW_BEFORE_EXPIRY <= exp

async def _needs_renewal(self, token_data: dict) -> bool:
    """만료까지 1시간 미만이면 True"""
    ...
    return datetime.now(timezone.utc) + RENEW_BEFORE_EXPIRY > exp
```

`get_token()` 흐름: 캐시 조회 → 유효하면 반환 → _needs_renewal True면 락 획득 후 재발급 → 저장 후 반환.

---

## 추가된 규칙 전문

`kis-v41-rules.md`에 **"## 환경"** 바로 아래에 삽입된 섹션:

- **KIS API 토큰 관리 규칙 (CEO 지시, 2026-02-23)**
  - 공식 정책: 24시간 유효, 1일 1회 발급 원칙, 재발급 최소 간격 1분, 초당 20건 제한
  - V4.1 원칙: Redis 캐시 필수, 재사용 우선, 만료 1시간 전 선제 갱신, config_id별 독립, 실패 대응(60초/120초 재시도, 3회 초과 degraded), 재시작 시 Redis 토큰 재사용
  - 금지: 매 호출 재발급, 1분 이내 연속 발급, 토큰 평문 로깅, .env 토큰 하드코딩
  - 현행 구현 상태: token_manager.py, Redis 캐시, 만료 1시간 전 갱신 구현됨, 실패 시 단계별 재시도/폴백 미구현

---

## 코드 개선 필요 사항

1. **실패 시 재시도/폴백**: CEO 규칙상 "1회 실패 60초, 2회 120초, 3회 초과 시 degraded"가 문서화되어 있으나, `token_manager.py`에는 해당 로직이 없음. 추후 `_issue_token_kis` 실패 시 재시도 루프 및 3회 초과 시 로그 경고/기존 캐시 재사용 또는 degraded 플래그 반영 검토 권장.
2. **revoke_token 버그**: `token_manager.py` 253행에서 KIS 경로로 `revoke_token` 호출 시 `key_index`가 정의되지 않음 (키움 전용 파라미터). KIS일 때는 `key_index=None`으로 호출하거나 시그니처 정리 필요.

---

## DB 무결성

- **strategy_cards**: 65건 (검증 시점 조회값)
- **v4_positions OPEN**: 5건
- **코드/DB/서비스 변경**: 없음

---

## Phase 완료 체크

| Phase | 내용 | 상태 |
|-------|------|------|
| A | 토큰 코드 검증 (읽기 전용) | 완료 |
| B | kis-v41-rules.md 토큰 규칙 섹션 추가 | 완료 |
| C | project-docs 복사 + sync_kis.sh | 완료 (rules는 스크립트에서 민감정보로 SKIP) |
| D | kis-autotrade-v4 커밋 및 push | 완료 |
| E | 보고서 발행 | 진행 (publish_report.sh 실행 예정) |
