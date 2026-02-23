# ShortFlow TTS 이중 엔진 적용 (Google Cloud + Edge-TTS)

**작성일시:** 2026-02-21
**작업 유형:** 신규 개발 / 설정 변경
**상태:** 완료
**관련 파일:** worker/requirements.txt, worker/services/tts_dual_engine.py, worker/workers/pipeline_worker.py, worker/config.py, .env, .env.example

---

## 1. 작업 개요

Google Cloud TTS를 메인, Edge-TTS를 폴백으로 하는 TTS 이중 엔진을 도입했습니다. 인증/크레딧/네트워크 오류 시 Edge-TTS로 자동 전환되며, compose 완료 후 업로드 전에 해당 엔진으로 나레이션을 생성해 최종 영상에 합성합니다.

## 2. 변경 사항

### 2.1 requirements.txt
- `google-cloud-texttospeech>=2.16.0` 추가 (edge-tts는 기존 유지).

### 2.2 신규 서비스 `worker/services/tts_dual_engine.py`
- **Google Cloud TTS**: Chirp 3 HD 음성, `GOOGLE_APPLICATION_CREDENTIALS`로 키 경로 지정.
- **Edge-TTS**: API 키 없이 사용, 폴백용.
- **`generate_narration(text, output_path, provider=None)`**: `TTS_PROVIDER`에 따라 Google 우선 시도, 실패 시 Edge로 폴백. `provider='edge-tts'`면 Edge만 사용.
- **`merge_audio_video(video_path, audio_path, output_path)`**: FFmpeg로 영상 + 나레이션 합성 (aac 192k, -shortest).

### 2.3 pipeline_worker.py
- Compose 결과로 `video_path` 확정 후, 업로드 전에 다음 단계 삽입:
  1. `data_path/audio/{job_id}_narration.mp3`에 이중 엔진으로 나레이션 생성 (`run_in_executor`로 동기 함수 호출).
  2. `data_path/videos/{job_id}_final.mp4`에 기존 영상 + 나레이션 merge.
  3. `job.artifacts.video_path`를 `final.mp4`로 갱신 후 COMPOSED 전이.

### 2.4 config.py
- TTS 이중 엔진용 설정 추가: `google_tts_voice`, `google_tts_key_path`, `tts_speaking_rate`, `tts_pitch` (기존 Edge 설정과 병행).

### 2.5 .env / .env.example
- TTS 블록 추가: `TTS_PROVIDER`, `GOOGLE_TTS_VOICE`, `GOOGLE_TTS_KEY_PATH`, `TTS_SPEAKING_RATE`, `TTS_PITCH`, `EDGE_TTS_VOICE`, `EDGE_TTS_RATE` (예시/실서버 반영).

### 2.6 docker-compose.yml
- worker 서비스에 이미 `./credentials:/app/credentials` 마운트 있음 → 변경 없음.

## 3. 테스트 결과

- 린트: `tts_dual_engine.py`, `pipeline_worker.py`, `config.py` 오류 없음.
- Docker 재빌드 및 런타임 테스트는 서버에서 아래 명령으로 수행 권장.

```bash
cd /data/shortflow
docker compose down
docker compose build worker
docker compose up -d

# Google Cloud TTS 테스트
docker compose exec worker python3 -c "
from services.tts_dual_engine import generate_narration
result = generate_narration(
    '오늘의 핫딜! 갤럭시 버즈3 프로가 역대 최저가로 나왔습니다. 지금 바로 확인하세요!',
    '/data/shortflow/data/audio/test_google.mp3',
    provider='google-cloud'
)
print('Google TTS:', result)
"

# Edge-TTS 테스트
docker compose exec worker python3 -c "
from services.tts_dual_engine import generate_narration
result = generate_narration(
    '오늘의 핫딜! 갤럭시 버즈3 프로가 역대 최저가로 나왔습니다. 지금 바로 확인하세요!',
    '/data/shortflow/data/audio/test_edge.mp3',
    provider='edge-tts'
)
print('Edge TTS:', result)
"

# 폴백 테스트 (Google 키 없음 → Edge 자동 전환)
docker compose exec worker python3 -c "
import os
os.environ['GOOGLE_TTS_KEY_PATH'] = '/nonexistent.json'
from services.tts_dual_engine import generate_narration
result = generate_narration(
    '폴백 테스트입니다. Edge-TTS로 자동 전환됩니다.',
    '/data/shortflow/data/audio/test_fallback.mp3',
    provider='google-cloud'
)
print('Fallback:', result)
"
```

## 4. 주의사항 / 후속 작업

- **Google Cloud TTS 사용 시**: 서버의 `/data/shortflow/credentials/gcloud-tts-key.json`에 서비스 계정 키를 두고, Cloud Text-to-Speech API 및 Chirp 모델 사용이 허용된 프로젝트인지 확인.
- **경로**: `DATA_PATH`가 `/data/shortflow/data`이면 `audio/`, `videos/`는 그 하위에 생성됨.
- **기존 파이프라인**: 스크립트→이미지→TTS(ElevenLabs/Edge)→클립→compose 흐름은 그대로 두고, compose 이후에만 이중 엔진 나레이션 + merge가 추가됨. 업로드되는 영상은 `*_final.mp4` 기준.
