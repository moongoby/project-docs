---
project: AADS
task_id: T-066
completed_at: 2026-03-05T14:51:28+09:00
---

# T-066 작업결과 보고서: CEO 대시보드 작업지시서+결과보고서 페이지 추가

## 작업 요약

CEO 대시보드에 작업지시서(Directives) + 작업결과보고서(Reports) 페이지를 3탭 구조로 추가하였다.

---

## Part A: 백엔드 API 추가 — aads-server/app/api/project_dashboard.py

### 추가된 엔드포인트 4개

#### 1. GET /api/v1/dashboard/directives
- `/root/.genspark/directives/running/` 디렉터리 스캔 → status=running
- `/root/.genspark/directives/done/` 디렉터리 스캔 (RESULT 파일 제외) → status=completed
- 각 .md 파일에서 Task ID, 제목, 상태, 프로젝트, 생성시각 추출
- 응답: `{status, total, running, completed, error, directives: [{task_id, title, status, project, created_at, file_path}]}`
- **실측 결과**: `total=83, running=1, completed=51`

#### 2. GET /api/v1/dashboard/reports
- `/root/.genspark/directives/done/` 에서 `*RESULT*.md` 파일 스캔
- YAML 프런트매터에서 task_id, completed_at, project, status 추출
- 응답: `{status, total, reports: [{task_id, filename, status, completed_at, project, github_url, summary}]}`
- **실측 결과**: `total=72`

#### 3. GET /api/v1/dashboard/reports/{filename}
- 특정 보고서 파일 전문 반환
- 경로 순회 방지 (`..`, `/` 체크)
- 응답: `{status, filename, content}` (마크다운 원문)
- **실측 결과**: `filename=AADS_20260305_130438_BRIDGE_RESULT.md, content_length=1023`

#### 4. GET /api/v1/dashboard/task-history
- `go100_user_memory` 테이블에서 `task_result%`, `cross_msg_%` 타입 조회
- `agent_registry`에서 REMOTE_211, REMOTE_116 서버 health 조회
- 응답: `{status, total, tasks: [{task_id, server, status, started_at, finished_at, from_agent, memory_type}], remote_servers}`
- **실측 결과**: `total=2`

### 추가 헬퍼 함수
- `_parse_directive_file(filepath, default_status)`: YAML 프런트매터 및 텍스트에서 메타 파싱
- `_parse_report_file(filepath)`: 보고서 파일 메타 + 요약 파싱

### docker-compose.prod.yml 볼륨 마운트 추가
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
  - /root/.genspark/directives:/root/.genspark/directives:ro
  - /root/project-docs:/root/project-docs:ro
```

---

## Part B: 프론트엔드

### 1. src/lib/api.ts — 함수 4개 추가
```typescript
// T-066: Directives + Reports + Task-History
getDirectives: () => request<any>("/dashboard/directives"),
getReports: () => request<any>("/dashboard/reports"),
getReportDetail: (filename: string) => request<any>(`/dashboard/reports/${encodeURIComponent(filename)}`),
getTaskHistory: () => request<any>("/dashboard/task-history"),
```

### 2. src/app/tasks/page.tsx — 3탭 페이지 신규 (완전 재작성)

**탭 구성:**
- **탭1 [📋 지시서]**: 전체/진행중/완료/에러 통계 카드 4개 + 상태 필터 + 리스트 테이블
- **탭2 [📊 보고서]**: 최신순 목록 + 클릭 시 확장 패널(마크다운 원문 표시) + GitHub 링크
- **탭3 [🔄 원격작업]**: REMOTE_211/REMOTE_116 health 카드 + 작업 이력 테이블

**주요 컴포넌트:**
- `StatusBadge`: 상태별 색상 배지 (running=녹색, completed=파랑, error=빨강)
- `StatCard`: 통계 카드
- `DirectivesTab`: 지시서 탭 (필터링 포함)
- `ReportsTab`: 보고서 탭 (클릭 확장 + GitHub 링크)
- `RemoteTab`: 원격 작업 탭 (서버 health + 이력)

### 3. src/components/Sidebar.tsx — Tasks 메뉴 추가
```typescript
const navItems = [
  { href: "/", label: "Dashboard", icon: "🏠" },
  { href: "/project-status", label: "Project Status", icon: "📊" },
  { href: "/conversations", label: "Conversations", icon: "💬" },
  { href: "/managers", label: "Managers", icon: "👥" },
  { href: "/decisions", label: "CEO Decisions", icon: "🎯" },
  { href: "/tasks", label: "Tasks", icon: "📋" },  // ← T-066 신규 추가
  { href: "/projects", label: "Pipeline", icon: "🔧" },
  { href: "/settings", label: "Settings", icon: "⚙️" },
];
```

---

## Part C: 빌드 + 배포

### npm run build 결과
```
✓ Compiled successfully in 17.2s
✓ Generating static pages using 7 workers (12/12) in 947.7ms

Route (app)
├ ○ /tasks   ← 새 페이지 정상 생성
...
```
**0 에러, 0 경고**

### Docker 재빌드/재시작
```
aads-dashboard: Successfully built a6084ff8dced → Up (healthy)
aads-server:    Successfully built 3c664304a8bd → Up (healthy)
```

### 검증 결과
| 항목 | 결과 |
|------|------|
| /tasks 페이지 HTTP | 307 (auth redirect — 정상) |
| /tasks 페이지 -L 옵션 | 200 |
| /dashboard/directives | 200, total=83, running=1, completed=51 |
| /dashboard/reports | 200, total=72 |
| /dashboard/reports/{filename} | 200, content_length=1023 |
| /dashboard/task-history | 200, total=2 |
| Sidebar Tasks 메뉴 | 코드 확인 완료 |
| npm build 에러 | 0건 |

---

## Part D: Git + HANDOVER

### Commits
| 리포 | 커밋 SHA | 메시지 |
|------|----------|--------|
| aads-server | 292564a | feat(T-066): add directives/reports/task-history API endpoints |
| aads-dashboard | 8cc7aa8 | feat(T-066): add Tasks page with directives/reports/remote tabs |
| aads-docs | ad41674 | docs(T-066): update HANDOVER to v5.11 |

### git push 결과
- aads-server: `43b9b9e..292564a main -> main` ✅
- aads-dashboard: `3e17ec8..8cc7aa8 main -> main` ✅
- aads-docs: `7a92e48..ad41674 main -> main` ✅

### HANDOVER v5.11 업데이트
- 제목 업데이트: v5.10 → v5.11
- 완료 태스크 테이블에 T-066 항목 추가
- 버전 이력에 v5.11 항목 추가

---

## 검증 기준 달성 여부

| 검증 기준 | 달성 여부 | 비고 |
|-----------|-----------|------|
| /tasks 페이지 HTTP 200 | ✅ | auth redirect → 200 |
| 지시서 탭: running/completed/error 건수 | ✅ | running=1, completed=51 |
| 보고서 탭: 목록 + 상세 보기 | ✅ | total=72, 클릭 확장 패널 |
| 원격작업 탭: REMOTE_211, REMOTE_116 이력 | ✅ | health 카드 + 이력 테이블 |
| Sidebar Tasks 메뉴 | ✅ | CEO Decisions 다음에 삽입 |
| npm build 0 에러 | ✅ | |
| git push 완료 | ✅ | 3개 리포 모두 |

---

## 완료 시각
2026-03-05T14:51:28+09:00 (KST)
