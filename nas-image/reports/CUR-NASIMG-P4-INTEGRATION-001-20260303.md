# CUR-NASIMG-P4-INTEGRATION-001-20260303

> 작성일: 2026-03-03 KST
> 작업자: Cursor AI (claude-4.6-sonnet-medium-thinking)
> 태스크: P4-INTEGRATION — P4 통합 파이프라인 E2E 연결 + 테스트

---

## §1. 구현 개요

P4 6개 모듈을 단일 파이프라인으로 연결하는 E2E 오케스트레이터 구현.

```
입력: /data/photos/{코디폴더}/_acut_v2/ (P3 A컷 결과)
│
├─ [P4-A] crop_images()        → _cropped/   (1:1, 3:4)
├─ [P4-B] tone_adjust()        → _toned/     (프리셋 자동 매칭)
├─ [P4-C] retouch_images()     → _retouched/ (default 프리셋)
├─ [P4-D] generate_intro_from_folder() → _intro/ (템플릿 A+C)
├─ [P4-E] rename_files()       → _renamed/   (rename_map.json)
└─ [P4-F] deploy_images()      → CDN dry-run + DB mock
```

---

## §2. 구현 내용

### 2-1. app/workers/p4_pipeline.py (통합 오케스트레이터)

| 요소 | 내용 |
|------|------|
| `run_p4_pipeline()` | E2E 파이프라인 실행, P4PipelineResult 반환 |
| `P4PipelineResult` | 단계별 StageResult, elapsed, rename_map, errors 포함 |
| `StageResult` | stage명, success, skipped, output_folder, file_count, elapsed_sec |
| 단계 실패 처리 | 해당 단계 skip + 다음 단계 진행 (fallback) |
| 원본 보호 | 파이프라인 전후 MD5 해시 비교로 원본 미변경 검증 |
| 1x1/3x4 분리 | `_split_by_pattern()` — `_crop_1x1`, `_crop_3x4` 패턴으로 파일 분류 |
| cdn_dry_run=True | 기본값 — 실배포는 CEO 승인 필요 |
| db_mock=True | 기본값 — 실DB는 CEO 승인 필요 |

### 2-2. app/api/pipeline_router.py (FastAPI 라우터)

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| /api/v1/pipeline | POST | 단건 파이프라인 실행 |
| /api/v1/pipeline/batch | POST | 배치 실행 (run_async 지원) |
| /api/v1/pipeline/status/{job_id} | GET | 배치 실행 상태 조회 |

### 2-3. app/main.py 갱신

pipeline_router 등록:
```python
from app.api.pipeline_router import router as pipeline_router
app.include_router(pipeline_router)
```

---

## §3. 테스트 결과

```
tests/test_pipeline.py — 10 passed in 26.66s

TC-01: TestE2EPipeline::test_full_pipeline_succeeds             PASSED
TC-02: TestE2EPipeline::test_stages_have_output_folder          PASSED
TC-03: TestRenameMap::test_rename_map_follows_naming_convention PASSED
TC-04: TestStageFallback::test_retouch_failure_continues_pipeline PASSED
TC-05: TestResultStructure::test_result_has_required_fields     PASSED
TC-05b: TestResultStructure::test_each_stage_has_elapsed        PASSED
TC-06: TestBatchPipeline::test_batch_multiple_codys             PASSED
TC-07: TestSourceIntegrity::test_source_files_unchanged         PASSED
TC-08: TestPipelineRouter::test_post_pipeline_http_200          PASSED
TC-09: TestPipelineRouter::test_post_pipeline_missing_goods_code_422 PASSED
```

전 테스트 HTTP mock(unittest.mock.patch) 사용 — 실제 이미지 처리/DB/CDN 호출 없음.
원본 파일 절대 수정/삭제 없음.

---

## §4. 파이프라인 파라미터

```json
{
  "cody_folder":     "/data/photos/시크블랙_코디01",
  "goods_code":      "BL5889K62",
  "goods_name":      "시크블랙 코트",
  "tone_preset":     "auto",
  "retouch_model":   "default",
  "intro_templates": ["A", "C"],
  "cdn_dry_run":     true,
  "db_mock":         true,
  "acut_suffix":     "_acut_v2"
}
```

---

## §5. 커밋 정보

- **커밋 SHA**: b0c9894
- **HTTP 200**: pytest 10 PASS
- **security_scan**: API 키 .env 전용, 보고서 미포함
- **path_check**: app/workers/p4_pipeline.py, app/api/pipeline_router.py, tests/test_pipeline.py
- **project-docs 동기화**: 완료

---

## §6. 잔여 사항 (CEO 확인 필요)

| 항목 | 내용 |
|------|------|
| P4-E-DEPLOY 실배포 | cdn_dry_run=false, db_mock=false — CEO 승인 필요 |
| P4-114-API 실배포 | 114서버 SSH 접속 + deploy_114_api.sh 실행 |
| NAS_API_KEY 발급 | 114서버 환경변수 + NAS .env 설정 |
| Docker rebuild | Dockerfile 변경사항 반영 (fonts-nanum) |
