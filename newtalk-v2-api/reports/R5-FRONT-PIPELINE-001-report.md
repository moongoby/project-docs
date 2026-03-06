# R5-FRONT-PIPELINE-001 — 콘텐츠 파이프라인 관리자 페이지 구현 보고서

**Task ID**: T-016
**완료일시**: 2026-03-05 19:50 KST
**서버**: 114 (newtalk-v2-api)
**우선순위**: P1-HIGH

---

## 1. 개요

FRONTEND-AUDIT-001에서 발견된 콘텐츠 파이프라인 관리 페이지 미구현 사항을 완성.
백엔드 ContentPipelineController 10+ EP가 이미 정상 동작하는 상태에서 프론트엔드 연동 레이어 전체를 구축.

---

## 2. 백엔드 EP 목록 (api.php 확인)

```
Route::middleware(['auth:sanctum', 'role:admin|md|outsource'])->prefix('pipeline')->group(function () {
    Route::get('dashboard', ContentPipelineController@dashboard)          GET /api/pipeline/dashboard
    Route::get('statistics', ContentPipelineController@statistics)        GET /api/pipeline/statistics
    Route::post('jobs/bulk-create', ContentPipelineController@bulkCreate) POST /api/pipeline/jobs/bulk-create
    Route::apiResource('jobs', ContentPipelineController)                 GET|POST|GET|PUT /api/pipeline/jobs{/{job}}
    Route::put('jobs/{job}/status', ContentPipelineController@updateStatus)        PUT /api/pipeline/jobs/{job}/status
    Route::put('jobs/{job}/assign-md', ContentPipelineController@assignMD)         PUT /api/pipeline/jobs/{job}/assign-md
    Route::put('jobs/{job}/assign-photo', ContentPipelineController@assignPhotographer) PUT /api/pipeline/jobs/{job}/assign-photo
    Route::put('jobs/{job}/assign-editor', ContentPipelineController@assignEditor) PUT /api/pipeline/jobs/{job}/assign-editor
    Route::post('jobs/{job}/media', ContentPipelineController@uploadMedia)         POST /api/pipeline/jobs/{job}/media
    Route::put('jobs/{job}/link-content', ContentPipelineController@linkContent)   PUT /api/pipeline/jobs/{job}/link-content
    Route::put('jobs/{job}/qa-reject', ContentPipelineController@qaReject)         PUT /api/pipeline/jobs/{job}/qa-reject
});
```

---

## 3. 생성 파일 목록

### Step 1 — 백업
- `frontend/src/lib/content-api.ts.bak.20260305_193730` ✅

### Step 3 — pipeline-api.ts (10함수)
- `frontend/src/lib/pipeline-api.ts`

| 함수명 | 메서드 | 엔드포인트 |
|--------|--------|------------|
| `getPipelineDashboard()` | GET | /api/pipeline/dashboard |
| `getPipelineQueue(params)` | GET | /api/pipeline/jobs |
| `assignPipelineTask(id, assigneeId, role)` | PUT | /api/pipeline/jobs/{id}/assign-{md\|photo\|editor} |
| `updatePipelineStatus(id, status)` | PUT | /api/pipeline/jobs/{id}/status |
| `rejectPipelineItem(id, reason)` | PUT | /api/pipeline/jobs/{id}/qa-reject |
| `approvePipelineItem(id)` | PUT | /api/pipeline/jobs/{id}/status → qa_approved |
| `publishPipelineItem(id)` | PUT | /api/pipeline/jobs/{id}/status → published |
| `getPipelineStats()` | GET | /api/pipeline/statistics |
| `getPipelineByProduct(productId)` | GET | /api/pipeline/jobs?product_id={productId} |
| `bulkAssignPipeline(productIds, assigneeId?)` | POST | /api/pipeline/jobs/bulk-create |

### Step 4 — types/pipeline.ts
- `frontend/src/types/pipeline.ts`
- 타입: `PipelineStatus` (11단계), `PipelineItem`, `PipelineDashboard`, `PipelineStats`, `PipelineQueueParams`, `PipelineQueueResponse`

### Step 5 — 관리자 파이프라인 페이지 (3개)
- `frontend/src/app/(admin)/admin/pipeline/page.tsx` — 대시보드 (상태별 카운트 + 칸반 보드 + 담당자별 현황)
- `frontend/src/app/(admin)/admin/pipeline/queue/page.tsx` — 작업 큐 (상태/기간 필터, 페이지네이션, 일괄 배정)
- `frontend/src/app/(admin)/admin/pipeline/[id]/page.tsx` — 개별 상세 (상태 진행 표시, MD/포토/에디터 배정, QA 승인/반려, 발행)

### Step 6 — 파이프라인 컴포넌트 (6개)
- `frontend/src/components/pipeline/PipelineStatusBadge.tsx` — 11단계 상태 뱃지 (색상 구분)
- `frontend/src/components/pipeline/PipelineDashboardWidget.tsx` — 요약 카드 + 그룹 카드 + 통계
- `frontend/src/components/pipeline/PipelineTaskCard.tsx` — 개별 태스크 카드 (우선순위, 담당자, 마감일)
- `frontend/src/components/pipeline/PipelineKanbanBoard.tsx` — 7컬럼 칸반 보드 (overflow-x scroll)
- `frontend/src/components/pipeline/PipelineAssignDialog.tsx` — 담당자 배정 다이얼로그
- `frontend/src/components/pipeline/PipelineRejectDialog.tsx` — QA 반려 사유 입력 다이얼로그

### Step 7 — admin-layout.tsx 수정
- `frontend/src/components/layout/admin-layout.tsx`
- GitBranch 아이콘 추가
- "콘텐츠 파이프라인" 메뉴 → `/admin/pipeline` 추가 (채널과 설정 사이)

### Step 8 — content-api.ts
- **변경 없음** (wholesale 전용 CRUD만 담당, pipeline은 별도 분리)

---

## 4. 빌드 테스트 결과

```
Node.js: v24.13.0 (playwright driver)
SWC: @next/swc-linux-x64-gnu@15.5.12 (수동 설치)

✓ Compiled successfully in 6.4s
✓ Generating static pages (35/35)
에러: 0건 → PASS
```

---

## 5. API 연동 테스트

```
POST /api/auth/login
  email: admin@newtalk.kr / password: NewTalk2026!@#
  → 200 OK, token 발급 ✅

GET /api/pipeline/dashboard
  HTTP 200 ✅
  Response:
  {
    "success": true,
    "data": {
      "by_status": { "received": 0, "classified": 0, "shooting_queue": 0, ... "cancelled": 0 },
      "total_active": 0,
      "total_published": 0
    }
  }

GET /api/pipeline/statistics
  HTTP 200 ✅
  Response:
  {
    "success": true,
    "data": { "total": 0, "published": 0, "cancelled": 0, "in_progress": 0, "date_from": null, "date_to": null }
  }
```

> 참고: login throttle 5/분 제한으로 rate limit 발생 → 65초 대기 후 재시도

---

## 6. 완료 기준 체크

| 기준 | 상태 |
|------|------|
| pipeline-api.ts 10함수 | ✅ |
| admin 파이프라인 페이지 3개 | ✅ |
| 컴포넌트 6개 | ✅ |
| 레이아웃 메뉴 추가 | ✅ |
| npm run build 에러 0 | ✅ |
| API 연동 200 확인 (dashboard, statistics) | ✅ |
