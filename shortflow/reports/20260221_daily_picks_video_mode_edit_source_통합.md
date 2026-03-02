# daily_picks video_mode·edit_source 통합 (외부 소스 편집 분기)

**작성일시:** 2026-02-21
**작업 유형:** 신규 개발 / 설정 변경
**상태:** 완료
**관련 파일:** `sql/004_daily_picks_video_source.sql`, `worker/workers/pipeline_worker.py`, `worker/config.py`, `.env.example`, `worker/services/video_editor.py`

---

## 1. 작업 개요

`daily_picks`에 외부 소스 영상 URL과 편집 모드를 저장하고, 파이프라인에서 **video_mode**에 따라 AI 생성(기존) vs **외부 소스 편집**을 분기하도록 구현했다. 편집 모드일 때는 이미지 생성 단계를 건너뛰고, 소스 다운로드 → `full_edit_pipeline` → TTS 합성 → 업로드까지 동일 플로우로 동작한다.

## 2. 변경 사항

### 2.1 Supabase `daily_picks` 컬럼 추가

- **파일:** `sql/004_daily_picks_video_source.sql`
- `video_source_url TEXT`: 외부 소스 영상 URL (있으면 편집 모드)
- `video_mode TEXT DEFAULT 'ai_generate'`: `ai_generate` 또는 `edit_source`
- Supabase SQL Editor에서 위 마이그레이션 실행 필요.

### 2.2 pipeline_worker.py 분기 로직

- **`_load_pick_video_info(pick_id)`**  
  `daily_picks`에서 `video_mode`, `video_source_url`, `product_name`, `price` 조회. 없으면 `settings.default_video_mode` 사용.
- **`_step_generate_images`**  
  `video_mode == "edit_source"`이면 이미지 생성 없이 `image_paths = []`로 두고 `IMAGES_READY`로 전이.
- **`_step_compose_video`**  
  - **edit_source + video_source_url 있는 경우**  
    - 소스 URL을 `{data_path}/videos/{job_id}_source.mp4`에 다운로드 (httpx).  
    - `services.video_editor.full_edit_pipeline` 호출: 트림(55초) → 세로 변환(crop/blur) → 속도 변경 → 상품명/가격 자막 → `{job_id}_edited.mp4`.  
    - 기존과 동일하게 TTS 나레이션 생성 후 편집 영상에 합성 → `{job_id}_final.mp4`, `COMPOSED` 전이.
  - **그 외**  
    - 기존 AI 이미지 기반 CompositionPlan → compose → TTS 합성 플로우 유지.

### 2.3 config.py

- `default_video_mode`: `"ai_generate"`
- `default_edit_speed`: `1.1`
- `default_edit_style`: `"crop"` (또는 `"blur"`)
- `default_edit_duration`: `55.0`

### 2.4 .env.example

- `DEFAULT_VIDEO_MODE=ai_generate`
- `DEFAULT_EDIT_SPEED=1.1`
- `DEFAULT_EDIT_STYLE=crop`
- `DEFAULT_EDIT_DURATION=55`

### 2.5 daily_picks 데이터 입력 방식

- 기존 상품: `video_mode` 미지정 시 기본값 `ai_generate` 유지.
- 외부 소스 영상 상품만: `video_mode='edit_source'`, `video_source_url`에 MP4 URL 설정.

## 3. 테스트 결과

- 린트: `pipeline_worker.py`, `config.py` 오류 없음.
- 통합 테스트는 서버에서 아래 절차로 수행.

## 4. 주의사항 / 후속 작업

### 4.1 사전 적용

1. **Supabase**  
   `sql/004_daily_picks_video_source.sql` 실행.
2. **.env**  
   필요 시 `DEFAULT_VIDEO_MODE`, `DEFAULT_EDIT_SPEED`, `DEFAULT_EDIT_STYLE`, `DEFAULT_EDIT_DURATION` 추가.

### 4.2 Docker 재빌드 후 통합 테스트 ([SERVER-ID], `/data/shortflow`)

1. Worker 이미지 재빌드  
   `docker compose build worker` (또는 프로젝트별 compose 파일 기준).
2. `daily_picks`에 테스트 상품 1건 등록  
   - `video_mode = 'edit_source'`  
   - `video_source_url = 'https://...'` (접근 가능한 MP4 URL)  
   - `product_name`, `price` 등 필수 필드 입력.
3. 해당 pick으로 Job 생성 후 파이프라인 트리거 (n8n 또는 Worker API).
4. 확인  
   - 소스 다운로드 → 편집(트림/세로/속도/자막) → TTS 합성 → `COMPOSED` → 업로드(비공개 설정 시 privacy=private)까지 정상 여부.

### 4.3 기타

- 편집 모드에서도 **스크립트 생성 → TTS 생성**은 그대로 수행되어 나레이션 텍스트·음성이 사용된다.
- 소스 다운로드 실패 또는 URL 미접근 시 해당 Job은 실패 처리되며, 필요 시 재시도/DEAD_LETTER 로직으로 처리된다.
