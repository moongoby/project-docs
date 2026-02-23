# CUR-TOKEN-RULE-DOC-UPDATE 보고서

**작업 ID:** CUR-TOKEN-RULE-DOC-UPDATE
**일시:** 2026-02-23 15:50 KST
**서버:** root@211.188.51.113
**유형:** 문서 반영 + 코드 읽기 전용 검증 (코드/DB 변경 없음)

## Phase A: 코드 검증 결과

### KIS (한국투자증권) 토큰 관리

| 항목 | 구현 여부 | 파일:라인 | 구현 방식 |
|------|----------|-----------|-----------|
| 토큰 캐시 | Y | token_manager.py:239-246, 307-311 | Redis (token:kis:{account_id}, TTL 23h) |
| 만료 1시간 전 갱신 | Y | token_manager.py:26, 79-94, 115-131 | RENEW_BEFORE_EXPIRY, _needs_renewal, _is_token_valid |
| 1분 재발급 간격 제한 | Y | token_manager.py:27, 132-143 | REISSUE_LOCK_TTL=60, _acquire_reissue_lock SETNX |
| config_id별 독립 관리 | Y | token_manager.py:30-33, 105 | account_id=kis:{config_id}, Redis 키 구분 |
| 실패 시 재시도/폴백 | 부분 | token_manager.py:90-94 | 1초 sleep 후 캐시 재조회만, 60/120초·3회 초과 degraded 미구현 |

### 키움증권 토큰 관리

| 항목 | 구현 여부 | 파일:라인 | 구현 방식 |
|------|----------|-----------|-----------|
| 토큰 캐시 | Y | token_manager.py | Redis (token:kiwoom:*) |
| 빈 토큰 방어 | Y | token_manager.py:116-118, 216-220, broker_kiwoom_client.py:81-84 | ValueError/RuntimeError + fallback |
| 만료 1시간 전 갱신 | Y | token_manager.py 동일 | get_token → _needs_renewal (79-94) |
| 1분 재발급 간격 제한 | Y | token_manager.py:132-143 | _acquire_reissue_lock (키움 동일) |
| account_id별 독립 관리 | Y | token_manager.py | Redis 키에 account_id 포함 |
| 실패 시 재시도/폴백 | Y | broker_kiwoom_client.py:101-168 | token_manager 실패 → 직접 POST 폴백, 3회 재시도(2^attempt+1초) |
| RPS 제한 | Y | kis_rate_limiter.py:447, 514-521 | TOTAL_KIWOOM_RPS=5, per_account fair-share (3계좌 시 1.67 rps) |

### 키움 수정 이력 (KIWOOM-TEST-003 패치)
- OAuth2 body: appsecret → secretkey 수정
- 빈 토큰 방어: _is_token_valid(), _issue_token_kiwoom(), authenticate() 3곳 패치
- Redis 캐시: 빈 토큰 키 저장 방지 완료

## Phase B: 규칙 추가 내용
- kis-v41-rules.md에 "## API 토큰 관리 규칙 (CEO 지시, 2026-02-23)" 섹션 추가
- KIS 토큰 관리 원칙 (6항목)
- 키움 토큰 관리 원칙 (7항목) + 계좌 현황·앱키 관리
- 공통 금지 사항 (5항목)
- 현행 구현 상태 표

## Phase C: 동기화
- .cursor/rules/kis-v41-rules.md → project-docs/kis-autotrade-v4/rules/kis-v41-rules.md 복사

## Phase D: 커밋
- 코드 repo: phase-2c-command-center에 rules 커밋
- 문서 repo: master에 rules 동기화 커밋

## DB 무결성
- strategy_cards: 65건
- v4_positions OPEN: 5건
- 코드/DB/서비스 변경: 없음

## Git 경로
- rules: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/rules/kis-v41-rules.md
- 보고서: report/v41/TOKEN-RULE-DOC-UPDATE-20260223.md
