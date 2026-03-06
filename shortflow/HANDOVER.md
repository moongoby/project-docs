# HANDOVER – ShortFlow YouTube Shorts 자동화 SaaS
> 최종 업데이트: 2026-03-06 (v1.8 — SF-T020~T040 완료: 멀티플랫폼 계정UI/Supabase 스키마/헬스체크 API + git push 완전 복구)
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
| GEMINI-CODE-CLEANUP | 03-02 | 코드 내 gemini-2.0-flash 잔존 0건 확인 (이전 커밋 299119b에서 완료) |
| V4-BATCH | 03-02 | v4 전편 6편 합성(ffprobe 전편 통과) + 비공개 업로드 성공 (economy 3편, health 3편) |
| V4-CRON | 03-02 | cron 스케줄러 v4 파이프라인(run_v4_pipeline.py)으로 교체, 구 scheduled_upload.sh 비활성화 |
| OLD-VIDEO-DELETE | 03-02 | v1 10편 + v3 6편 + UPLOAD-TEST 2편 YouTube 삭제 완료 (총 18건, 실패 0건) |
| ALERT-CRON | 03-02 | send_alert_email.py → alert_on_error.sh(Python 우선) + daily_report.sh(이상감지 알림) + run_v4_pipeline.py(단계별 실패 알림) 연동 완료 |
| V4-PUBLIC | 03-03 | 크론 업로드 모드 public 전환 완료 (auto_upload=True, e38d72d) / 기존 6편 공개 전환: OAuth 토큰 만료로 수동 재인증 필요 (STEP1 차단) |
| OAUTH-REAUTH | 03-03 | JSON 토큰 갱신 성공, 6편 공개 전환 완료, run_v4_pipeline.py Python3.9 타입힌트 버그 수정 (367c0a4) |
| CLAUDEBOT-PERM | 03-05 | claudebot /data/shortflow 쓰기 권한 복구 (o+wx 적용) — SF-T001~T008 PREFLIGHT_FAIL 원인 해결 |

| SF-T005 | 03-06 | SaaS DB 스키마 12테이블 (001_saas_schema.sql), verify_schema.py |
| SF-T008 | 03-06 | 멀티플랫폼 동시 업로드 엔진 |
| SF-T009 | 03-06 | hook_presets.json + Prompt v2 (llm_script_engine.py) |
| SF-T011 | 03-06 | upload_metadata.json + 크론 피크타임 (07:30/12:00/19:00) |
| SF-T013 | 03-06 | performance_tracker.py + collect_analytics.py + video_registry.json |
| SF-T014 | 03-06 | content_planner.py + plan_content.py + topic_history |
| SF-T016 | 03-06 | Pipeline v5 통합 (run_v5_pipeline.py 514라인), 크론 v5 교체 |
| SF-T017 | 03-06 | QA Score Engine v2 (qa_score_engine.py + run_qa_check.py) |
| SF-T021 | 03-06 | Gmail SMTP SSL 알림 활성화 (bqizbhzrlixvovvv), 이메일 발송 성공 |
| SF-T022 | 03-06 | 멀티플랫폼 계정 등록 — DB SQL(002_platform_accounts.sql) + API 6엔드포인트 + Next.js 계정 관리 UI + 마이그레이션 스크립트 |
| SF-T030 | 03-06 | Git push 복구 (root SSH 키 인증 성공, 3커밋 동기화) + HANDOVER v1.7 |
| SF-T031 | 03-06 | Supabase 스키마 점검 — DATABASE_URL 없음 확인, REST API로 2/12 테이블 존재 확인, 알림 이메일 ALERT_TEST_OK |
| SF-T032 | 03-06 | 멀티플랫폼 계정 DB + FastAPI API — platforms.json + api/routes/platform_accounts.py + migrate 스크립트 |
| SF-T033 | 03-06 | 멀티플랫폼 계정 관리 대시보드 UI (Next.js) — /dashboard/accounts 페이지, AccountCard, AddAccountModal, 사이드바 수정 |
| SF-T040 | 03-06 | 외부 헬스체크 API 구축 — /api/health (server/disk/git/pipeline/db/env), HEALTH_API_KEY 보호, ALERT_EMAIL_PASSWORD 등록 |

---

## 3. 진행 중 작업

| Task ID | 상태 | 내용 |
|---------|------|------|
| HISTORY-TOKEN | 대기 | history 채널 OAuth 토큰 발급 (CEO 채널ID/이메일 필요) |
| SF-T006 | 대기 | 멀티플랫폼 OAuth 실제 연동 모듈 (현재 UI만 구현) |
| SUPABASE-SCHEMA | 대기 | CEO가 Supabase SQL Editor에서 001_saas_schema.sql 실행 필요 (DATABASE_URL 미설정으로 자동화 불가) |

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
- 크론: economy 09/13/18시, health +10분 등록 (v4 파이프라인 run_v4_pipeline.py로 교체 완료 03-02, 업로드 모드: public 전환 완료 03-03)
- 알림: alert_on_error.sh(09:25/13:25/18:25 Python 우선), daily_report.sh(23:30 이상감지), run_v4_pipeline.py 실패 즉시 알림 연동 완료 (ALERT_EMAIL_PASSWORD 설정 시 활성화)
- 보안: .env, youtube_token_*.json, venv/ 모두 .gitignore 등록
- Cloudflare: shotflow 레코드 Proxied 상태 복원 완료

### API/한도
- YouTube Data API: 10,000 units/day, 업로드 1건 = 1,600 units
- 2채널 × 3회/일 = 9,600 units (96%) — 3채널 시 한도 상향 필요
- Pexels API: 무료, 상업 사용 가능
- Gemini API: Google AI Studio 무료 티어

---

## 6. 웹 Claude 인수인계 사항

### 6-1. 최신 상태 (2026-03-02 기준)
- v4 전편 6편 비공개 업로드 완료 (economy 3편, health 3편)
  - economy: 6s5UU1vFCvg, VIMxlQSSXUQ, tpeRTVKNtng (private)
  - health: 4ZWoA8hbkWs, RtmEvQoM7Iw, OW3_51k40LY (private)
- v4 파이프라인 크론 교체 완료 (run_v4_pipeline.py: LLM대본→v4합성→업로드)
- gemini-2.0-flash 소스 코드 내 0건 확인 (Gemini 2.5 Flash 사용 중)
- v1/v3 테스트 영상 전량 삭제 완료 (18건)
- history 채널은 OAuth 스크립트만 준비, 채널ID/이메일 미확정

### 6-2. 웹 Claude가 해야 할 일
1. v4 영상 CEO 품질 확인 후 공개 전환 승인 요청
2. CEO에게 history 채널 정보(채널ID, 이메일) 확인 요청
3. CEO에게 Gmail App Password 확인 → .env에 ALERT_EMAIL_PASSWORD 설정 (알림 활성화)
4. HISTORY-TOKEN: history 채널 OAuth 토큰 발급 (CEO 정보 확인 후)

### 6-3. 대표님 확인 필요 사항
- history(역사5분) 채널: YouTube Channel ID (UCxxxx), Google 계정 이메일
- v4 영상 품질 최종 확인 후 공개 전환 승인
- CLOVA Voice TTS 네이버 클라우드 API 발급 (또는 Gemini 2.5 Pro TTS로 대체 검토)

### 6-4. 주의사항
- .env, config/youtube_token_*.json, venv/ 절대 커밋 금지
- OAuth 토큰 3개 전부 만료(invalid_grant) — YouTube API 사용 전 브라우저 재인증 필수
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
| v1.8 | 2026-03-06 | SF-T022/T031/T032/T033/T040 완료, 멀티플랫폼 계정 UI + 헬스체크 API + git push 완전 복구, pending 15건 아카이브 |
| v1.7 | 2026-03-06 | SF-T005/T008/T009/T011/T013/T014/T016/T017/T021/T030 완료, Git push 복구, HANDOVER 갱신 |
| v1.0 | 2026-02-28 | 초판 – 전체 대화 내역 + 최종 보고서 기반 작성 |
| v1.1 | 2026-03-02 | V4-BATCH/CRON/DELETE 완료, IP/이메일 마스킹, 섹션 6 갱신 |
| v1.4 | 2026-03-03 | OAUTH-REAUTH 완료: JSON토큰 갱신, 6편 공개, Python3.9 타입힌트 버그 수정 (367c0a4) |
| v1.3 | 2026-03-03 | V4-PUBLIC STEP2 완료 (auto_upload=True, e38d72d) |
| v1.2 | 2026-03-02 | ALERT-CRON 완료 (alert_on_error.sh Python 우선, daily_report.sh 이상감지, run_v4_pipeline.py 에러핸들러) |
