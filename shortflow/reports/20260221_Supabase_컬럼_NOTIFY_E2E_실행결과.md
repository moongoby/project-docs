# Supabase video_mode·video_source_url 컬럼 추가, NOTIFY pgrst 및 E2E 실행 결과

**작성일시:** 2026-02-21
**작업 유형:** 설정 변경 / E2E 테스트
**상태:** 부분 완료 (등록·트리거 성공, edit_source 픽 미선정·TTS 402로 *_final.mp4 미생성)
**관련 파일:** `scripts/migrations/add_daily_picks_video_source_columns.sql`, `scripts/e2e_edit_source.sh`

---

## 1. 작업 개요

Supabase에 `video_mode`, `video_source_url` 컬럼 추가 및 PostgREST 스키마 캐시 갱신(NOTIFY pgrst)을 마이그레이션에 반영하고, `e2e_edit_source.sh`를 실행해 테스트 상품 등록 → 파이프라인 트리거 → worker 로그 → ffprobe 결과까지 확인했다.

---

## 2. 변경 사항

### 2.1 Supabase 마이그레이션 + NOTIFY

- **파일:** `scripts/migrations/add_daily_picks_video_source_columns.sql`
- **내용:** `NOTIFY pgrst, 'reload schema';` 를 주석이 아닌 실행문으로 포함. Supabase SQL Editor에서 전체 스크립트를 한 번에 실행하면 ALTER + 스키마 리로드까지 적용된다.

```sql
ALTER TABLE daily_picks ADD COLUMN IF NOT EXISTS video_source_url TEXT;
ALTER TABLE daily_picks ADD COLUMN IF NOT EXISTS video_mode TEXT DEFAULT 'ai_generate';
COMMENT ON COLUMN daily_picks.video_source_url IS '외부 소스 영상 URL (있으면 편집 모드)';
COMMENT ON COLUMN daily_picks.video_mode IS 'ai_generate 또는 edit_source';
NOTIFY pgrst, 'reload schema';
```

### 2.2 E2E 스크립트

- **실행:** `bash /data/shortflow/scripts/e2e_edit_source.sh`

---

## 3. 테스트 결과

### 3.1 1) 테스트 상품 등록

- **결과:** 성공  
- **Inserted pick_id:** 8  
- `video_mode`, `video_source_url` 컬럼이 스키마에 반영되어 insert 정상 동작 (이전 PGRST204 해소).

### 3.2 2) 파이프라인 트리거

- **결과:** 성공  
- **Pipeline response:** 200  

### 3.3 3) 60초 대기 후 worker 로그 (tail 150)

- **결과:** 파이프라인은 동작했으나, **선정된 픽은 pick_id=8이 아님.**
- Job 36: pick_id=7 (테스트 외부편집 상품) → **SCRIPTING → SCRIPTED → GENERATING_IMAGES → IMAGES_READY → GENERATING_TTS** → ElevenLabs **402 Payment Required** → FAILED → DEAD_LETTER.
- Job 37: pick_id=5 (비비고 왕교자 만두) → 동일하게 ai_generate 경로로 진행 후 TTS 402로 DEAD_LETTER.
- **원인:** Daily 파이프라인은 `get_todays_picks()`(picked_date=오늘, status=pending) 또는 fallback으로 `status in ('active','pending')` 중 **random.choice(remaining)** 으로 한 건만 선택한다. 방금 넣은 pick_id=8이 선택되지 않고 7, 5가 선택됨. 또한 7번은 예전에 video_mode 없이 등록된 레코드일 수 있어 ai_generate로 처리됨.

### 3.4 4) 결과 파일 및 ffprobe

- **`*_edited.mp4`, `*_final.mp4`:** 없음 (edit_source 플로우 미진입 + TTS 실패로 compose 단계 미실행).
- **ffprobe:** edit_source 출력물이 없어, E2E에서 사용하는 **소스 영상** `sample_source.mp4` 에 대해 실행한 결과는 아래와 같다.

**sample_source.mp4 (edit_source 소스) ffprobe 요약:**

| 항목 | 값 |
|------|-----|
| 비디오 코덱 | h264 (High 4:4:4 Predictive) |
| 해상도 | 1920x1080 (16:9) |
| 프레임레이트 | 30/1 |
| 길이 | 60.000000초 |
| 오디오 코덱 | aac (LC), mono, 44100 Hz |

---

## 4. 주의사항 / 후속 작업

1. **Supabase:** 컬럼이 아직 없다면 Dashboard → SQL Editor에서 `add_daily_picks_video_source_columns.sql` 전체를 실행하면 ALTER + NOTIFY까지 한 번에 적용된다.
2. **edit_source E2E 검증:** pick_id=8이 반드시 처리되게 하려면  
   - **방법 A:** `POST /api/v1/jobs/create` 로 `pick_id=8` 로 job 생성 후, 해당 job을 pipeline worker로 실행하거나  
   - **방법 B:** E2E 스크립트를 “특정 pick_id로 job 생성 후 run” 하도록 수정해 실행한다.
3. **ElevenLabs 402:** ai_generate 경로에서 TTS가 402 Payment Required로 실패하고 있으므로, edit_source만 검증할 때는 8번 픽이 선정되어 TTS/이미지 생성을 건너뛰고 편집만 수행되면 `*_final.mp4` 생성까지 확인할 수 있다.
