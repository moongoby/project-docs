# CEO DIRECTIVES – ShortFlow YouTube Shorts 자동화 SaaS
> 최종 업데이트: 2026-02-28 (v1.0)
> 관리자: CEO (moongoby)
> 용도: 모든 AI 세션에서 필수 읽기. 이 문서의 지시를 위반하는 설계/작업은 무효.

---

## 1. 사고방식 원칙

### D-001 단순 사고 금지
- "하나를 던지면 10을 생각하고 연구해서 반영하라"
- 단일 변수, 단일 시점, 단일 관점 분석은 불충분
- 복합계, 다층 구조, 다시점 분석이 기본

### D-002 영상 품질이 최우선
- 배경이 없는 단색 영상은 Shorts로서 가치 없음
- 배경 영상/이미지는 반드시 대본 내용과 일치해야 함
- 자막은 가독성 최우선 (하단 20%, 반투명 박스, 40px 흰색)
- 매 파이프라인 변경 시 반드시 스크린샷으로 품질 검증
- v3 실패 사례: 경제 채널에 바닷가/외국 화폐, 건강 채널에 단색 배경 — 이런 결과는 불합격

### D-003 자동화가 핵심
- 대본 생성 → TTS → 배경 → 합성 → 업로드 전 과정이 무인 자동
- cron 기반 스케줄링, 에러 시 자동 재시도 + 알림
- 사람이 개입해야 하는 단계를 최소화

### D-004 채널별 독립 운영
- economy, health, history 각 채널은 독립적 토큰, 대본, 키워드, 배경 프리셋 보유
- 채널 간 스톡 영상/키워드 혼용 금지
- 각 채널의 YouTube 계정이 다르므로 OAuth 토큰도 별도 관리

### D-005 보안 절대 규칙
- .env, config/youtube_token_*.json, venv/ 커밋 금지
- API 키 노출 시 즉시 교체
- Cloudflare DNS-only 전환은 OAuth 시에만, 완료 후 즉시 Proxied 복원
- 서버 IP(114.207.244.86) 외부 노출 최소화

### D-006 비공개 우선 정책
- 모든 업로드는 private으로 시작
- CEO가 YouTube Studio에서 직접 확인 후 공개 전환 승인
- 자동 공개 전환 로직은 CEO 승인 후에만 활성화

### D-007 문서화 의무
- 모든 작업 완료 시 보고서 작성 + GitHub push + HTTP 200 확인
- HANDOVER.md 업데이트 필수 (미수행 시 작업 미완료)
- 보고서는 docs/reports/{YYYYMMDD}_{제목}.md 형식

---

## 2. 기술적 지시

### T-001 영상 파이프라인 (v4 확정)
- 대본: Gemini 2.5 Flash (model ID: gemini-2.5-flash, 폴백: Claude → GPT)
  - 주의: gemini-2.0-flash 사용 금지 (2026-02 기준 신규 사용 불가 404)
  - 최신 모델 참고: Gemini 3 Flash(최신), 2.5 Pro(고급), 2.5 Flash-Lite(저비용)
- TTS: Edge-TTS (폴백: Google Cloud TTS)
  - 향후 검토: Gemini 2.5 Pro TTS Preview (고품질 음성 합성)
- 배경: Pexels 스톡 영상 (채널별 프리셋 7키워드, 세그먼트별 순환)
  - 폴백: 채널별 그라데이션 배경 (economy #1a237e→#0d47a1, health #1b5e20→#2e7d32)
- 합성: FFmpeg (1080x1920, H.264, AAC, 29.97fps, ≤60s)
- 자막: 하단 20% (y=h*0.75), 반투명 검정 박스, 40px 흰색, 테두리 2px 검정
- 업로드: YouTube Data API v3 (private)
- 캐시: cache/stock_videos/{channel}_{keyword}.mp4

### T-002 채널 설정
| 채널 | 계정 | Channel ID | 토큰 | 크론 |
|------|------|------------|------|------|
| 3분경제 | oby240610@gmail.com | UC1qhhy2MDsF4vorlma6-dQ | youtube_token_economy.json | 09:00/13:00/18:00 |
| 건강한입 | moongo76@gmail.com | UCKRf4X2fOwhTGcKSVO8rLYQ | youtube_token_health.json | 09:10/13:10/18:10 |
| 역사5분 | (미정) | (미정) | youtube_token_history.json | (미정) |

### T-003 키워드 프리셋
- economy: us dollar bills close up, stock market trading screen, financial chart graph, korean won currency, wall street new york, gold bars investment, bank vault money
- health: fresh fruits vegetables table, healthy meal preparation, fitness exercise workout, vitamin supplement pills, green salad bowl, morning yoga meditation, organic food market
- history: (미정 — 채널 확정 후 설정)

### T-004 서버 환경
- OS: Ubuntu 20.04 Focal
- Python: 3.9.5 (venv, 2026-02-27 교체 완료)
- Python 3.11 미지원 (Focal 한계) → 필요 시 OS 업그레이드 또는 pyenv
- Gemini SDK: google-generativeai (Python 3.9 호환 확인)
- Git: /usr/bin/git commit 사용 (wrapper alias 오류 회피)

### T-005 로드맵
1. Phase 5 (현재): v4 전편 합성 + 업로드, gemini-2.0-flash 잔존 코드 정리
2. Phase 6: v4 cron 교체, 기존 테스트 영상 삭제, 모니터링 알림 연동
3. Phase 7: history 채널 토큰 발급 + 파일럿
4. Phase 8: 비공개→공개 전환 로직, 일일 모니터링 리포트 자동화
5. Phase 9: CLOVA/Gemini TTS 3중 엔진, AI 이미지 배경 추가
6. Phase 10: 추가 채널 확대, StyleFlow 재개, 수익 트래킹

### T-006 API 한도 관리
- YouTube Data API: 10,000 units/day
- 업로드 1건 = 1,600 units
- 2채널 × 3회/일 = 9,600 units (96%)
- 3채널 시 14,400 units 필요 → 한도 상향 신청 또는 업로드 횟수 조정

---

## 3. 절대 규칙 (위반 시 작업 무효)
- .env, youtube_token_*.json, venv/ 커밋 금지
- YouTube 업로드는 반드시 private (CEO 승인 전)
- gemini-2.0-flash 모델 ID 사용 금지 (404 에러, gemini-2.5-flash 사용)
- 서버 Docker 컨테이너 임의 삭제 금지
- 원본 DB 테이블 직접 수정 금지
- 작업 완료 시 HANDOVER.md 업데이트 필수
- 보고서 GitHub push + HTTP 200 확인 필수
- /usr/bin/git commit 사용 (alias wrapper 오류 회피)

---

## 4. 버전 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| v1.0 | 2026-02-28 | 초판 – D-001~D-007, T-001~T-006, 절대 규칙 |
