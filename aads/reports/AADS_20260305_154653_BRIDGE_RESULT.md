---
project: AADS
task_id: T-069
completed_at: 2026-03-05T15:55:05+09:00
---

# T-069 실행 결과: Tasks 프론트엔드 전면 개선 + 분석 탭 추가

## 1. 작업 전 백업

```
cp /root/aads/aads-dashboard/src/app/tasks/page.tsx /root/aads/aads-dashboard/src/app/tasks/page.tsx.bak.T069
cp /root/aads/aads-dashboard/src/lib/api.ts /root/aads/aads-dashboard/src/lib/api.ts.bak.T069
```

결과: backup done

---

## 2. src/lib/api.ts — 신규 API 함수 수정

### 변경 내용

- `getDirectives(project?: string)` — 프로젝트 필터 쿼리파라미터 지원 추가
- `getReports(project?: string)` — 프로젝트 필터 쿼리파라미터 지원 추가
- `getAnalytics()` — 기존 함수 유지 (이미 존재)

### 변경 전
```ts
  // T-066: Directives + Reports + Task-History
  getDirectives: () => request<any>("/dashboard/directives"),
  getReports: () => request<any>("/dashboard/reports"),
```

### 변경 후
```ts
  // T-066: Directives + Reports + Task-History
  getDirectives: (project?: string) => request<any>(`/dashboard/directives${project && project !== "all" ? `?project=${encodeURIComponent(project)}` : ""}`),
  getReports: (project?: string) => request<any>(`/dashboard/reports${project && project !== "all" ? `?project=${encodeURIComponent(project)}` : ""}`),
```

---

## 3. src/app/tasks/page.tsx — 4탭 전면 재구성

### 추가된 타입/상수

- `ProjectFilter` 타입: `"all" | "AADS" | "KIS" | "ShortFlow" | "NewTalk" | "GO100" | "NAS"`
- `PROJECT_FILTERS` 배열
- `Directive.error_type?: string` 필드 추가
- `RemoteServer.monitoring_projects?: string[]` 필드 추가
- `ErrorDist` 인터페이스 추가
- `Analytics.error_distribution?: ErrorDist[]` 필드 추가
- `ERROR_TYPES`, `ERROR_TYPE_COLORS` 상수 추가

### 추가된 헬퍼 컴포넌트

- `projectBadgeClass(project)` — 프로젝트별 Tailwind 클래스 반환 (AADS: blue, KIS: purple, ShortFlow: orange, NewTalk: green, GO100: yellow, NAS: pink)
- `ProjectBadge({ project })` — 프로젝트 색상 뱃지 렌더링
- `RemoteStatusBadge({ status })` — active(초록)/reported(파랑)/completed(회색) 색상 구분
- `ProjectFilterBar({ active, onChange })` — 프로젝트 필터 버튼 바 (전체|AADS|KIS|ShortFlow|NewTalk|GO100|NAS)

### 탭1 [지시서] 개선 내용

- KPI 카드 4개: 전체, 진행중, 완료, 에러 (에러 카드에 error_type 비율 표시: auth_expired=회색, task_failure=빨강)
- 상단 프로젝트 필터 버튼 추가 (ProjectFilterBar)
- 상태 필터: 전체|진행중|완료|에러
- 테이블: Task ID, 제목(에러시 error_type 툴팁 인라인 표시), 프로젝트(뱃지 색상별), 상태, 생성시각
- 프로젝트 변경시 API 재호출 (서버사이드 필터링)

### 탭2 [보고서] 개선 내용

- 프로젝트 필터 버튼 추가 (ProjectFilterBar)
- 성공/에러 카운트 표시 (총 N건 / 성공 N / 에러 N)
- filename 기준 중복 제거된 목록
- 클릭시 마크다운 원문 펼침
- GitHub 링크 버튼 스타일 개선 (배경 버튼 형태)
- 프로젝트 뱃지 표시 추가

### 탭3 [원격작업] 개선 내용

- REMOTE_211, REMOTE_114 우선 표시하는 정렬 로직
- 서버 카드: online(에메랄드)/offline(빨강) 색상, last_ping 최근 보고 시각, monitoring_projects 목록 표시
- 작업 테이블: RemoteStatusBadge 적용 — active(초록)/reported(파랑)/completed(회색)

### 탭4 [분석] 개선 내용

- KPI 카드 4개로 재구성: 총 작업수, 성공률(%), 총 비용($), 평균 작업시간(분)
- 프로젝트별 테이블: 프로젝트명(뱃지), 대화수, 비용, 토큰, 최근활동
- 서버별 테이블: 서버명, 작업수, 상태, 최근보고
- 일별 트렌드 바 차트 (최근 7일, .slice(-7))
- 에러 유형 분포 바: auth_expired(회색), permission_denied(노랑), timeout(주황), task_failure(빨강) 각 비율

---

## 4. npm run build (로컬)

```
> aads-dashboard@0.1.0 build
> next build

▲ Next.js 16.1.6 (Turbopack)
- Environments: .env.local

⚠ The "middleware" file convention is deprecated. Please use "proxy" instead.
  Creating an optimized production build ...
✓ Compiled successfully in 18.6s
  Running TypeScript ...
  Collecting page data using 7 workers ...
  Generating static pages using 7 workers (0/12) ...
  Generating static pages using 7 workers (3/12)
  Generating static pages using 7 workers (6/12)
  Generating static pages using 7 workers (9/12)
✓ Generating static pages using 7 workers (12/12) in 808.5ms
  Finalizing page optimization ...

Route (app)
┌ ○ /
├ ○ /_not-found
├ ○ /conversations
├ ○ /decisions
├ ○ /login
├ ○ /managers
├ ○ /project-status
├ ƒ /project-status/[id]
├ ○ /projects
├ ƒ /projects/[id]
├ ƒ /projects/[id]/costs
├ ƒ /projects/[id]/stream
├ ○ /settings
└ ○ /tasks


ƒ Proxy (Middleware)

○  (Static)   prerendered as static content
ƒ  (Dynamic)  server-rendered on demand
```

결과: **빌드 성공**

---

## 5. Docker 빌드

```
BUILDX_CONFIG=/tmp/buildx docker compose -f /root/aads/aads-server/docker-compose.prod.yml build aads-dashboard
```

주요 출력:
```
#10 [aads-dashboard builder 6/6] RUN npm run build
✓ Compiled successfully in 18.7s
✓ Generating static pages using 7 workers (12/12) in 1189.7ms

#14 writing image sha256:b230a2d9a2bc7b2c3b5448af6822e26a01c85403da9a98d2a1893074927924a9
#14 naming to docker.io/library/aads-server-aads-dashboard
#14 DONE 1.1s
```

결과: **Docker 이미지 빌드 성공** (sha256: b230a2d9a2bc7b2c3b5448af6822e26a01c85403da9a98d2a1893074927924a9)

---

## 6. Docker 컨테이너 up

```
BUILDX_CONFIG=/tmp/buildx docker compose -f /root/aads/aads-server/docker-compose.prod.yml up -d aads-dashboard
```

출력:
```
Container aads-dashboard  Recreate
Container aads-dashboard  Recreated
Container aads-dashboard  Starting
Container aads-dashboard  Started
```

결과: **컨테이너 재시작 성공**

---

## 7. HTTP 상태 확인

```
sleep 5 && curl -sL -o /dev/null -w '%{http_code}' https://aads.newtalk.kr/tasks
```

결과: **200**

---

## 8. Git 커밋 및 Push

```
git add src/app/tasks/page.tsx src/lib/api.ts
git commit -m 'feat(T-069): tasks frontend overhaul - project filter, analytics tab, error classification'
git push
```

출력:
```
[main 82bd14f] feat(T-069): tasks frontend overhaul - project filter, analytics tab, error classification
 2 files changed, 273 insertions(+), 70 deletions(-)
To https://github.com/moongoby-GO100/aads-dashboard.git
   15707e2..82bd14f  main -> main
```

커밋 SHA: `82bd14f`
커밋 URL: https://github.com/moongoby-GO100/aads-dashboard/commit/82bd14f

---

## 보고

[CURSOR-AADS] push 완료
작업: T-069 Tasks 프론트엔드 전면 개선 + 분석 탭
커밋: https://github.com/moongoby-GO100/aads-dashboard/commit/82bd14f
HTTP: 200
HANDOVER: 완료
다음: T-070 대기
