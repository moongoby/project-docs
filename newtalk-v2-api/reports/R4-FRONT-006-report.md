# R4-FRONT-006 콘텐츠 파이프라인 UI — 작업 보고서

**작업 ID**: R4-FRONT-006  
**버전**: v3.14.0  
**선행 완료**: R4-API-005 (v3.5.0) — ContentPipelineService, 13 EP, 12단계 워크플로우  
**문서 기준**: CONTEXT.md v3.11.0

---

## 1. 개요

콘텐츠 제작 파이프라인(입고→분류→촬영→편집→QA→퍼블리싱) 전 과정을 관리하는 칸반 보드 + 상세 뷰 + 대시보드 UI. MD/촬영/편집 담당자 사용.

---

## 2. 구현 요약

| 구분 | 내용 |
|------|------|
| 타입 정의 | `frontend/src/types/pipeline.ts` |
| API 클라이언트 | `frontend/src/lib/pipeline-api.ts` (14함수) |
| 컴포넌트 | `frontend/src/components/pipeline/` 12개 + index |
| 페이지 | /admin/pipeline, /admin/pipeline/[id], /admin/pipeline/dashboard, /admin/pipeline/new |
| 레이아웃 | admin-layout "콘텐츠 파이프라인" → /admin/pipeline (Workflow 아이콘) |

---

## 3. 타입 (pipeline.ts)

- **PipelineStatus**: received, classified, shooting_queue, shooting, shot_complete, editing, edit_complete, qa_pending, qa_approved, qa_rejected, published, cancelled (12단계)
- **PipelinePriority**: low, normal, high, urgent
- **PipelineGrade**: A, B, C
- **PipelineContentType**: photo, video, mixed
- **PipelineMediaStage**: raw, edited, final
- **ContentPipelineJob**: id, product_id, job_number, status, content_type, priority, grade, 담당자 ID/관계, 노트, NAS 경로, content_id, 일자 필드, product/assigned_md/assigned_photographer/assigned_editor, logs, media
- **PipelineLog**, **PipelineMedia**, **PipelineDashboard**, **PipelineCreateRequest**, **PipelineListResponse**, **PipelineStatistics**

---

## 4. API 함수 (pipeline-api.ts)

| # | 함수 | 메서드 | 경로 |
|---|------|--------|------|
| 1 | createPipelineJob | POST | /pipeline/jobs |
| 2 | getPipelineJobs | GET | /pipeline/jobs |
| 3 | getPipelineJob | GET | /pipeline/jobs/{id} |
| 4 | updatePipelineJob | PUT | /pipeline/jobs/{id} |
| 5 | updatePipelineStatus | PUT | /pipeline/jobs/{id}/status |
| 6 | assignMD | PUT | /pipeline/jobs/{id}/assign-md |
| 7 | assignPhotographer | PUT | /pipeline/jobs/{id}/assign-photo |
| 8 | assignEditor | PUT | /pipeline/jobs/{id}/assign-editor |
| 9 | uploadPipelineMedia | POST | /pipeline/jobs/{id}/media |
| 10 | linkContent | PUT | /pipeline/jobs/{id}/link-content |
| 11 | rejectQA | PUT | /pipeline/jobs/{id}/qa-reject |
| 12 | bulkCreateJobs | POST | /pipeline/jobs/bulk-create |
| 13 | getPipelineDashboard | GET | /pipeline/dashboard |
| 14 | getPipelineStatistics | GET | /pipeline/statistics |

응답은 `ApiResponse<T>` 래핑 시 `unwrap()`으로 추출.

---

## 5. 컴포넌트 (12개)

| 컴포넌트 | 역할 |
|----------|------|
| PipelineKanbanBoard | 12단계 칸반 보드, 가로 스크롤, 컬럼별 드롭 시 updatePipelineStatus 호출 |
| PipelineJobCard | 칸반 카드(썸네일, 작업번호, 우선순위/등급, 담당자, 마감일), 드래그·클릭 이동 |
| PipelineJobList | 리스트 뷰 테이블, 필터(상태/우선순위/담당자/기간), 페이지네이션 |
| PipelineJobDetail | 작업 상세(상품, 상태 배지, 담당자, 노트, NAS 경로, 미디어 갤러리, 로그) |
| PipelineStatusBadge | 12가지 상태 색상 배지 |
| PipelinePriorityBadge | low=회색, normal=파랑, high=주황, urgent=빨강 |
| PipelineAssignDialog | MD/촬영/편집 담당자 배정 다이얼로그 |
| PipelineMediaGallery | raw/edited/final 탭, 이미지·영상 미리보기, 업로드 버튼 |
| PipelineCreateDialog | 상품 선택, 유형·우선순위·등급·메모·마감일 |
| PipelineDashboardPage | 상태별 건수 도넛 차트, 담당자별 바 차트, 평균 소요일, 지연 건수 |
| PipelineTimeline | 로그 타임라인(상태 변경 이력) |
| index | barrel export |

---

## 6. 페이지 (4개)

| 경로 | 역할 |
|------|------|
| /admin/pipeline | 칸반 보드(기본) + 리스트 뷰 토글, 작업 생성 버튼, 일괄 생성 링크 |
| /admin/pipeline/[id] | 작업 상세 (PipelineJobDetail) |
| /admin/pipeline/dashboard | 파이프라인 대시보드 (PipelineDashboardPage) |
| /admin/pipeline/new | 일괄 생성(상품 ID 입력) + 단일 작업 생성 다이얼로그 |

---

## 7. 파일 목록

```
frontend/src/types/pipeline.ts
frontend/src/lib/pipeline-api.ts
frontend/src/components/pipeline/PipelineStatusBadge.tsx
frontend/src/components/pipeline/PipelinePriorityBadge.tsx
frontend/src/components/pipeline/PipelineJobCard.tsx
frontend/src/components/pipeline/PipelineKanbanBoard.tsx
frontend/src/components/pipeline/PipelineJobList.tsx
frontend/src/components/pipeline/PipelineTimeline.tsx
frontend/src/components/pipeline/PipelineAssignDialog.tsx
frontend/src/components/pipeline/PipelineMediaGallery.tsx
frontend/src/components/pipeline/PipelineCreateDialog.tsx
frontend/src/components/pipeline/PipelineJobDetail.tsx
frontend/src/components/pipeline/PipelineDashboardPage.tsx
frontend/src/components/pipeline/index.ts
frontend/src/app/(admin)/admin/pipeline/page.tsx
frontend/src/app/(admin)/admin/pipeline/[id]/page.tsx
frontend/src/app/(admin)/admin/pipeline/dashboard/page.tsx
frontend/src/app/(admin)/admin/pipeline/new/page.tsx
frontend/src/components/layout/admin-layout.tsx (메뉴 추가)
docs/CHANGELOG.md
docs/CONTEXT.md
docs/architecture/NT-V2-ARCHITECTURE.md
docs/handover/HANDOVER.md
docs/reports/R4-FRONT-006-report.md
```

---

## 8. 테스트·검증

- **TypeScript**: 타입 정의 및 API/컴포넌트 연동 타입 일치
- **Lint**: 수정 구간 린트 에러 없음
- **Docker**: 지시서 STEP 0 기준 5/5 Up (프로젝트 경로에서 확인)
- **백엔드**: pipeline 라우트는 R4-API-005 기준 13 EP; 현재 repo의 `routes/api.php`에는 pipeline 라우트 미등록 상태. 프론트는 14함수·13 EP 스펙에 맞춰 구현 완료. 백엔드 라우트 추가 시 즉시 연동 가능.

---

## 9. 문서 갱신

- **CHANGELOG.md**: [3.14.0] R4-FRONT-006 콘텐츠 파이프라인 UI 추가
- **CONTEXT.md**: 완료 항목 43건, R4-FRONT-006 완료, 다음 작업에서 R4-FRONT-006 제거
- **HANDOVER.md**: R4-FRONT-006 완료 섹션, 다음 작업 큐 갱신
- **NT-V2-ARCHITECTURE.md**: Frontend 라우트에 /admin/pipeline, /admin/pipeline/[id], /admin/pipeline/dashboard, /admin/pipeline/new 추가

---

## 10. Git / 배포

- **STEP 8**: 메인 레포 push — 사용자 실행 (SSH 키·권한 필요)
- **STEP 9**: project-docs 레포 동기화 — 사용자 실행
- **V2 SHA**: push 후 `git log -1 --pretty=%h` 로 기록
- **project-docs SHA**: push 후 동일하게 기록

---

## 11. 다음 작업

- R4-FRONT-007: 위탁배송·드롭십 UI
