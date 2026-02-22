# ShortFlow / StyleFlow 프로젝트 컨텍스트
> 최종 갱신: 2026-02-23 22:00 KST

## 프로젝트 개요
- **ShortFlow v3.0**: 쿠팡 파트너스 × YouTube Shorts 자동화 SaaS (B2C)
- **StyleFlow v1.0**: 쇼핑몰 원본사진 → 릴스 자동 생성 B2B SaaS
- **운영 주체**: 뉴톡 (대표님)
- **자체 채널**: 템빨신상맨 (YouTube)

## 인프라
- **114서버**: rfree-0009.cafe24.com (루트 76%, 201GB 여유)
- **프로젝트 경로**: /data/shortflow → 심볼릭 링크 → goodscode 11TB 서브디스크
- **StyleFlow 경로**: /data/styleflow → 심볼릭 링크 → goodscode
- **NAS**: Synology DSM 7.2.1, 내부 192.168.30.23, 외부 183.96.69.193, SSH 2222
- **DB**: MySQL autoda (상품 77,109건, goods 테이블)
- **GitHub**: https://github.com/moongoby/shortflow (private, SSH 인증)

## 기술 스택
- Python 3.11, FastAPI, Next.js (대시보드)
- MySQL, Supabase
- YouTube Data API v3 (일일 10,000 units, 업로드당 1,600, 최대 6건/일)
- TTS, LLM (Claude/GPT), FFmpeg
- Docker, crontab

## 완료 항목
- [x] 서브디스크 이관 + 심볼릭 링크 (루트 100%→76%)
- [x] Sprint 1: 10-Layer 양산형 회피 엔진 (16 스텝 전부 완료, 통합테스트 통과)
  - Layer 1 Visual / 2 Script / 3 Voice / 4 BGM / 5 Metadata / 6 Upload Pattern
  - Layer 7 Originality Score / 8 Narrative Injection / 9 Structural Variation / 10 Cross-Video Checker
  - Collision Avoidance, Style Seed, 오케스트레이터
- [x] 기획서 3종 저장 (shortflow_v3.0_plan.md, styleflow_v1.0_plan.md, .cursorrules)
- [x] 문서 버전관리 체계 (docs 디렉토리 구조화, git init)
- [x] GitHub 저장소 생성 및 push (412 objects, 5 commits)
- [x] .cursorrules Work Rules 반영 (백업/보고서/커밋/배포/디스크/GitHub/컨텍스트/인계)
- [x] 경쟁사 분석: Reelbox, FastCut, AutoPanda 요금·기능 조사 완료
- [x] YouTube 정책 확인: Inauthentic Content 기준 반영

## 진행 중
- (없음 — 다음 작업 대기)

## 다음 작업 (우선순위)
1. .env 실제 값 세팅 + 보안 확인 (.gitignore 제외 재확인)
2. YouTube OAuth2.0 설정 + 채널 소유 확인 + 토큰 발급 테스트
3. crontab 업로드 스케줄러 등록 (09:00/13:00/18:00 KST ±30분)
4. NAS ↔ 114서버 동기화 파이프라인 (rsync/sftp)
5. MOV → MP4 변환 서비스 구현
6. 5개 템플릿 릴스 엔진 운영 점검 (DB 연동, 상품 자동 매칭)
7. 쿠팡 파트너스 약관 검증 (SaaS 링크 생성·배포 허용 여부, Phase 3 전 필수)
8. 통신판매업 신고

## 핵심 파일 경로
- 기획서: docs/plans/shortflow_v3.0_plan.md, styleflow_v1.0_plan.md
- 아키텍처: docs/architecture/system_architecture_v1.0.md
- 인수인계: docs/handover/handover_v2.0.md
- 인계 템플릿: docs/handover/HANDOVER_TEMPLATE.md
- 엔진 오케스트레이터: engine/anti_inauthentic.py
- 엔진 모듈: engine/ (12개 파일)
- 템플릿: templates/script_archetypes/ (7개), structural_patterns/ (4개), visual_components.json
- 설정: .cursorrules, .env, .gitignore

## 가격 정책
- **ShortFlow**: Starter 29,000원/90영상, Growth 59,000원/200영상, Pro 99,000원/500영상
- **StyleFlow**: Trial 0원/14일, Starter 149,000원/100영상, Growth 349,000원/300영상, Enterprise 690,000원/1,000영상
- **매출 목표**: ShortFlow 월 16,420,000원 + StyleFlow 월 17,450,000원 = 총 월 33,870,000원

## 핵심 기술 상수
- ORIGINALITY_THRESHOLD=70
- CROSS_VIDEO_SIMILARITY_THRESHOLD=0.85
- UPLOAD_OFFSET_MINUTES=30
- YOUTUBE_DAILY_LIMIT=6
- 영상 규격: 1080x1920, H.264, AAC, 29.97fps, ≤60초
