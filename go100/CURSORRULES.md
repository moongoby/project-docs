# GO100 프로젝트 Cursor 규칙
# 작업 전 반드시 docs/ 문서를 읽고 현재 상태를 파악하세요.
# CUR-GO100-PHASE2-STABILIZE STEP4, 2026-02-23 — 빌드 검증/커밋 후 작업/보고서/필수 참조 문서

## 필수 참조 문서 (전체)
- docs/CONTEXT.md
- docs/PLANNING.md
- docs/ARCHITECTURE.md
- docs/DB_SCHEMA.md
- docs/API_SPEC.md
- docs/HANDOVER.md
- docs/CHANGELOG.md
- docs/ISSUES.md
- docs/ROADMAP.md

## 절대 규칙
1. go100_* 파일/테이블만 수정
2. 모든 수정 파일에 헤더 코멘트 (작업ID, 날짜)
3. .env, .bak 커밋 금지
4. DB 스키마 변경은 go100_* 한정
5. 작업 완료 시 docs/ 문서 업데이트 필수
6. 문서 갱신 후 sync_go100.sh 실행

## 서버 정보
- DB: PGPASSWORD='****' psql -h localhost -U kis_admin -d kisautotrade
- 백엔드: systemctl restart go100 (localhost:8002)
- 프론트: systemctl restart go100-frontend (localhost:3000)
- 빌드: cd frontend && npm run build

## user_id 매핑 주의
- get_effective_uid() 필수
- v4_users: 3=naver, 2=gmail
- legacy users: 15=naver, 6=gmail

## 빌드 검증 규칙
- 프론트엔드 수정 후 반드시: npm run build → BUILD_ID 시간 확인 → 커밋 시간보다 이후인지 검증
- 검증 명령: ls -la frontend/.next/BUILD_ID && git log -1 --format="%ai"
- BUILD_ID가 커밋보다 이전이면 재빌드 필수

## 커밋 후 필수 작업
- bash /root/project-docs/scripts/sync_go100.sh (매 커밋 후 필수)
- report/ 폴더 보고서도 sync 대상에 포함

## 보고서 규칙
- 모든 작업 완료 후 report/YYYYMMDD-TASK-ID.md 생성
- sync_go100.sh 실행하여 project-docs에 반영

## 문서 동기화
- bash /root/project-docs/scripts/sync_go100.sh
