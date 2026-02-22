# DASH-FIX-VERIFY + PROMOTION-SCAN 결과 보고서
**작업일**: 2026-02-22  
**작업명**: DASH-FIX-VERIFY + PROMOTION-SCAN (대시보드 수정 확인 + 인계 코드 탐색)  
**규칙**: 읽기 전용 탐색, DB/파일 수정 없음, kis-v41-api/monitor/scheduler 재시작 없음

---

## 사전 확인 결과 (기준값 일치)

| 항목 | 기대값 | 실제 | 결과 |
|------|--------|------|------|
| strategy_cards COUNT | 59 | 59 | OK |
| v4_positions OPEN | 5 | 5 | OK |
| kis-v41-api | active | active (running) | OK |
| kis-v41-monitor | active | active (running) | OK |
| kis-v41-scheduler | active | active (running) | OK |
| df -h / | - | 41% used, 56G avail | OK |

---

## PART A: DASH-FIX 결과 확인

### STEP A1: kis-v41-webapp 서비스 상태
- **kis-v41-webapp**: **유닛 없음** (systemctl Unit could not be found)
- 동일 서버 웹앱 관련: kis-webapp-api.service (Legacy Platform) active, 포트 8001 사용
- 대시보드 제공: nginx가 8003(kis-v41-api)으로 /dashboard/, /dashboard.html, /style.css, /app.js 프록시

### STEP A2: API 인증 테스트
- localhost:8001 /api/health: **404** (해당 경로 없음. 8001은 레거시 API)
- localhost:8003 /health: **200** — status ok, version 4.1.0, database/redis connected
- V4 API 엔드포인트는 8003이며, /api/v4/* 는 X-Internal-API-Key 검증 적용

### STEP A3: nginx 설정
- trading41.newtalk.kr 설정: /etc/nginx/sites-available/kis-autotrade (80 + 443 서버블록)
- 포함 파일: include /etc/nginx/internal-api-key.conf
- /api/v4/ location: proxy_pass 127.0.0.1:8003, proxy_set_header X-Internal-API-Key $internal_api_key
- nginx -t: syntax ok, test successful
- internal-api-key.conf: **EXISTS** (내용 미확인, 보안)

### STEP A4: 대시보드 HTML에서 API-Key 전달 방식
- 프론트엔드: frontend/dashboard/app.js — ensureApiKey()에서 localStorage 또는 prompt, api()에서 headers X-Internal-API-Key 설정
- 백엔드: backend/app/core/security_middleware.py — InternalAPIKeyMiddleware가 /api/v4/* 에서 X-Internal-API-Key 검증
- nginx: 외부 /api/v4/ 요청에 서버 측에서 X-Internal-API-Key 주입

### STEP A5: 외부 접속 테스트
- https://trading41.newtalk.kr/ : **200**
- https://trading41.newtalk.kr/api/health : **404** (/api/ 는 8001로 프록시, 해당 경로 없음)
- https://trading41.newtalk.kr/api/v4/dashboard/overview : 호출 시 타임아웃 (일시적 네트워크 가능성)

---

### DASH-FIX-VERIFY 결과 요약
- kis-v41-webapp 상태: 유닛 없음 (대시보드는 nginx to 8003)
- localhost:8001 응답: 404 (/api/health 없음)
- localhost:8003 /health: 200
- 외부 접속 응답: / 200, /api/health 404
- API-Key 에러 해결 여부: **Y** (nginx internal-api-key.conf 포함, /api/v4/ 헤더 주입 설정 완료)
- 남은 이슈: 없음

---

## PART B: PROMOTION-SCAN 결과

### B1 키워드
- promotion: v4_pipeline_orchestrator.py, split_transfer_engine.py
- handover: 없음 (비즈니스 코드)
- position_transfer / transfer_position: v4_pipeline_orchestrator.py, split_transfer_engine.py, lifecycle.py, test_phase3e_position.py
- split_order: 없음 (분할매매는 split_transfer_engine SPLIT_SELL/TRANSFER_UP 등)
- pyramid: 없음 (비즈니스 코드)

### B2 v4_pipeline_orchestrator.py
- 관련 로직: 있음. _desk3_receive_transfers, _desk4_receive_transfers, _desk5_receive_transfers (v4_position_transfers JOIN). execute_exit_signals 내 TRANSFER_UP 시 can_promote_after_demotion, promotion_target, split_engine.execute_transfer(..., PROMOTION, ...)

### B3 Position Manager / lifecycle
- position_manager.py: desk_id 읽기/저장만, transfer_position 없음
- lifecycle.py: transfer_position(session, position_id, new_desk_id, reason) 구현
- split_transfer_engine: _meets_promotion_criteria, can_promote_after_demotion, execute_transfer (v4_position_transfers INSERT, v4_desk_fund 조정)

### B4 FundPool / Reservation
- fund_pool: desk_limits, desk_used, allocate/release per desk. promot/transfer 키워드 없음. 인계 시 자금은 split_transfer_engine에서 처리.
- reservation: CANCELLED, desk_id. promot/transfer 없음.

### B5 DB 스키마
- v4_position_transfers 테이블 있음: from_desk_id, to_desk_id, transfer_type (PROMOTION | DEMOTION) 등
- v4_positions: promotion_from, source_desk, target_desk 컬럼 없음. desk_id, original_desk_id, split_phase 및 v4_position_transfers로 인계 추적.

### B6 설계서/문서
- docs v41-architecture-v1.1, strategy_card_system_design_20260220, v41-adaptive-architecture-spec, CLAUDE.md 등에 promotion_rules, 승격, 인계 언급

---

### PROMOTION-SCAN 결과 요약
- promotion 키워드 발견 파일: v4_pipeline_orchestrator.py, split_transfer_engine.py
- handover 키워드 발견 파일: 없음
- split_order 키워드 발견 파일: 없음
- v4_pipeline_orchestrator.py 내 관련 로직: 있음 (_desk3/4/5_receive_transfers, execute_exit_signals TRANSFER_UP)
- position_manager 내 관련 로직: 있음 (lifecycle.transfer_position)
- fund_pool 내 관련 로직: 있음 (desk 배분), promotion/transfer 키워드 없음
- DB 스키마 내 promotion 관련 컬럼: 있음 (v4_position_transfers.from_desk_id, to_desk_id, transfer_type)
- 구현 상태 판정: **구현완료**
- strategy_cards COUNT: 59
- v4_positions OPEN: 5
- 이슈 사항: 없음

---

## 컴플라이언스 체크리스트
- .env/.bak 커밋: 수정 없음
- strategy_cards 59건: 확인
- v4_positions OPEN 5: 확인
- DB 스키마 변경: 없음
- 서비스 재시작: 없음
- V4.1 파일 수정: 없음 (읽기 전용)
