# CEO DIRECTIVES – NewTalk V2 프로젝트
> 최종 업데이트: 2026-02-28 (v1.0)
> 관리자: CEO (moongoby)
> 용도: 모든 AI 세션에서 필수 읽기. 이 문서의 지시를 위반하는 설계/작업은 무효.

---

## 1. 사고방식 원칙

### D-001 단순 사고 금지
- "하나를 던지면 10을 생각하고 연구해서 반영하라"
- 단일 변수, 단일 시점, 단일 관점 분석은 불충분
- 복합계, 다층 구조, 다시점 분석이 기본

### D-002 교차검증 필수
- Cursor/Claude Code 결과를 무비판적으로 수용하지 말 것
- 수치와 논리를 반드시 검증
- 작업 결과 보고서의 수치·결론·논리적 일관성 확인 후 다음 단계 진행

### D-003 맥락 연속성
- 세션이 끊겨도 맥락이 이어져야 함
- HANDOVER.md가 생명줄 — 매 작업 완료 시 반드시 업데이트
- HANDOVER.md 미업데이트 시 작업 미완료로 간주

### D-004 V1 시스템 보호
- V1(CodeIgniter 2.x/PHP 5.4)은 현재 운영 중인 라이브 시스템
- 소스 코드·DB 무단 수정 절대 금지
- CEO 건별 예외 승인 시에만 수정 가능 (승인 내용을 보고서에 명시)

### D-005 이미지 저장소 정책 (2026-02-28 CEO 승인)
- 이미지는 서버 로컬 디스크에 저장
- Cloudflare CDN이 newtalk.kr 앞단에서 캐시 → 트래픽 과금 $0
- DigitalOcean Spaces URL 사용 금지 (DO CDN은 1TB 초과 시 과금)
- 모든 이미지 URL은 newtalk.kr 도메인으로 통일

---

## 2. 기술적 지시

### T-001 기술 스택
- Backend: Laravel 12 + PHP 8.3-FPM, Sanctum, Spatie Permission (RBAC 6 roles)
- DB: MySQL 8.0 (port 3307), Redis 7 (port 6380)
- Frontend: Next.js 16 (Node 20) + shadcn/ui + App Router
- Gateway: Nginx 1.25-alpine (port 8080)
- Infra: Docker 28.1.1, Compose v2.35.1, Ubuntu 20.04

### T-002 커밋 규칙
- 접두사: [R{라운드}-{TASK번호}] 또는 [DOCS] 또는 [V1-FIX-XXX]
- 예: [R4-FRONT-007] 드롭십 UI, [DOCS] HANDOVER 업데이트, [V1-FIX-001] 이미지 URL 치환
- 빈 테이블 커밋 금지
- 작업 완료 후 반드시 git push origin main 실행
- push 실패 시 즉시 채팅에 오류 메시지 보고

### T-003 Docker 명령 표준
```
docker compose --env-file .env.docker exec app php artisan {command}
docker compose --env-file .env.docker exec app composer {command}
```

### T-004 보고서 규칙
- 위치: /srv/newtalk-v2/docs/reports/{TASK-ID}-report.md
- 필수 항목: 파일 목록, 실행 결과, 테스트 결과, Git SHA
- 보고서 상단에 인계 확인 체크포인트 필수
- GitHub push + HTTP 200 확인 필수

### T-005 백업 규칙
- 파일 수정 전 반드시: cp {파일} {파일}.bak.{YYYYMMDD_HHMMSS}
- DB 수정 전 반드시: mysqldump로 해당 테이블 백업

### T-006 민감정보 관리
- .env.docker, 비밀번호 등 민감정보 Git 커밋 절대 금지
- 인계서에 평문 비밀번호 기록 금지
- 비밀번호는 "참조 경로"만 기재 (예: /srv/newtalk-v2/.env.docker 참조)

### T-007 HANDOVER.md 업데이트 의무
- 모든 작업 완료 시 HANDOVER.md 업데이트 필수
- 업데이트 대상 섹션:
  - 섹션 2 완료 작업에 본 Task 추가
  - 섹션 3 진행 중 작업 갱신
  - 섹션 5 핵심 발견 추가 (해당 시)
  - 섹션 6 웹 Claude 인수인계 갱신
- push 후 HTTP 200 확인:
  curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/newtalk-v2-api/HANDOVER.md
- 보고서 마지막 줄: "HANDOVER.md 업데이트 완료: {커밋해시}"

---

## 3. 절대 규칙 (위반 시 작업 무효)

1. V1 소스 코드 무단 수정 금지 (CEO 건별 예외 승인 필요)
2. V1 DB 쓰기 금지 (읽기만 허용, CEO 예외 승인 시에만 쓰기)
3. .env.docker, 비밀번호 등 민감정보 Git 커밋 금지
4. 작업 완료 시 HANDOVER.md 업데이트 + push 필수
5. 보고서 GitHub push + HTTP 200 확인 필수
6. 기존 운영 시스템(V1 웹, V1 어드민, NAS) 무단 변경 금지
7. Docker 컨테이너 임의 재시작 금지 (확인 후 재시작)

---

## 4. 로드맵

| 단계 | 상태 | 내용 |
|------|------|------|
| R0 인프라 구축 | ✅ 완료 | Laravel 12 + Docker + RBAC |
| R1 백엔드 API | ✅ 완료 | 인증, 상품, 발주, 대시보드, 마이그레이션 (5건) |
| R2 프론트+API | ✅ 완료 | UI 6건 + API 4건 (10건) |
| R3 마켓플레이스 | ✅ 완료 | API 6건 + FRONT 6건 (12건) |
| R4 확장 기능 | ✅ 완료 | API 7건 + FRONT 7건 + DOCS-FIX 2건 (16건) |
| V1-FIX | 🔄 진행중 | V1 이미지 URL 도메인 치환 |
| CODE-REVIEW | ⏳ 대기 | R1~R4 전체 코드 검수 |
| R5 | ⏳ 기획대기 | 일본 크로스보더 + 라이브 B2B |

---

## 5. 버전 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| v1.0 | 2026-02-28 | 초판 – D-001~D-005, T-001~T-007, 절대 규칙 7항, 로드맵 |
