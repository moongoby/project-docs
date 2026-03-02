# TTS 3중 폴백 + 영상 합성 보고서

**작성일시:** 2026-02-25 KST  
**작업 유형:** TTS 파이프라인 강화 / 영상 합성  
**상태:** 실행 완료 (2026-02-25 15:00 KST)  
**서버:** [SERVER-IP] ([SERVER-HOSTNAME])  
**프로젝트:** /data/shortflow

---

## 1. 개요

대본(JSON) → TTS(MP3) → 영상(MP4) 파이프라인에서 **TTS 3중 폴백**을 적용하여 CLOVA 장애 시에도 Google Cloud TTS, Edge-TTS로 자동 전환되도록 구성했다.

| 순위 | 엔진 | 채널별 음성 | 비고 |
|------|------|-------------|------|
| 1 | CLOVA Voice (네이버) | economy: vdaeseong, health: vgoeun | API 키 필요 |
| 2 | Google Cloud Text-to-Speech | economy: ko-KR-Wavenet-C, health: ko-KR-Wavenet-A | GOOGLE_APPLICATION_CREDENTIALS |
| 3 | Edge-TTS | economy: ko-KR-InJoonNeural, health: ko-KR-SunHiNeural | 무료, 키 불필요 |

---

## 2. 스크립트 위치 및 실행

- **경로:** `scripts/tts_3fallback_video_synth.sh`
- **실행:** 서버에서 `bash scripts/tts_3fallback_video_synth.sh`
- **전제 조건:**
  - `output/scripts/{economy,health}/*.json` 대본 존재
  - `.env`에 CLOVA 키(선택), `GOOGLE_APPLICATION_CREDENTIALS`(선택) 설정
  - Python: `edge-tts`, `google-cloud-texttospeech`, `requests`
  - FFmpeg 설치

---

## 3. 처리 단계

1. **STEP 1:** CLOVA / Google 키 존재 여부 확인  
2. **STEP 2:** `edge-tts`, `google-cloud-texttospeech` 설치·import 확인  
3. **STEP 3:** 채널별 대본 순회 → CLOVA → Google → Edge-TTS 순으로 TTS 생성, `output/tts/{economy,health}/*.mp3` 저장  
4. **STEP 4:** TTS 기준 FFmpeg 영상 합성 (세그먼트별 컬러 배경 + concat), `output/videos/{economy,health}/*.mp4` 저장  
5. **STEP 5:** 대본/TTS/영상 디렉터리 목록 출력 및 TTS/영상 건수 요약  

---

## 4. 영상 규격

- 해상도: 1080×1920 (9:16)
- 비디오: libx264, preset=fast, crf=23, 29.97fps
- 오디오: AAC 128k
- 세그먼트별 고정색 배경 + `-shortest`로 오디오 길이에 맞춤

---

## 5. 작업 완료 후 필수 사항

- 보고서 저장: `/data/shortflow/docs/reports/` (본 문서)
- shortflow 푸시: `git push origin main`
- project-docs 동기화: `/data/project-docs/shortflow/reports/`에 동일 보고서 복사
- project-docs 푸시: `git push origin master`
- 푸시 후 raw URL HTTP 200 확인 및 결과 보고

---

## 6. 관련 문서

- 파일럿 영상 E2E 2채널: `docs/reports/20260225_pilot_video_E2E_2ch.md`
- 스크립트: `scripts/tts_3fallback_video_synth.sh`

---

## 7. raw URL (project-docs 반영 후)

```
https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/20260225_TTS_3fallback_영상합성.md
```

---

## 8. 실행 결과 (2026-02-25 15:00 KST)

| 항목 | economy | health | 합계 |
|------|---------|--------|------|
| 대본(JSON) | 2 | 2 | 4 |
| TTS(MP3) | 2 | 2 | **4** |
| 영상(MP4) | 2 | 2 | **4** |

- **TTS 엔진:** 전건 CLOVA 1순위 성공 (Google/Edge 폴백 미사용)
- **영상 규격:** 1080×1920, 약 60초, H.264/AAC

**TTS 파일**
- economy: `20260225_122907_economy.mp3`, `20260225_122941_2026년_금리_인하가_가져올_변화_.mp3`
- health: `20260225_122918_health.mp3`, `20260225_123015_잠들기_전_절대_하면_안_되는_습관_.mp3`

**영상 파일**
- economy: `20260225_122907_economy.mp4`, `20260225_122941_2026년_금리_인하가_가져올_변화_.mp4`
- health: `20260225_122918_health.mp4`, `20260225_123015_잠들기_전_절대_하면_안_되는_습관_.mp4`
