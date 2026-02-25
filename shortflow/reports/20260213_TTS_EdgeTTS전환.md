# TTS Edge TTS 전환

**작성일시:** 2026-02-13  
**작업 유형:** 리팩터링 / 설정 변경  
**상태:** 완료  
**관련 파일:** worker/services/tts_generator.py, worker/config.py, worker/requirements.txt

---

## 1. 작업 개요

ElevenLabs 유료/402 한도를 피하고 무료로 한국어 내레이션을 쓰기 위해 **Edge TTS**를 기본 제공자로 두고, ElevenLabs는 fallback으로 유지했다. Edge TTS는 API 키 없이 사용 가능하며 한국어 네이럴 음성(ko-KR-InJoonNeural 등)을 지원한다.

---

## 2. 변경 사항

### 2.1 worker/requirements.txt

- **edge-tts>=6.1.0** 추가.

### 2.2 worker/config.py

- **tts_provider: str = "edge"** (환경변수 `TTS_PROVIDER`, "edge" | "elevenlabs").
- **edge_tts_voice: str = "ko-KR-InJoonNeural"** (환경변수 `EDGE_TTS_VOICE`, 여성: ko-KR-SunHiNeural 등).

### 2.3 worker/services/tts_generator.py

- **import edge_tts** 추가.
- **generate():** `settings.tts_provider == "edge"` 이면 `_generate_edge(text, pick_id, scene_texts)` 호출 후 반환. 그 외는 기존 ElevenLabs 로직 유지.
- **_generate_edge(text, pick_id, scene_texts):**
  - `edge_tts.Communicate(text, settings.edge_tts_voice)` 로 생성 후 `await communicate.save(output_path)`.
  - 출력 파일 유효성 검사(존재·최소 1000바이트).
  - `_build_even_alignment(output_path, scene_texts or [text])` 로 alignment 생성 후 반환.
- **generate_with_split():** `tts_provider == "edge"` 이면 청크 분할 없이 전체 텍스트로 `_generate_edge()` 한 번 호출. ElevenLabs일 때만 기존 분할·concat·merge 유지.
- ElevenLabs 관련 메서드(_concat_audio, _merge_alignments, 기존 generate 경로 등)는 삭제하지 않고 유지.

### 2.4 .env.example

- TTS_PROVIDER, EDGE_TTS_VOICE 주석 및 예시 추가 (선택).

---

## 3. 테스트 결과

### 3.1 Docker 리빌드 및 기동

- `docker compose down` → `docker compose build worker` → `docker compose up -d` 성공.
- `curl http://localhost:8000/health` → 정상.

### 3.2 파이프라인 재테스트 (Job 5)

- Job 생성 (pick_id=1) → job_id=5.
- 파이프라인 실행 후:
  - 스크립트 생성(Claude) 성공.
  - 이미지 생성(Google Imagen) 5장 성공.
  - **TTS:** `Edge TTS generated: /data/shortflow/data/audio/20260213_1_narration.mp3` (약 3.4초).
  - TTS_READY → GENERATING_CLIPS → CLIPS_READY → COMPOSING 진행.
- 생성 파일: `data/audio/20260213_1_narration.mp3`, `data/temp/.../clip_*.mp4`, `with_audio.mp4`, `with_subs.mp4`, `concat.mp4` 등 확인.

| 단계           | 결과   | 비고                |
|----------------|--------|---------------------|
| 스크립트 생성  | 성공   | Claude              |
| 이미지 생성    | 성공   | Google Imagen 5장   |
| TTS 생성       | **성공** | Edge TTS, 3.4초     |
| 클립/합성      | 진행됨 | Ken Burns 클립·합성 |

**결론:** Edge TTS 전환 후 무료로 TTS 단계 통과, 파이프라인이 합성 단계까지 진행됨.

---

## 4. 주의사항 / 후속 작업

- **음성 변경:** `EDGE_TTS_VOICE=ko-KR-SunHiNeural` 등으로 여성 음성으로 변경 가능.
- **ElevenLabs 복귀:** `TTS_PROVIDER=elevenlabs` 로 설정하면 기존 ElevenLabs 경로 사용.
- **균등 분배 alignment:** Edge TTS도 기존과 동일하게 `_build_even_alignment`로 씬별 균등 분배 적용.
