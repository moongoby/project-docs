# CLAUDE.md — 211서버 멀티 프로젝트 공통 규칙

## 프로젝트 식별
- 작업 지시에 "GO100" 포함 → .cursor/rules/go100-rules.md 적용
- 작업 지시에 "KIS" 또는 "V4.1" 포함 → .cursor/rules/kis-v41-rules.md 적용
- 불명확할 경우 → 반드시 사용자에게 확인 후 진행

## 서버 공통 정보
- 서버: root@kis-autotrade-v4
- 프로젝트 루트: /root/kis-autotrade-v4
- DB: PostgreSQL kisautotrade / kis_admin / localhost:5432
- 백엔드: FastAPI localhost:8002 (systemd go100)
- 프론트: Next.js localhost:3000 (systemd go100-frontend)
- Python 3.12.3, Node v18.19.1

## 공유 테이블 (양쪽 프로젝트 공통)
- v4_users (4행): 사용자 인증/매핑
- accounts (7행): 증권 계좌
- users (12행): 레거시 사용자 (JWT 토큰 소스)
★ user_id 매핑: legacy users.id ≠ v4_users.user_id, 반드시 get_effective_uid() 사용

## 공유 파일 (수정 시 양쪽 영향도 확인 필수)
- backend/app/main.py (라우터 등록)
- backend/app/services/strategy_card_service.py (catalog V4+GO100 병합)
- frontend/src/app/(protected)/strategy-cards/page.tsx
- frontend/src/app/(protected)/backtest/page.tsx
- frontend/src/app/(protected)/layout.tsx

## 공통 절대 규칙
1. .env, .bak 파일 절대 커밋 금지
2. 작업 전 DB 백업: pg_dump -h localhost -U kis_admin -d kisautotrade -F c -f /tmp/backup_<TASK>_$(date +%Y%m%d_%H%M%S).dump
3. 작업 후 빌드 검증: npm run build 후 BUILD_ID 시간 > 커밋 시간 확인
4. 서비스 재시작: sudo systemctl restart go100 && sudo systemctl restart go100-frontend
5. 헬스체크: curl http://localhost:8002/health && curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/go100

## 보고서 push 필수 절차 (CEO 지시, 2026-02-23)

### 원칙
- 모든 작업의 보고서는 **코드 레포 커밋과 별도로** project-docs 레포에 반드시 push해야 한다.
- 보고서가 project-docs에 push되지 않으면 해당 태스크는 "미완료"로 간주한다.
- 코드 레포(kis-autotrade-v4, go100) 커밋 ≠ 문서 레포(project-docs) 커밋이다. 둘 다 해야 완료.

### 모든 커서 지시서 마감 단계 (필수 포함)
모든 지시서의 마지막에 아래 단계를 반드시 포함할 것:

=== 필수 마감: project-docs 보고서 push ===
이 단계를 절대 건너뛰지 마라.
1) 로컬 보고서 존재 확인
REPORT_PATH="/root/project-docs/{프로젝트}/reports/{TASK-ID}-{YYYYMMDD}.md" ls -la "$REPORT_PATH" || { echo "ERROR: 보고서 없음 → 즉시 작성하라"; exit 1; }

2) project-docs 레포에 add/commit/push
cd /root/project-docs git add "$REPORT_PATH" git commit -m "docs: {TASK-ID} 보고서 push ({YYYYMMDD})" git push origin master

3) push 성공 확인
if [ $? -eq 0 ]; then echo "✅ 보고서 push 성공" git log --oneline -1 else echo "❌ push 실패 → 재시도" git pull --rebase origin master && git push origin master if [ $? -ne 0 ]; then echo "❌❌ 2차 push 실패 → 사용자에게 보고" fi fi

4) GitHub URL 접근 확인
curl -s -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/moongoby/project-docs/master/{프로젝트}/reports/{TASK-ID}-{YYYYMMDD}.md"
200이 아니면 에러 보고

### 보고서 경로 규칙
| 프로젝트 | 로컬 작성 경로 | project-docs 경로 |
|----------|---------------|-------------------|
| KIS V4.1 | /root/kis-autotrade-v4/report/v41/{ID}-{DATE}.md | /root/project-docs/kis-autotrade-v4/reports/{ID}-{DATE}.md |
| GO100 | /root/kis-autotrade-v4/report/go100/{ID}-{DATE}.md | /root/project-docs/go100/reports/{ID}-{DATE}.md |

### 동기화 스크립트
- KIS: bash /root/project-docs/scripts/sync_kis.sh
- GO100: bash /root/project-docs/scripts/sync_reports.sh
- 수동: cp + git add/commit/push

### 체크포인트 (지시서에 2개 독립 체크 필수)
- [ ] 코드 레포 커밋 완료 (kis-autotrade-v4 또는 go100)
- [ ] project-docs 보고서 push 완료 (GitHub raw URL 200 확인)

두 체크가 모두 통과해야 태스크 "완료" 판정.

## API 키 보안 절대 규칙 (R-KEY)
- 절대 API 키를 소스코드/config에 하드코딩하지 않는다
- 모든 시크릿은 `.env` 파일에만 저장
- 커밋 전 pre-commit hook이 API 키 패턴 자동 감지 → 차단
- 위반 시: 제공사가 키를 leaked 처리하여 영구 비활성화됨
