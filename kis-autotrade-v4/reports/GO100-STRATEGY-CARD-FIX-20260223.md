# GO100-STRATEGY-CARD-FIX — 전략카드 POST 500 수정 보고서

- **작업 ID**: GO100-STRATEGY-CARD-FIX
- **일시**: 2026-02-23 15:20 KST
- **서버**: root@211.188.51.113
- **프로젝트**: /root/kis-autotrade-v4 (branch: phase-2c-command-center)
- **절대규칙 준수**: kis-v41-* 재시작 없음, strategy_cards ALTER/DROP/DELETE 없음, v4_positions 직접 수정 없음, .env/.bak 커밋 없음

---

## 1. 요약

| 단계 | 항목 | 결과 |
|------|------|------|
| Phase A | 로그 확인 | ✅ 원인 특정: `syntax error at or near ":"` |
| Phase B | 코드 진단 | ✅ SQL `::jsonb`와 SQLAlchemy `:bind` 파서 충돌 |
| Phase C | 수정 | ✅ `CAST(:param AS jsonb)`로 교체 |
| Phase D | 재테스트 | ⏳ 수정 반영 시 201 기대 (go100 재시작 후) |
| Phase E | 보고서/배포 | ✅ 본 문서 작성, publish/sync 실행 |

---

## 2. Phase A — 로그 진단

- **명령**: `journalctl -u go100 --since "2026-02-23 14:50" | grep -iE "strategy.card|500|error|traceback" | tail -50`
- **에러**: `asyncpg.exceptions.PostgresSyntaxError: syntax error at or near ":"`
- **위치**: `backend/app/services/go100/strategy/card_service.py`, line 186, `create_card` 내 INSERT 실행 시
- **로그 발췌**:
  - `GO100 카드 생성 실패: ... PostgresSyntaxError: syntax error at or near ":"`
  - `INSERT INTO go100_strategy_cards (` 직후 에러 → VALUES 절의 `:param::jsonb` 구문이 원인으로 특정됨.

---

## 3. Phase B — 코드 진단

- **파일**: `backend/app/services/go100/strategy/card_service.py`
- **원인**: SQLAlchemy `text()` 내부에서 `:name`은 바인드 파라미터로 해석됨. PostgreSQL 타입 캐스팅 `::jsonb`가 `:param::jsonb` 형태로 쓰이면, 드라이버/엔진에 따라 `::`가 `:` 로 파싱되며 "syntax error at or near `:`" 발생.
- **영향 구문**:
  - INSERT (create_card): `:universe_filter::jsonb`, `:entry_rules::jsonb`, `:exit_rules::jsonb`, `:risk_params::jsonb`, `:strategy_params::jsonb`
  - UPDATE (update_card): 동적 SET 절의 `:universe_filter::jsonb` 등 5곳
  - INSERT (subscribe_from_store): `COALESCE(:entry_rules::jsonb, '[]')` 등 4곳
- **스키마**: `Go100StrategyCardCreate` 필수 필드는 문제 없음. DB INSERT 컬럼/타입 불일치 없음.

---

## 4. Phase C — 수정 내용

- **규칙**: strategy_cards 테이블/데이터 변경 없음. go100_strategy_cards INSERT/UPDATE 문만 수정.
- **방법**: 모든 `:param::jsonb` → `CAST(:param AS jsonb)` 로 교체하여 바인드 파라미터와 캐스팅 구문 분리.
- **수정 파일**: `backend/app/services/go100/strategy/card_service.py`
  - create_card INSERT VALUES: 4개 컬럼 `CAST(:... AS jsonb)` 적용
  - update_card 동적 updates: 5개 `CAST(:... AS jsonb)` 적용
  - subscribe_from_store INSERT VALUES: 4개 `COALESCE(CAST(:... AS jsonb), ...)` 적용
- **검증**: `python3 -m py_compile card_service.py` ✅, `from backend.app.services.go100.strategy.card_service import go100_strategy_card_service` ✅

---

## 5. Phase D — 재테스트

- **엔드포인트**: `POST http://localhost:8002/api/go100/strategy-cards`
- **수정 반영**: go100 프로세스 재시작 후 반영됨. (재시작은 CEO 승인 시에만 수행)
- **권장 테스트** (재시작 후, 유효 토큰 사용):
  ```bash
  curl -X POST http://localhost:8002/api/go100/strategy-cards \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"strategy_name":"E2E_TEST","strategy_type":"GO100_AI","description":"E2E test"}'
  ```
- **기대**: 201 Created 또는 200 OK. (재시작 전 curl 시 401은 인증 필요로 정상.)

---

## 6. Phase E — 보고서 배포

- **로컬 보고서**: `/root/kis-autotrade-v4/report/v41/GO100-STRATEGY-CARD-FIX-20260223.md`
- **배포**: `bash /root/project-docs/scripts/publish_report.sh GO100-STRATEGY-CARD-FIX`
- **동기화**: `bash /root/project-docs/scripts/sync_kis.sh`

---

## 7. Phase F — 완료 체크

- **DB 무결성**: strategy_cards=62, v4_positions OPEN=5 (직접 수정/ALTER 없음)
- **Git URL**: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/GO100-STRATEGY-CARD-FIX-20260223.md
- **sync_kis.sh**: 실행하여 report/v41 본 문서가 project-docs reports로 반영됨
