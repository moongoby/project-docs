# DB-SCHEMA-EXPORT 작업 보고서 (2026-02-23)

## 작업 개요

- **작업 ID**: DB-SCHEMA-EXPORT
- **일시**: 2026-02-23 17:30 KST
- **서버**: root@211.188.51.113 (참조만, 실행 환경 제한)
- **규칙**: DB SELECT 전용, 서비스 재시작 금지, .env 수정 금지, 실데이터 미포함

---

## STEP 0 — 사전 확인

| 항목 | 기대값 | 결과 |
|------|--------|------|
| strategy_cards 건수 | 65 | 미실행 (본 환경 DB 접속 불가, Peer auth) |
| v4_positions OPEN 건수 | 5 | 미실행 (동일) |
| kis-v41-scheduler | active | active |
| kis-v41-monitor | active | active |
| kis-v41-api | active | active |
| 디스크 여유 (/) | — | 43G 여유, 55% 사용 |

*실제 DB 불변 확인은 서버에서 `psql -U kisautotrade -d kisautotrade` 로 수행 권장.*

---

## STEP 1 — DB 스키마 추출

본 환경에서 psql 접속이 불가하여 **실제 쿼리 미실행**.  
스키마 문서는 **코드베이스(ORM 모델)** 및 **v41-architecture-v1.2.md** 기반으로 정리하여 작성함.

- 1-1 ~ 1-8 쿼리: 서버에서 실행 시 `database/DB-SCHEMA.md` 보강 가능.

---

## STEP 2 — 문서 생성

- **경로**: `/root/project-docs/kis-autotrade-v4/database/DB-SCHEMA.md`
- **구조**: 지시서 대로 1. 테이블 개요, 2. V4.1 핵심 테이블 상세(2-1~2-8), 3. GO100, 4. 레거시, 5. 제약/인덱스, 6. 파티션, 7. 추정 행 수, 8. 보안 체크리스트, 9. 변경 이력, 10. 유지보수 규칙
- **내용**: 실데이터·계좌·토큰·IP·비밀번호 미포함

---

## STEP 3 — 보안 검증

```bash
grep -iE "password|secret|token_value|app_key|app_secret|api_key|211\.188|..." DB-SCHEMA.md
```

- **결과**: 0건 (통과)

---

## STEP 4 — 미푸시 보고서

- TOKEN-MANAGER-DIAG: `/root/project-docs/kis-autotrade-v4/reports/TOKEN-MANAGER-DIAG-20260223.md` 이미 존재
- NXT-LIVE-PREP: `/root/project-docs/kis-autotrade-v4/reports/NXT-LIVE-PREP-20260223.md` 이미 존재  
→ 추가 복사 없음.

- **architecture/README.md**: v1.2 행 이미 포함됨.

---

## STEP 5 — 필수 마감 규칙 반영

- **kis-v41-rules.md**: "필수 마감 단계" 섹션 기존 존재
- **추가 반영**: "DB 스키마 변경 시 문서 동기화 규칙" 문단 추가 (DB-SCHEMA.md 업데이트, 변경 이력, project-docs push)

---

## STEP 6 — Git push (project-docs)

- **커밋**: `a83f556 docs: DB-SCHEMA 초판 + 필수마감규칙(DB스키마동기화) (20260223)`
- **변경 파일**: kis-autotrade-v4/database/DB-SCHEMA.md (신규), kis-autotrade-v4/rules/kis-v41-rules.md (수정)
- **push**: origin master 성공

---

## STEP 7 — 최종 검증

| 항목 | 결과 |
|------|------|
| GitHub raw DB-SCHEMA.md | HTTP 200 |
| strategy_cards / v4_positions OPEN | DB 미접속으로 미확인 (서버에서 확인 권장) |
| kis-v41-* 서비스 3개 | active |
| git log --oneline -1 | a83f556 docs: DB-SCHEMA 초판 + ... |

---

## STEP 8 — 보고서 작성 (본 문서)

- **파일**: `/root/project-docs/kis-autotrade-v4/reports/DB-SCHEMA-EXPORT-20260223.md`

---

## 필수 마감: 보고서 push

- 보고서 파일 존재 확인 후 project-docs에 add/commit/push 수행 예정.

---

## 산출물 GitHub 경로

- https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/database/DB-SCHEMA.md
- https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/DB-SCHEMA-EXPORT-20260223.md
- https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/architecture/README.md (v1.2 기존 포함)
- https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/rules/kis-v41-rules.md (필수마감·DB스키마동기화 규칙 반영)
