# edit_source E2E 테스트 실행 결과 (스키마 캐시 조치)

**작성일시:** 2026-02-21
**작업 유형:** E2E 테스트
**상태:** 부분 완료 (스키마 캐시 조치 후 재실행 필요)
**관련 파일:** `scripts/e2e_edit_source.sh`, `scripts/migrations/add_daily_picks_video_source_columns.sql`

---

## 1. 작업 개요

004 마이그레이션 완료 후 edit_source E2E 테스트를 실행했으나, **Supabase PostgREST 스키마 캐시**에 `video_mode`/`video_source_url` 컬럼이 반영되지 않아 테스트 상품 등록(insert) 단계에서 실패함.

---

## 2. 변경 사항

- **원인:** 마이그레이션 SQL은 적용되었으나 PostgREST가 스키마 캐시를 갱신하지 않아 `PGRST204` (Could not find the 'video_mode' column) 발생.
- **마이그레이션 파일:** `add_daily_picks_video_source_columns.sql`에 스키마 캐시 갱신 안내 주석 추가 (`NOTIFY pgrst, 'reload schema';`).
- **E2E 스크립트 추가:** `scripts/e2e_edit_source.sh` — 테스트 상품 등록 → 파이프라인 트리거 → 대기 → 로그/결과 파일 확인까지 한 번에 실행.

---

## 3. 테스트 결과

| 단계 | 결과 | 비고 |
|------|------|------|
| 1) 테스트 상품 등록 | **실패** | `APIError: PGRST204` (video_mode column not in schema cache) |
| 2) 파이프라인 트리거 | 200 OK | 정상 |
| 3) worker 로그 | 미실행 | insert 실패로 edit_source 픽 없음 |
| 4) `*_final.mp4` | 없음 | edit_source 플로우 미진입 |

---

## 4. 주의사항 / 후속 작업

### 즉시 조치 (Supabase)

1. **Supabase Dashboard → SQL Editor**에서 아래 한 줄 실행:
   ```sql
   NOTIFY pgrst, 'reload schema';
   ```
2. 같은 서버에서 E2E 스크립트 실행:
   ```bash
   bash /data/shortflow/scripts/e2e_edit_source.sh
   ```

### 성공 기준 (재실행 후 확인)

- `*_final.mp4` 파일 생성
- 해상도 1080x1920, 코덱 h264+aac, 길이 55초 이내
- `ffprobe`로 포맷/스트림 확인

### NOTIFY 후 재실행 결과 (2026-02-21)

- **1) 테스트 상품 등록:** 여전히 `PGRST204` (video_mode column not in schema cache). NOTIFY만으로는 반영 안 됨 → **Supabase에서 마이그레이션 SQL(ALTER TABLE)이 실제로 적용된 DB인지 확인 후, 필요 시 ALTER 재실행 + NOTIFY 재실행 권장.**
- **2) 파이프라인 트리거:** 200 OK.
- **3) Worker 로그:** pick_id=7(테스트 외부편집 상품)이 **video_mode 없이** 등록되어 **ai_generate** 경로로 진행됨 → 스크립트·이미지 생성 후 TTS 단계에서 ElevenLabs **402 Payment Required**로 실패 → DEAD_LETTER.
- **4) 결과 파일:** `*_edited.mp4`, `*_final.mp4` 없음 (edit_source 미진입 + TTS 실패로 compose 미실행).

### 수동 실행 예시 (스크립트 대신)

```bash
# 1) 테스트 상품 등록
docker compose exec worker python3 -c "..."  # (e2e_edit_source.sh 내 명령과 동일)

# 2) 파이프라인 트리거
curl -X POST http://localhost:8000/api/v1/pipeline/daily

# 3) 로그 확인
docker compose logs worker --tail 150 -f

# 4) 결과 확인
ls -la /data/shortflow/data/videos/*_edited.mp4 /data/shortflow/data/videos/*_final.mp4
ffprobe -v quiet -print_format json -show_format -show_streams /data/shortflow/data/videos/*_final.mp4
```
