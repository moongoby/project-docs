# ============================================================
# 뉴톡 V2 프로젝트 — Cursor 필수 규칙
# ============================================================
# 이 파일은 모든 커서 작업에 자동 적용된다.
# 규칙을 위반하는 작업은 수행하지 않는다.

# ============================================================
# 1. 서버 접속
# ============================================================
# - SSH: ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86
# - V2 작업 디렉토리: /srv/newtalk-v2/
# - NAS (시스템 C): ssh newtalk@192.168.30.23 (별도 작업)
# - 작업은 반드시 서버에 접속하여 직접 실행한다.
# - "스크립트 제공", "런북 배치", "서버에서 수동 실행 필요" 형태의
#   작업은 허용하지 않는다. 직접 실행하고 실제 결과를 보고하라.

# ============================================================
# 2. DB 접속
# ============================================================
# - V1 DB (autoda):
#   mysql -u pigupuser -p'<비밀번호>' -h 127.0.0.1 -P 3306 autoda
#   → 읽기 전용. SELECT만 허용.
#   → INSERT/UPDATE/DELETE/DROP/ALTER 절대 금지.
#
#   비밀번호 확인 방법 (2개 경로 존재):
#   ① /home/danharoo/www/application/config/database.php ← 이 파일로 접속 성공 확인됨
#   ② /home/danharoo/pigup/application/config/database.php ← 접속 실패 (참고용)
#   → cat <경로> | grep -A5 "password"
#   → 비밀번호를 보고서/Git/코드에 기록 금지.
#
# - V2 DB (newtalk_v2):
#   mysql -u newtalk_v2_user -p'<비밀번호>' -h 127.0.0.1 -P 3307 newtalk_v2
#   → 자유롭게 작업 가능.
#   → 비밀번호는 /srv/newtalk-v2/.env.docker 참조.
#
# - V1 DB 접속 순서:
#   (1) /home/danharoo/www/application/config/database.php 에서 비밀번호 확인
#   (2) mysql -u pigupuser -p'<비밀번호>' -h 127.0.0.1 -P 3306 autoda -e "SELECT 1;"
#   (3) 성공 확인 후 작업 진행
#   (4) 작업 완료 후 unset DBPW (변수 제거)

# ============================================================
# 3. V1 보호 원칙 (절대 규칙)
# ============================================================
# - V1 소스 (/home/autoda/, /home/danharoo/ 등) 수정 금지. 읽기만 허용.
# - V1 DB (autoda) 쓰기 금지. SELECT만 허용.
# - V1 포트 (80, 443, 3306) 충돌 금지.
# - V1 Apache/Nginx/MariaDB 설정 변경 금지.
# - 작업 후 V1 정상 동작 확인:
#   curl -s -o /dev/null -w "%{http_code}" http://114.207.244.86
#   → 200 확인

# ============================================================
# 4. V2 Docker 환경
# ============================================================
# - 컨테이너: newtalk-v2-app, newtalk-v2-nginx, newtalk-v2-db, newtalk-v2-redis
# - Docker Compose: cd /srv/newtalk-v2 && docker compose --env-file .env.docker
# - Laravel 명령: docker compose --env-file .env.docker exec app php artisan <명령>
# - Composer: docker compose --env-file .env.docker exec app composer <명령>
# - V2 웹: http://114.207.244.86:8080
# - V2 DB 외부: mysql -h 127.0.0.1 -P 3307 -u newtalk_v2_user -p newtalk_v2

# ============================================================
# 5. 백업 규칙
# ============================================================
# - 파일 변경 전: 원본을 .bak.{YYYYMMDD_HHMMSS} 형식으로 백업
# - DB 변경 전: mysqldump로 해당 테이블 백업
# - 백업 위치: /srv/newtalk-v2/backups/
# - 백업 없이 파일을 수정하지 않는다.

# ============================================================
# 6. 보고서 규칙
# ============================================================
# - 작업 시작 시: "작업 시작" 보고 (대상, 예상 변경 사항)
# - 작업 완료 시: 완료 보고서 작성
#   → 경로: /srv/newtalk-v2/docs/reports/<문서번호>-report.md
# - 보고서에는 실제 실행 결과만 기록한다.
#   → "서버에서 실행 후 기입" 같은 빈 칸 금지.
#   → 실행하지 못한 항목은 사유를 명확히 기록.
# - 오류 발생 시: 오류 내용과 시도한 해결 방법 기록.
#
# 6.1 보고서 플레이스홀더 금지 (절대)
# - 커밋 SHA: "푸시후기록", "{SHA}", "(푸시 후 기록)" → push 후 실제 7자리 SHA로 즉시 교체.
# - API 테스트/검수: "(실행 후 기입)", "실행 후 확인" → 서버에서 실제 curl/artisan 실행 후 결과 기입.
# - 서버 전용 항목은 docs/scripts/*-fill-report.sh 실행으로 보고서 파일을 직접 갱신한 뒤 커밋.
# - 플레이스홀더가 남은 보고서로 커밋·push하지 않는다. 작업 미완료로 간주.

# ============================================================
# 7. Git 커밋 규칙
# ============================================================
# - 저장소: GitHub moongoby/newtalk-v2-api-
# - 브랜치: main ← develop ← feature/<작업명>
# - 커밋 메시지: [R0-001], [R0-002] 등 작업번호 접두사
# - 커밋 시 "unknown option trailer" 오류 발생하면:
#   env -i HOME="$HOME" PATH="/usr/bin:/bin" git commit -m "<메시지>"
# - .gitignore 필수 포함: .env, .env.docker, vendor/, node_modules/, backups/
# - 민감정보 (비밀번호, API키) 절대 커밋 금지.
# - GitHub SSH: ~/.ssh/config에 github.com Host 설정 완료 상태.
#   키: /root/.ssh/id_ed25519_newtalk
# - GitHub CLI (gh): 설치 완료. 인증 필요 시 gh auth login -p ssh -h github.com

# ============================================================
# 8. 배포 규칙
# ============================================================
# - R0 단계는 개발 환경 구축. 프로덕션 배포 없음.
# - Docker Compose up/down으로 관리.
# - V1 서비스에 영향 주지 않도록 포트 충돌 확인 필수.

# ============================================================
# 9. 작업 실행 원칙
# ============================================================
# - 지시서의 명령은 서버에서 직접 실행한다.
# - 스크립트를 만들어 놓고 "실행 필요" 형태로 보고하지 않는다.
# - 실행 결과를 있는 그대로 보고한다.
# - 빈 표, 템플릿만 만들어서 보고하지 않는다.
# - 실행할 수 없는 항목은 사유를 명확히 보고한다.

# ============================================================
# 10. 대화 토큰 관리
# ============================================================
# - 토큰 사용량이 컨텍스트 윈도우의 약 80%에 도달하면
#   즉시 작업 중단 후 인계서를 작성하여 보고한다.
# - 인계서 포함 내용:
#   (1) 완료된 작업 목록과 결과물 경로
#   (2) 진행 중이던 작업의 현재 상태
#   (3) 미완료 작업 목록
#   (4) 다음 대화에서 이어가기 위한 컨텍스트

# ============================================================
# 11. 기타
# ============================================================
# - 작업지시서는 전체를 코드블록으로 감싸서 전달된다.
# - 대표님(사용자)은 직접적, 간결한 커뮤니케이션을 선호한다.
# - 불필요한 확인 질문보다 실행 중심으로 진행한다.
# - 잘못된 해석에 대해 즉시 교정이 온다.

# ============================================================
# 12. 작업 완료 후 문서 동기화 (필수)
# ============================================================
# - 모든 작업 완료 후 반드시 아래 순서로 실행:
#   (1) 보고서 작성: /srv/newtalk-v2/docs/reports/{작업ID}-report.md
#   (2) CONTEXT.md 갱신: /srv/newtalk-v2/docs/CONTEXT.md (완료/진행중/다음작업 업데이트)
#   (3) CHANGELOG.md 갱신: /srv/newtalk-v2/docs/CHANGELOG.md
#   (4) project-docs 동기화: bash /data/project-docs/scripts/sync_newtalk_v2_api.sh
#   (5) 양쪽 Git 커밋 & 푸시 (private + project-docs)
# - 동기화 스크립트가 없거나 실패하면 수동 복사:
#   cp /srv/newtalk-v2/docs/CONTEXT.md /data/project-docs/newtalk-v2-api/
#   cp /srv/newtalk-v2/.cursorrules /data/project-docs/newtalk-v2-api/cursorrules.md
#   cp /srv/newtalk-v2/docs/reports/*.md /data/project-docs/newtalk-v2-api/reports/
#
# ============================================================
# 13. project-docs 보안 (Public 저장소)
# ============================================================
# - project-docs에 복사되는 모든 .md에서 민감정보 자동 제거:
#   sed -i 's/NewTalk2026!@#/[REDACTED]/g'
# - 비밀번호, API키, 토큰, .env 내용이 project-docs에 절대 포함되지 않도록 한다.
# - 커밋 전 검사: grep -rIiE "(NewTalk2026|password\s*[:=])" /data/project-docs/newtalk-v2-api/
#
# ============================================================
# 14. Frontend 빌드 규칙
# ============================================================
# - 서버에 Node.js가 없을 수 있으므로 Docker 내부에서 빌드한다.
# - frontend/.env.local은 Git에 커밋하지 않는다.
# - shadcn/ui 컴포넌트 추가: Docker 내부에서 npx shadcn@latest add <컴포넌트>
# - 프론트엔드 서비스: docker compose --env-file .env.docker up -d --build frontend
#
# ============================================================
# 15. 대화 인계 규칙
# ============================================================
# - 대화 종료 또는 토큰 80% 시 인계서 작성:
#   /srv/newtalk-v2/docs/handover/HANDOVER.md (최신 버전 덮어쓰기)
# - 인계서 필수 포함: 완료 작업, 진행중 작업, 다음 단계, Git SHA, 에러, 파일 목록
# - project-docs 동기화 후 인계
# - 새 대화 시작법: https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/CONTEXT.md 전달

# ============================================================
# 16. project-docs 보고서 push 필수 마감 (절대 건너뛰지 않는다)
# ============================================================
# 코드 커밋과 별도로, 작업 완료 시 반드시 아래를 실행한다.
# 이 단계를 건너뛰면 작업 미완료로 간주한다.
#
# (1) 보고서 파일 존재 확인
#     ls -la {project-docs}/newtalk-v2-api/reports/{TASK-ID}-report.md
#     → 없으면 즉시 작성
#
# (2) 핵심 문서 복사 (서버 → project-docs)
#     CONTEXT.md, CHANGELOG.md, HANDOVER.md, cursorrules.md, 보고서
#
# (3) review 소스 복사 (검수 대상이 있을 때)
#     find 로 실제 경로 확인 → 복사 → ls -la 로 존재 확인
#
# (4) 민감정보 검사
#     grep -rIiE "(password|secret|token=|NewTalk2026|Test2026)"
#
# (5) git add -A → git status 확인 → commit → push origin master
#
# (6) push 성공 확인: echo $? → 0, git log --oneline -1
#
# (7) 원격 검증: sleep 30 → curl 200 확인
#
# (8) 실패 시 3회 재시도. 3회 실패 시 에러 원인 보고.
#
# --- {SHA} 플레이스홀더 금지 ---
# CONTEXT, CHANGELOG, 보고서에 {SHA}, (커밋 후 기록) 등 빈칸 금지.
# git log --oneline -1 로 SHA 확인 후 즉시 교체, 재커밋.
