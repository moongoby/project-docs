# ShortFlow / StyleFlow 프로젝트 컨텍스트
> 최종 갱신: 2026-02-24 (Phase 4 진행 중)

## 프로젝트 개요
- **ShortFlow v3.0**: 쿠팡 파트너스 × YouTube Shorts 자동화 SaaS (B2C)
- **StyleFlow v1.0**: 쇼핑몰 원본사진 → 릴스 자동 생성 B2B SaaS
- **운영 주체**: 뉴톡 (대표님)
- **자체 채널**: korea walker (UCqpf3lJQio6EBHxthLQob0g) + moongoby (UC9fJiBkP9yYq4taKOXqFvsg)

## 인프라
- **114서버**: [SERVER-HOSTNAME] (루트 76%, 197GB 여유)
- **프로젝트 경로**: /data/shortflow → 심볼릭 링크 → goodscode 11TB 서브디스크
- **StyleFlow 경로**: /data/styleflow → 심볼릭 링크 → goodscode
- **NAS**: Synology DSM 7.2.1, 내부 [NAS-IP], 외부 [NAS-PUBLIC-IP], SSH 2222
- **DB**: MySQL autoda (상품 77,122건, goods 테이블)
- **Supabase**: Auth + DB (profiles, coupang_credentials 등)
- **GitHub**: https://github.com/moongoby/shortflow (private, SSH)
- **GitHub Docs**: https://github.com/moongoby/project-docs (public)
- **YouTube**: korea walker 6구독/22영상, moongoby 0/0
- **대시보드**: https://shotflow.newtalk.kr (Apache ProxyPass → Next.js :3000)
- **venv**: /data/shortflow/venv
- **NAS 동기화**: tar over SSH → /data/styleflow/raw/
- **crontab**: NAS 매30분, convert 매10/40분, upload 09/13/18시

## 기술 스택
- Python 3.11, FastAPI, Next.js 14 (대시보드)
- MySQL, Supabase (Auth + PostgreSQL)
- YouTube Data API v3 (일일 10,000 units, 업로드당 1,600, 최대 6건/일)
- TTS: Google Cloud TTS + Edge-TTS (CLOVA Voice 연동 예정)
- LLM: Gemini 2.0 Flash (1순위) + OpenAI + Anthropic 폴백
- FFmpeg, Docker, crontab
- Cloudflare (DNS + SSL Flexible)

## 완료 항목 (Phase 1~3)
- [x] 서브디스크 이관 + 심볼릭 링크 (루트 100%→76%)
- [x] Sprint 1: 10-Layer 양산형 회피 엔진 (16 스텝, 통합테스트 통과)
- [x] 기획서 3종, 문서 버전관리, GitHub push, .cursorrules Work Rules
- [x] Phase 2-1~2-5: .env 보안, YouTube OAuth, crontab, NAS 동기화, MOV→MP4
- [x] Phase 3-1~3-5: 템플릿 엔진, 업로드 워커, 쿠팡 약관, E2E 영상, 실운영
- [x] 업로드워커 오리지널리티 self_channel 모드
- [x] DB 스키마 문서화 (226 테이블)
- [x] 통신판매업 신고 완료 (2026-02-23)

## 완료 항목 (2026-02-24)
- [x] shotflow.newtalk.kr 외부 접속 (Apache VHost 443 충돌 해결)
- [x] Supabase 리다이렉트 URL 등록
- [x] 사업 기획서 10개 모델 (BUSINESS_ROADMAP.md v1.0)
- [x] 멀티채널 기획서 12채널 (YOUTUBE_MULTICHANNEL_PLAN.md v1.0)
- [x] 멀티채널 3채널 셋업 (economy/health/history JSON + 스크립트)
- [x] 인수인계서 v3.0
- [x] Supabase Auth 회원가입/로그인 연동 (/login, /register 페이지)
- [x] LLM 대본 생성 엔진 v2.0 (Anthropic/OpenAI 이중)
- [x] .env에 GEMINI_API_KEY 추가 완료

## 진행 중 (2026-02-24)
- [ ] LLM 엔진 v3.0 Gemini 전환 + API 호출 테스트
- [ ] 미들웨어 /terms, /privacy 경로 예외 수정
- [ ] 이용약관 + 개인정보처리방침 페이지
- [ ] CLOVA Voice TTS 3중 엔진 연동 (네이버 클라우드 발급 대기)
- [ ] profiles SQL 실행 확인 (대표님)

## 다음 작업 (우선순위)
1. CLOVA Voice 발급 + TTS 3중 엔진
2. YouTube 브랜드 채널 생성 (경제·건강·역사)
3. 파일럿 영상 각 채널 3편 제작
4. 업로드 스케줄러(cron) 콘텐츠 채널용
5. 1주일 업로드 모니터링 시스템
6. SaaS 대시보드 LogoutButton 삽입 + 프로필 페이지

## 채널 구조
- **쇼핑군 (계정A)**: 시크블랙, 린다샵, 단하루, 로그데이
- **콘텐츠군 (계정B)**: 3분경제, 건강한입, 역사5분 (Phase 1) + 운동·꿀팁·유머 (Phase 2)

## 핵심 파일 경로
- 기획·아키텍처·인계: docs/plans/, docs/handover/
- 엔진: engine/(12개+), templates/script_archetypes/(7개)
- 채널설정: channels/{economy,health,history,sikblack,...}.json
- 대본생성: scripts/generate_content_script.py, engine/llm_script_engine.py
- 설정: .cursorrules, .env, .gitignore
- 대시보드: dashboard/src/app/

## 가격 정책
- ShortFlow: 29k/59k/99k원 · StyleFlow: 0/149k/349k/690k원

## 핵심 기술 상수
- ORIGINALITY_THRESHOLD=70
- CROSS_VIDEO_SIMILARITY_THRESHOLD=0.85
- UPLOAD_OFFSET_MINUTES=30
- YOUTUBE_DAILY_LIMIT=12
- 영상 규격: 1080x1920, H.264, AAC, 29.97fps, ≤60초

## 지시서 작성규칙

```
>>>DIRECTIVE_START
Task ID: T-NNN
제목: (한글 제목)
서버: 114 (shortflow)
우선순위: P0-CRITICAL / P1-HIGH / P2-NORMAL
예상 시간: N분
예상 비용: $0
의존성: (없음 또는 선행 Task ID)

(작업 내용 상세 기술)
>>>DIRECTIVE_END
```

- 타임스탬프: KST 기준 (UTC 금지)
- 작업 완료 후 HANDOVER.md 반드시 갱신
- git commit + push 필수
