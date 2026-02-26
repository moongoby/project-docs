# R4-API-005 콘텐츠 파이프라인 API — 완료 보고서

**작성일시**: 2026-02-26 KST  
**버전**: v3.5.0  
**커밋 접두사**: `[R4-API-005]`

---

## 요약

| 항목 | 내용 |
|------|------|
| 테이블 | 3개 (`content_pipeline_jobs`, `pipeline_logs`, `pipeline_media`) |
| 모델 | 3개 (`ContentPipelineJob`, `PipelineLog`, `PipelineMedia`) |
| 서비스 | `ContentPipelineService` (14 메서드) |
| 엔드포인트 | 13개 |
| 워크플로우 | 12단계 (received → published, qa_rejected → editing 재작업) |

---

## R4-API-005 완료

- **테이블 3개**: content_pipeline_jobs, pipeline_logs, pipeline_media  
- **모델 3개**: ContentPipelineJob (STATUS_TRANSITIONS, generateJobNumber, 스코프), PipelineLog, PipelineMedia  
- **서비스**: ContentPipelineService (14 메서드)  
- **엔드포인트 13개**  
- **12단계 워크플로우** (received → classified → shooting_queue → shooting → shot_complete → editing → edit_complete → qa_pending → qa_approved → published, qa_rejected → editing)

---

## STEP 1: 마이그레이션

- `database/migrations/2026_02_26_340004_create_content_pipeline_jobs_table.php`
  - **content_pipeline_jobs**: product_id, assigned_md_id, assigned_photographer_id, assigned_editor_id, job_number(unique), status(12종), content_type, priority, grade, md_notes, shooting_notes, editing_notes, qa_notes, nas_folder_path, content_id(nullable), classified_at, shot_at, edited_at, qa_at, published_at, deadline, timestamps, softDeletes
  - index(status, priority), index(assigned_md_id, status), index(assigned_photographer_id, status), index(product_id)

- `database/migrations/2026_02_26_340005_create_pipeline_logs_table.php`
  - **pipeline_logs**: pipeline_job_id(FK CASCADE), user_id(nullable), from_status, to_status, description, metadata(json), timestamps
  - index(pipeline_job_id, created_at)

- `database/migrations/2026_02_26_340006_create_pipeline_media_table.php`
  - **pipeline_media**: pipeline_job_id(FK CASCADE), stage(raw/edited/final), file_path, file_name, file_size, mime_type, sort_order, ai_metadata, timestamps
  - index(pipeline_job_id, stage)

---

## STEP 2: 모델

- **ContentPipelineJob**  
  - STATUS_TRANSITIONS (허용 상태 전환), generateJobNumber(): CP-YYYYMMDD-XXXXX  
  - 관계: product, assignedMD, assignedPhotographer, assignedEditor, content, logs, media  
  - 스코프: byStatus, byPriority, byAssignedMD, byAssignedPhotographer, byAssignedEditor, deadlineBetween, createdBetween  
  - 상수: STATUS_*, CONTENT_TYPE_*, PRIORITY_*, GRADE_*

- **PipelineLog**  
  - 관계: pipelineJob, user  
  - fillable, casts(metadata => array)

- **PipelineMedia**  
  - 관계: pipelineJob  
  - 상수: STAGE_RAW, STAGE_EDITED, STAGE_FINAL  
  - fillable, casts

---

## STEP 3: 서비스 레이어

**파일**: `app/Services/ContentPipelineService.php`

| # | 메서드 | 설명 |
|---|--------|------|
| 1 | createJob(productId, data) | 파이프라인 작업 생성 |
| 2 | updateStatus(job, newStatus, notes?, userId?) | 상태 전환 + 로그 |
| 3 | assignMD(job, mdUserId) | MD 배정 |
| 4 | assignPhotographer(job, photographerId) | 촬영 담당 배정 |
| 5 | assignEditor(job, editorId) | 편집 담당 배정 |
| 6 | getJobs(filters, perPage) | 작업 목록 (필터·페이지네이션) |
| 7 | getJobDetail(job) | 상세 (로그 + 미디어) |
| 8 | getDashboard() | 현황 대시보드 (상태별·담당자별 건수, 평균 소요일) |
| 9 | uploadMedia(jobId, stage, file, aiMetadata?) | 미디어 업로드 (raw/edited/final) |
| 10 | linkToContent(job, contentId) | 최종 콘텐츠 연결 |
| 11 | rejectQA(job, notes) | QA 반려 → qa_rejected (재작업은 editing으로 전환) |
| 12 | bulkCreateFromInbound(inboundReceiptId) | 입고 완료 시 일괄 작업 생성 |
| 13 | getNASFiles(folderPath) | NAS 파일 목록 조회 (Synology API 스텁) |
| 14 | getStatistics(dateFrom, dateTo) | 기간별 통계 |

---

## STEP 4: 컨트롤러·라우트

**파일**: `app/Http/Controllers/Api/ContentPipelineController.php`

| Method | URI | 메서드 |
|--------|-----|--------|
| POST | /api/pipeline/jobs | store (작업 생성) |
| GET | /api/pipeline/jobs | index (목록) |
| GET | /api/pipeline/jobs/{job} | show (상세) |
| PUT | /api/pipeline/jobs/{job} | update (일반 필드 수정) |
| PUT | /api/pipeline/jobs/{job}/status | updateStatus |
| PUT | /api/pipeline/jobs/{job}/assign-md | assignMD |
| PUT | /api/pipeline/jobs/{job}/assign-photo | assignPhotographer |
| PUT | /api/pipeline/jobs/{job}/assign-editor | assignEditor |
| POST | /api/pipeline/jobs/{job}/media | uploadMedia |
| PUT | /api/pipeline/jobs/{job}/link-content | linkContent |
| PUT | /api/pipeline/jobs/{job}/qa-reject | qaReject |
| POST | /api/pipeline/jobs/bulk-create | bulkCreate |
| GET | /api/pipeline/dashboard | dashboard |
| GET | /api/pipeline/statistics | statistics |

미들웨어: `auth:sanctum`, `role:admin|md|outsource`.

---

## STEP 5: 검증·요청 클래스

- **StoreContentPipelineJobRequest**: product_id(required), content_type, priority, grade, md_notes, shooting_notes, editing_notes, nas_folder_path, deadline
- **UpdateContentPipelineStatusRequest**: status(허용 전환만), notes(optional)
- 컨트롤러 내 validate: assign 시 user_id, link-content 시 content_id, qa-reject 시 notes, bulk-create 시 inbound_receipt_id

---

## 신규·변경 파일 목록

- `database/migrations/2026_02_26_340004_create_content_pipeline_jobs_table.php`
- `database/migrations/2026_02_26_340005_create_pipeline_logs_table.php`
- `database/migrations/2026_02_26_340006_create_pipeline_media_table.php`
- `app/Models/ContentPipelineJob.php`
- `app/Models/PipelineLog.php`
- `app/Models/PipelineMedia.php`
- `app/Services/ContentPipelineService.php`
- `app/Http/Controllers/Api/ContentPipelineController.php`
- `app/Http/Requests/StoreContentPipelineJobRequest.php`
- `app/Http/Requests/UpdateContentPipelineStatusRequest.php`
- `routes/api.php` (pipeline 라우트 그룹)

---

## 검증

- 서버에서 `php artisan migrate` 실행 시 340004, 340005, 340006 마이그레이션 적용.
- `php artisan route:list --path=pipeline` 로 13개 엔드포인트 확인.
- 상태 전환: ContentPipelineJob::STATUS_TRANSITIONS 및 canTransitionTo() 검증.

---

## 최종 요약

**R4-API-005 완료**  
테이블 3개, 모델 3개, 서비스 ContentPipelineService (14 메서드), 엔드포인트 13개, 12단계 워크플로우 (received → published).
