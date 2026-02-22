# GO100 프로젝트 Cursor 규칙
# 작업 전 반드시 docs/ 문서를 읽고 현재 상태를 파악하세요.

## 필수 참조 문서
- docs/CONTEXT.md (전체 요약)
- docs/HANDOVER.md (인수인계서)
- docs/CHANGELOG.md (변경 이력)
- docs/ISSUES.md (알려진 이슈)
- docs/ROADMAP.md (로드맵)
- docs/DB_SCHEMA.md (DB 스키마)
- docs/API_SPEC.md (API 명세)
- docs/PLANNING.md (기획서)
- docs/ARCHITECTURE.md (아키텍처)

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

## 문서 동기화
- bash /root/project-docs/scripts/sync_go100.sh
