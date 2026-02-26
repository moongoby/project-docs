# CUR-GO100-PHASE4-A2-MULTITURN

## Phase 4 A-2 멀티턴 5턴 확대 보고서

**날짜**: 2026-02-26
**티켓**: CUR-GO100-PHASE4-A2-MULTITURN
**상태**: 완료

---

## 목표

- 최근 5턴(10메시지) 대화 히스토리 저장
- 맥락 윈도우 확대: C2SC 프롬프트에 최근 5턴 + 엔티티 섹션 포함
- TTL 10분 → 30분 확대
- 맥락 기반 엔티티 추적 (종목명/코드, 섹터, 카드 ID)

## 구현 요약

### 1. Redis 키 구조 변경

- **키**: `go100:chat:ctx:{user_id}` (동일)
- **값**: JSON
  - `turns`: 최대 10항목(5턴). 각 항목: `role`, `content`, `intent`, `timestamp`
  - `entities`: `last_stock_code`, `last_stock_name`, `last_sector`, `last_card_id`
  - `last_intent`, `last_message`: 하위 호환
- **TTL**: 1800초(30분)

### 2. ai_router.py 변경

- `_CTX_TTL`: 600 → 1800
- `_save_chat_context`: 단일 저장 → turns 배열 append, assistant 응답 100자 요약 추가, entities 업데이트, reply_summary/params 인자 추가
- `_get_chat_context`: turns/entities 포함 구조 반환, 구 형식 호환
- `_build_c2sc_prompt`: [이전 대화 맥락]에 최근 5턴(10항목), [현재 추적 중인 엔티티] 섹션 추가
- `_resolve_follow_up`: "그종목", "이종목", "이거" 힌트 추가
- 모든 인텐트 핸들러에서 `_save_chat_context` 호출 시 `reply_summary` 전달
- stock_info 개별 종목 응답 시 `result.data`에 `stock_code`, `stock_name` 포함 → 맥락 params로 저장

### 3. llm_router.py 동기화

- `_try_data_backed_response`에서 인터셉트 시 `_save_chat_context(user_id, intent, message, reply_summary=...)` 호출

## 검증

- 서비스 재시작: `systemctl restart go100`
- 5턴 시나리오 테스트: Bearer 토큰 필요. 동일 사용자로 순차 호출 시 Redis에 turns/entities 적재 확인 가능.
- Redis 확인 예시:
  - `redis-cli GET "go100:chat:ctx:1" | python3 -m json.tool`
  - `redis-cli TTL "go100:chat:ctx:1"` → 1800 이하 양수 기대

---

*Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>*
