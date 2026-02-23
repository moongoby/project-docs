# pick_id=8 edit_source E2E 직접 테스트 + TTS 폴백 수정

**작성일시:** 2026-02-21 18:45
**작업 유형:** 버그 수정 / E2E 테스트
**상태:** 완료
**관련 파일:** worker/workers/pipeline_worker.py, worker/services/tts_generator.py, worker/core/retry_engine.py, worker/core/exceptions.py

---

## 1. 작업 개요

- TTS 402 발생 시 DEAD_LETTER로 빠지던 문제를 **ElevenLabs → Google Cloud TTS → Edge-TTS** 3단 폴백으로 수정.
- pick_id=8을 지정해 edit_source 플로우를 직접 실행하고, 결과 영상(pick8_final.mp4)을 검증함.

## 2. 변경 사항

### 2.1 TTS 3단 폴백

- **worker/core/exceptions.py**  
  - `TTSQuotaExceededError(TTSGenerationError)` 추가: ElevenLabs 402 시 폴백용 예외.

- **worker/services/tts_generator.py**  
  - 402 응답 시 `raise TTSQuotaExceededError("ElevenLabs payment required (402)")` 처리 추가.

- **worker/core/retry_engine.py**  
  - `elevenlabs` 정책: `TTSQuotaExceededError`는 재시도하지 않도록 `retry_if_not_exception_type(TTSQuotaExceededError)` 적용.

- **worker/workers/pipeline_worker.py**  
  - `_call_tts_gen`: ElevenLabs 호출 후 `TTSQuotaExceededError` 시 `_call_tts_dual_engine` 호출.
  - `_call_elevenlabs`: 기존 TTS 생성 로직을 `@with_retry("elevenlabs")` 적용 메서드로 분리.
  - `_call_tts_dual_engine`: `tts_dual_engine.generate_narration()`(Google → Edge 폴백) 호출 후 `_build_even_alignment`로 alignment 반환.

### 2.2 pick_id=8 직접 테스트

- 컨테이너 내에서 다음 스크립트 실행:
  - `full_edit_pipeline(sample_source.mp4 → pick8_edited.mp4)` (crop, 55초, 1.1x, 제목/가격 오버레이)
  - `generate_narration(문구 → pick8_narration.mp3)` (Google TTS 사용)
  - `merge_audio_video(edited, audio → pick8_final.mp4)`

## 3. 테스트 결과

- **직접 테스트:** 성공. `Done! Check pick8_final.mp4` 출력, Google TTS로 나레이션 생성 후 Merge 완료.
- **결과 파일:**
  - `pick8_edited.mp4`: 1.7MB
  - `pick8_final.mp4`: 1.8MB
- **ffprobe pick8_final.mp4:**
  - 비디오: 1080x1920, h264, ~50초
  - 오디오: aac, 44100Hz, mono
- **성공 기준 충족:** 1080x1920, h264+aac, ≤55초 ✓

## 4. 주의사항 / 후속 작업

- TTS 폴백 수정 반영 후 `docker compose build worker && docker compose up -d` 로 워커 재빌드·재기동 완료.
- edit_source 플로우는 이미 `generate_narration`/`merge_audio_video`를 사용 중이므로, 이번 3단 폴백은 주로 **AI 이미지 기반 파이프라인**의 TTS 단계(402 시)에 적용됨.
