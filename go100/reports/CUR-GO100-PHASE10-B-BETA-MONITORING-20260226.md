# CUR-GO100-PHASE10-B-BETA-MONITORING (2026-02-26)

## 개요
Phase 10-B: 베타 테스트 준비 및 모니터링 구축.

## 완료 항목

### 1. 사용 로그
- **테이블**: `go100_usage_logs` (마이그레이션 `033_go100_usage_logs.sql`)
  - log_id, user_id, session_id, intent, message_preview, response_length, latency_ms, llm_model, llm_tokens_in, llm_tokens_out, is_error, error_type, created_at
  - 인덱스: created_at DESC, (user_id, created_at DESC)
- **서비스**: `backend/app/services/go100/ai/usage_logger.py`
  - `log_chat_usage(...)` — 비동기 INSERT, 에러 시 무시
  - `get_usage_stats(days, db)` — 일별 요청 수, 인텐트 분포, 평균 응답시간, 에러율
  - `get_user_engagement(user_id, days, db)` — 사용자별 일별 대화 수, 상위 인텐트
- **연동**: `ai_router.py`의 `ai_chat()` 모든 반환 경로에서 `asyncio.create_task(log_chat_usage(...))` (fire-and-forget)

### 2. 모니터링 API
- **라우터**: `backend/app/routers/go100/monitor_router.py` (prefix: `/api/go100/monitor`)
  - `GET /health` — 서비스 상태 (DB, Redis, 디스크, 메모리), 인증 없음
  - `GET /stats?days=7` — 사용 통계 (인증 필요)
  - `GET /errors?limit=20` — 최근 에러 목록 (인증 필요)
  - `GET /disk` — 디스크 사용량, 인증 없음

### 3. 헬스체크 크론
- **스크립트**: `scripts/go100/health_monitor.py`
  - 5분마다 실행 권장 (크론 `*/5 * * * *`)
  - 디스크 >85% → 경고 로그 + go100_reports urgent 저장
  - go100 서비스 다운 → 자동 재시작 시도 + 실패 시 urgent 저장
  - DB 연결 실패 → 경고 + urgent 저장
  - 1시간 내 에러율 >10% → 경고 + urgent 저장
  - 환경변수: `GO100_ALERT_USER_ID`(기본 1), `GO100_SERVICE_NAME`(기본 go100)

### 4. 베타 테스트 체크리스트
- **문서**: `project-docs/go100/GO100-BETA-TEST-CHECKLIST.md`
  - 사전 준비, 테스트 시나리오, 모니터링 항목 정리

## 검증
- 마이그레이션 적용: `sudo -u postgres psql -d kisautotrade -f backend/migrations/033_go100_usage_logs.sql`
- 서비스 재시작: `systemctl restart go100`
- 헬스: `curl -s https://go100.newtalk.kr/api/go100/monitor/health | python3 -m json.tool`
- 통계(토큰 필요): `curl -s -H "Authorization: Bearer $TOKEN" "https://go100.newtalk.kr/api/go100/monitor/stats?days=7" | python3 -m json.tool`

## Git
- kis-autotrade-v4: feat(go100): Phase 10-B 베타 모니터링 + 사용 로그
- project-docs: docs(go100): Phase 10-B 베타 모니터링 보고서
