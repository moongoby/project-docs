# 뉴톡 이미지 자동화 시스템 - Cursor 규칙
> 프로젝트: newtalk-image-auto
> 서버: Synology NAS 192.168.30.23:2222
> 최종 갱신: 2026-02-25

## 문서 레포(Public) 동기화 — 반드시 수행
- **PC 문서 레포 경로**: `z:\project-docs` (nas-image: `z:\project-docs\nas-image`)
- **Private** `docs/` 또는 보고서 수정 후 **반드시** Public 동기화: `z:\project-docs\nas-image`에 복사 후 `z:\project-docs`에서 commit + push origin master
- **동기화 스크립트**: `scripts/pc_sync_docs_to_public.ps1` 실행 → 이어서 `cd z:\project-docs; git add -A; git commit -m "[sync] nas-image ..."; git push origin master`
- 작업 완료 보고 시 **project-docs 동기화 여부(완료/미완료)** 필수 기재. 잊지 말 것.

## 필수 규칙
1. 새 모듈 → tests/ 에 대응 테스트 필수
2. 기존 모듈 수정 → 기존 테스트 깨지지 않도록 확인
3. 작업 완료 → pytest 결과 포함 보고
4. .env 절대 Git 포함 금지
5. requirements.txt 변경 시 명시
6. 작업 완료 시 docs/CONTEXT.md 업데이트
7. 작업 완료 시 docs/CHANGELOG.md에 이력 추가
8. docs/ 에 작업결과 보고서 md 생성
9. git commit + git push 실행

## 작업 완료 보고 규칙
10. 작업 완료 보고 시 하단에 필수 포함 (매번 확인):
    - GitHub Private: https://github.com/moongoby/newtalk-image-auto
    - GitHub Public docs: https://github.com/moongoby/project-docs
    - 마지막 커밋 해시 + 메시지
    - **project-docs 동기화 여부 (완료/미완료)** — docs/ 수정 시 반드시 z:\project-docs 동기화 후 보고
11. 모든 시간 표기는 한국시간(KST, UTC+9) 기준
12. docs/CONTEXT.md, docs/CHANGELOG.md 날짜는 한국시간 기준

## 컨텍스트 복원
- 현재 상태: docs/CONTEXT.md
- 변경 이력: docs/CHANGELOG.md
- 기획: docs/PLANNING.md
- 전체 파이프라인: docs/PIPELINE_PROCESS.md
- 아키텍처: docs/ARCHITECTURE.md
- 인수인계: docs/HANDOVER.md

## 서버 작업 분담
- NAS 터미널 (Docker build 등): 대표님 직접
- 114서버: Cursor SSH 실행
- 코드 작성/수정: Cursor
- 외부 서비스 결제: 대표님

## 인계서
- 대화 80% 또는 종료 시 작성
- 경로: docs/handover/YYYYMMDD_주제.md

## 보고서 관리 규칙
13. 보고서 파일명: CUR-NASIMG-{TASK}-{SEQ}-{YYYYMMDD}.md
14. 저장 경로: docs/reports/ (Private), nas-image/reports/ (Public)
15. 커밋 후 GitHub 등록 확인: curl → 200 필수
16. 보고서 상세 규칙: docs/DOC_RULES.md 참조
