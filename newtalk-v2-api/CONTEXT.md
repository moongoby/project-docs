# NewTalk V2 API — 프로젝트 컨텍스트

**프로젝트**: NewTalk V2 (SNS형 B2B SaaS 마켓플레이스)
**서버**: 114 (rfree-009), Ubuntu 20.04
**스택**: Laravel 12 + Next.js 16, Docker (app/nginx/db/redis/frontend)

## 목적
V1(CodeIgniter 2.x/PHP 5.4)을 Laravel 12 + Next.js 16으로 재구축. SNS형 B2B SaaS 마켓플레이스로 진화.

## 문서 (이 디렉터리 기준)
- **인계서**: [handover/HANDOVER.md](./handover/HANDOVER.md) — 접속 정보, 작업 규칙, 완료/진행 중 작업
- **기획서**: [NT-V2-PLAN-002-FINAL.md](./NT-V2-PLAN-002-FINAL.md) — 8레이어, 66화면, 로드맵
- **아키텍처**: [NT-V2-ARCHITECTURE.md](./NT-V2-ARCHITECTURE.md) — 시스템 구조, Docker, DB
- **변경 이력**: [CHANGELOG.md](./CHANGELOG.md)
- **Cursor 규칙**: [cursorrules.md](./cursorrules.md) — 검토용 사본 (원본은 프로젝트 `.cursorrules`)

## 보고서
- `reports/*.md` — Task별 실행/테스트 보고서 (R1-TASK-001 ~ R2-FRONT-001 등)

## 규칙 요약
- V1 소스/DB 수정 금지 (V1 DB 읽기 전용)
- 민감정보(.env.docker, 비밀번호) Git 커밋 금지
- 커밋 접두사: `[R{n}-{TASK}]`, `[DOCS]`

## 동기화
- project-docs 반영: `bash /data/project-docs/scripts/sync_newtalk_v2_api.sh`
