# HANDOVER – ShortFlow YouTube Shorts 자동화 SaaS
> 최종 업데이트: 2026-02-28 (v1.0 — 초판)
> 관리자: CEO (moongoby)
> 용도: 모든 AI 세션(웹 Claude, Cursor, Claude Code) 시작 시 필수 읽기

---

## 1. 프로젝트 개요
- ShortFlow v3.0: YouTube Shorts 자동 생성·업로드 SaaS
- 서버: root@[SERVER-IP] ([SERVER-HOSTNAME], Ubuntu 20.04 Focal), 작업 디렉터리 /data/shortflow
- GitHub 본 레포: https://github.com/moongoby/shortflow (main)
- GitHub 문서 레포: https://github.com/moongoby/project-docs (master)
- 대시보드: https://shotflow.newtalk.kr (Docker 포트 3001, Cloudflare Proxied)
- DB: MySQL autoda (77,122 rows), Supabase (auth + PostgreSQL)
- YouTube 채널: 3분경제 ([CHANNEL-EMAIL-1]), 건강한입 ([CHANNEL-EMAIL-2]), 역사5분 (미발급)
- Tech: Python 3.9.5 (3.8→3.9 업그레이드 완료 02-27), FastAPI, Next.js 14, FFmpeg, Docker, crontab
- YouTube API: 10,000 units/day, 1,600/upload, 최대 6회/일
- LLM: Gemini 2.5 Flash (model ID: gemini-2.5-flash) → Anthropic Claude (폴백) → OpenAI GPT (폴백)
  - 주의: gemini-2.0-flash는 신규 사용 불가 (404), 코드 내 잔존 시 반드시 gemini-2.5-flash로 교체
- TTS: Edge-TTS (1순위), Google Cloud TTS (폴백), CLOVA Voice (미발급)
  - 참고: Gemini 2.5 Pro TTS Preview 모델 존재 → 향후 TTS 대체 검토 가능
- StyleFlow v1.0: 이미지→릴스 변환 서비스 (/data/styleflow, 별도)

---

## 2. 완료된 작업

| Task ID | 날짜 | 핵심 결과 |
|---------|------|-----------|
| PHASE1 | 02-13 | 10-Layer 회피 엔진, FFmpeg 합성, 상태머신, YouTube 업로드 매니저, Dashboard UI |
| PHASE2 | 02-21~23 | .env 보안, OAuth 설정, crontab 스케줄러, NAS 동기화, MOV→MP4 변환, 디스크 정리 |
| PHASE3 | 02-23 | 템플릿 엔진, 업로드 워커, 쿠팡 파트너스 API, E2E 영상 생성, 멀티채널 구조 |
| PHASE4 | 02-24~26 | 외부 접속 복구, Supabase Auth, LLM 대본 v2.0, 3채널 기획서, 인수인계서 v3.0 |
| OAUTH-WEB | 02-26 | YouTube OAuth 웹 클라이언트 발급, economy·health 토큰 발급 성공 |
| UPLOAD-TEST | 02-26 | 비공개 업로드 테스트 성공 (economy ZwysqK_puMY, health nZkJ9PjviH4) |
| CRON-SETUP | 02-26 | economy 09/13/18시, health +10분 크론 등록 |
| LLM-V3 | 02-26 | Gemini 전환 시도 (Python 3.8 제약 → Claude 폴백 동작) |
| PILOT-SCRIPT | 02-26 | 파일럿 대본 6편 생성 (economy 3, health 3) |
| PILOT-V1 | 02-26 | v1 단색배경 영상 6편 합성, ffprobe 통과 |
| PEXELS-API | 02-26 | Pexels API 키 등록, stock_video_downloader.py 구현 |
| PILOT-V3 | 02-26~27 | v3 스톡배경 5편 합성 (health 1편 moov atom 오류 → 재합성 완료) |
| V3-RESOLUTION | 02-27 | v3 전편 6편 해상도 검수 통과 (전부 1080x1920) |
| V3-UPLOAD | 02-27 | v3 스톡배경 6편 비공개 업로드 성공 |
| V4-KEYWORD | 02-27 | v4 채널별 프리셋 키워드 7종 + 세그먼트별 배경 전환 + 자막 개선 |
| V4-TEST | 02-27 | v4 economy·health 각 1편 합성, ffprobe 통과, 스크린샷 확인 |
| PYTHON-UPGRADE | 02-27 | Python 3.8→3.9.5 venv 교체 완료 (3.11은 Focal 미지원) |
| GEMINI-UPGRADE | 02-27 | gemini-2.0-flash → gemini-2.5-flash 전환, SDK 직접 호출 성공 |
| TERMS-PRIVACY | 02-26 | /terms, /privacy 페이지 생성, HTTP 200 확인 |
| DOCS-SYNC | 02-26~27 | project-docs 동기화, sync 스크립트 정상 |
| HISTORY-PREP | 02-27 | history 채널 OAuth 스크립트 준비 (채널ID/이메일 미확정) |
| MONITORING | 02-27 | daily_report.sh(23:30 cron), upload_monitor.sh 점검, alert 미연동 |
| GEMINI-KEY-CHANGE | 02-26 | Gemini API 키 교체 완료 |

---

## 3. 진행 중 작업

| Task ID | 상태 | 내용 |
|---------|------|------|
| V4-BATCH | 대기 | v4 전편 합성 (economy 3편 + health 3편) + 비공개 업로드 |
| V4-CRON | 대기 | cron 스케줄러를 v4 파이프라인으로 교체 |
| GEMINI-CODE-CLEANUP | 대기 | 코드 내 gemini-2.0-flash 잔존 참조를 gemini-2.5-flash로 일괄 교체 |
| OLD-VIDEO-DELETE | 대기 | v1/v3 테스트 영상 YouTube에서 삭제 |
| HISTORY-TOKEN | 대기 | history 채널 OAuth 토큰 발급 (CEO 채널ID/이메일 필요) |
| ALERT-CRON | 대기 | send_alert_email.py를 cron/daily_report에 연동 |

---

## 4. 보류/미시작

| 항목 | 선행조건 | 우선순위 |
|------|----------|----------|
| 비공개→예약공개→공개 전환 로직 | v4 품질 확인 + CEO 승인 | P2 |
| CLOVA Voice TTS 3중 엔진 | 네이버 클라우드 발급 | P2 |
| Gemini 2.5 Pro TTS 검토 | Python 3.9 환경 테스트 | P2 |
| AI 이미지 배경 (Gemini/Imagen) | Gemini SDK 정상화 완료 → 테스트 가능 | P2 |
| 추가 채널 확대 (6→12) | 기존 3채널 안정화 | P3 |
| StyleFlow B2B SaaS 재개 | ShortFlow 안정화 | P3 |
| 쿠팡 파트너스 수익 트래킹 | 대시보드 UI 완성 | P3 |
| Ubuntu 업그레이드 (→22.04+) | Python 3.11 필요 시 | P3 |

---

## 5. 핵심 발견 (누적)

### 영상 품질
- v1(단색배경): 시청 불가 수준, 자막+TTS만 존재
- v3(스톡 1키워드): 키워드 매칭 부정확 — 경제 채널에 흑백 바닷가/외국 화폐, 건강 채널에 단색(다운로드 실패 폴백)
- v4(프리셋+세그먼트전환): 채널별 맞춤 배경, 세그먼트별 전환, 자막 하단 20% 반투명 박스 — 품질 합격
- v4 economy: 100달러 지폐 클로즈업, 금융 차트 등 → 적합
- v4 health: 신선한 농산물/정원 배경 → 적합

### 기술적 전환
- Python 3.8 → 3.9.5 완료 (3.11은 Ubuntu 20.04 Focal에서 미지원)
- Gemini 2.0 Flash → 2.5 Flash 전환 완료 (2.0은 신규 사용 불가 404)
- Gemini 최신 라인업: Gemini 3 Flash(최신), 2.5 Pro, 2.5 Flash, 2.5 Flash-Lite, 2.5 Pro TTS Preview
- google-generativeai SDK: Python 3.9에서 정상 작동 확인

### 인프라
- 디스크: 79% (649GB/875GB), shortflow ~1.5GB
- Docker: shortflow-saas-dashboard 정상 가동 (HTTP 200)
- 크론: economy 09/13/18시, health +10분 등록 (현재 v3 기반 → v4로 교체 필요)
- 보안: .env, youtube_token_*.json, venv/ 모두 .gitignore 등록
- Cloudflare: shotflow 레코드 Proxied 상태 복원 완료

### API/한도
- YouTube Data API: 10,000 units/day, 업로드 1건 = 1,600 units
- 2채널 × 3회/일 = 9,600 units (96%) — 3채널 시 한도 상향 필요
- Pexels API: 무료, 상업 사용 가능
- Gemini API: Google AI Studio 무료 티어

---

## 6. 웹 Claude 인수인계 사항

### 6-1. 최신 상태
- v4 파이프라인 테스트 완료 (economy 1편, health 1편), 품질 합격
- Python 3.9.5 + Gemini 2.5 Flash 직접 호출 정상 확인
- v4 전편 합성 + 업로드는 아직 미실행
- 코드 내 gemini-2.0-flash 참조가 잔존할 수 있음 → 일괄 교체 필요
- history 채널은 OAuth 스크립트만 준비, 채널ID/이메일 미확정

### 6-2. 웹 Claude가 해야 할 일
1. 코드 내 gemini-2.0-flash → gemini-2.5-flash 일괄 교체 지시
2. v4 전편 합성 + 비공개 업로드 지시서 작성 (economy 3편 + health 3편)
3. cron 스케줄러를 v4 기반으로 교체 지시
4. v1/v3 기존 테스트 영상 삭제 지시
5. CEO에게 history 채널 정보(채널ID, 이메일) 확인 요청
6. 영상 공개 전환 시점 CEO와 협의

### 6-3. 대표님 확인 필요 사항
- history(역사5분) 채널: YouTube Channel ID (UCxxxx), Google 계정 이메일
- v4 영상 품질 최종 확인 후 공개 전환 승인
- CLOVA Voice TTS 네이버 클라우드 API 발급 (또는 Gemini 2.5 Pro TTS로 대체 검토)

### 6-4. 주의사항
- .env, config/youtube_token_*.json, venv/ 절대 커밋 금지
- YouTube 업로드는 반드시 private으로 (CEO 승인 전까지)
- API quota 96% 소진 주의 → 하루 6편 이하
- gemini-2.0-flash 모델 ID 사용 금지 (404 에러)
- Cloudflare DNS-only 전환 시 서버 IP 노출 → OAuth 후 즉시 Proxied 복원
- /usr/bin/git commit 사용 (wrapper alias 오류 회피)

---

## 7. 업데이트 규칙
1. 모든 작업 완료 시 본 문서 업데이트 필수
2. 섹션 2에 완료 Task 추가, 섹션 3 갱신, 섹션 6 웹 Claude 인수인계 갱신
3. 업데이트 후 project-docs에 push + HTTP 200 확인
4. 미업데이트 시 작업 미완료로 간주

---

## 8. 버전 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| v1.0 | 2026-02-28 | 초판 – 전체 대화 내역 + 최종 보고서 기반 작성 |
