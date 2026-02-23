# ShortFlow / StyleFlow 프로젝트 컨텍스트
> 최종 갱신: 2026-02-23 (Phase 3 완료)

## 프로젝트 개요
- **ShortFlow v3.0**: 쿠팡 파트너스 × YouTube Shorts 자동화 SaaS (B2C)
- **StyleFlow v1.0**: 쇼핑몰 원본사진 → 릴스 자동 생성 B2B SaaS
- **운영 주체**: 뉴톡 (대표님)
- **자체 채널**: korea walker (UCqpf3lJQio6EBHxthLQob0g) + moongoby (UC9fJiBkP9yYq4taKOXqFvsg)

## 인프라
- **114서버**: rfree-0009.cafe24.com (루트 76%, 201GB 여유)
- **프로젝트 경로**: /data/shortflow → 심볼릭 링크 → goodscode 11TB 서브디스크
- **StyleFlow 경로**: /data/styleflow → 심볼릭 링크 → goodscode
- **NAS**: Synology DSM 7.2.1, 내부 192.168.30.23, 외부 183.96.69.193, SSH 2222
- **DB**: MySQL autoda (상품 77,111건, goods 테이블)
- **GitHub**: https://github.com/moongoby/shortflow (private, SSH 인증)
- **GitHub 문서 폴더**: https://github.com/moongoby/shortflow/tree/main/docs
- **YouTube**: korea walker 6구독/22영상, moongoby 0/0
- **venv**: /data/shortflow/venv (Py3.8.10)
- **NAS 동기화**: tar over SSH → /data/styleflow/raw/
- **crontab**: NAS 매30분, convert 매10/40분, upload 09/13/18시

## 기술 스택
- Python 3.11, FastAPI, Next.js (대시보드)
- MySQL, Supabase
- YouTube Data API v3 (일일 10,000 units, 업로드당 1,600, 최대 6건/일)
- TTS, LLM (Claude/GPT), FFmpeg
- Docker, crontab

## 완료 항목
- [x] 서브디스크 이관 + 심볼릭 링크 (루트 100%→76%)
- [x] Sprint 1: 10-Layer 양산형 회피 엔진 (16 스텝 완료, 통합테스트 통과)
- [x] 기획서 3종, 문서 버전관리, GitHub push, .cursorrules Work Rules, 경쟁사·YouTube 정책
- [x] Phase 2-1: .env 보안강화 (.gitignore, .env.example, credentials 정리)
- [x] Phase 2-2: YouTube OAuth2.0 (2채널 토큰·채널 확인·업로드 테스트)
- [x] Phase 2-3: crontab 업로드 스케줄러 (09/13/18시 KST, ±30분, 일일 6건)
- [x] Phase 2-4: NAS→114 동기화 (tar over SSH, 268파일 수신)
- [x] 멀티채널(korea_walker+moongoby), venv·Google API, project-docs(ONBOARDING·7종)
- [x] Phase 2-5: MOV→MP4 변환 서비스 (394 MOV, crontab 10/40분)
- [x] Phase 3-1: 템플릿 엔진 점검 + DB E2E 드라이런 (46e18f8)
- [x] Phase 3-2: 업로드 워커 파이프라인 연동 (5e7a030)
- [x] Phase 3-3: 쿠팡 약관 + ffprobe 검수 (a509ea1)
- [x] Phase 3-4: 실제 영상 생성 E2E – FFmpeg+TTS 1건 (완료)
- [x] Phase 3-5: 업로드 워커 crontab 실운영 활성화 (완료)
- [x] 업로드워커 오리지널리티 self_channel 모드 (8e273a0)
- [x] 쿠팡 파트너스 약관 가이드 (47d00a1)
- [x] DB 스키마 문서화 (완료)

## 진행 중
- Phase 3 완료

## 다음 작업 (우선순위)
1. 쿠팡 파트너스 키 발급 + 상품 링크 Description 자동 삽입
2. 통신판매업 신고
3. 업로드 모니터링 1주일 관찰
4. Python 3.10+ 업그레이드 검토
5. SaaS 대시보드 MVP (Next.js)

## 핵심 파일 경로
- 기획·아키텍처·인계: docs/plans/, docs/architecture/, docs/handover/
- 엔진: engine/(12개), templates/script_archetypes/(7개)
- 설정: .cursorrules, .env, .gitignore

## 가격 정책
- ShortFlow: 29k/59k/99k원 · StyleFlow: 0/149k/349k/690k원 · 매출목표 월 약 3,387만원

## 핵심 기술 상수
- ORIGINALITY_THRESHOLD=70
- CROSS_VIDEO_SIMILARITY_THRESHOLD=0.85
- UPLOAD_OFFSET_MINUTES=30
- YOUTUBE_DAILY_LIMIT=12
- 영상 규격: 1080x1920, H.264, AAC, 29.97fps, ≤60초
