# 파일럿 영상 E2E 2채널 제작 보고서

**작성일시:** 2026-02-25 KST
**작업 유형:** 신규 개발 / E2E 테스트
**상태:** 완료
**서버:** rfree-0009.cafe24.com (114.207.244.86)
**프로젝트:** /data/shortflow

## 1. 작업 개요
2개 콘텐츠 채널(3분경제, 건강한입)의 파일럿 영상 E2E 제작.
Gemini 대본 → CLOVA TTS → 이미지 소싱 → FFmpeg 합성 전체 파이프라인 검증.

## 2. 채널 설정

| 채널 | 채널 ID | 계정 | 핸들 |
|------|---------|------|------|
| 3분경제 | UC1qhhty2MDsF4worImq6-dQ | oby240610@gmail.com | @3분경제-m9f |
| 건강한입 | UCKRf4X2fOwhTGcKSVO8rLYQ | moongo76@gmail.com | @건강한입-e1b |

## 3. 생성 결과

| 항목 | 수량 |
|------|------|
| 대본 (JSON) | 5건 |
| TTS (MP3) | 0건 |
| 영상 (MP4) | 0건 |

## 4. 영상 규격
- 해상도: 1080x1920 (9:16)
- 코덱: H.264 / AAC
- FPS: 29.97
- 길이: ≤60초

## 5. 파이프라인
```
Gemini 2.0 Flash → JSON 대본
    ↓
CLOVA Voice TTS → MP3 음성
    ↓
이미지 소싱 (Unsplash/FFmpeg) → JPG/PNG
    ↓
FFmpeg 합성 → MP4 (1080x1920, H.264, AAC)
```

## 6. 다음 작업
1. YouTube 고급 기능 승인 대기
2. OAuth 토큰 발급 (2개 계정)
3. 파일럿 영상 업로드 테스트
4. 업로드 스케줄러 설정

## 7. 백업
- backups/{TIMESTAMP}_pilot_video

## 8. 보고서 GitHub 위치
- shortflow: docs/reports/20260225_pilot_video_E2E_2ch.md
- project-docs: https://raw.githubusercontent.com/moongoby/project-docs/master/shortflow/reports/20260225_pilot_video_E2E_2ch.md
