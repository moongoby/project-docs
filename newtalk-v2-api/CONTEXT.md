# NewTalk V2 프로젝트 컨텍스트
> 최종 갱신: 2026-02-23

## 프로젝트 개요
- **NewTalk V2**: 동대문 패션 도매-소매 B2B "SNS형 SaaS 마켓플레이스" 플랫폼
- **운영 주체**: 뉴톡 (대표님)
- **V1 현황**: 콘텐츠 중개 플랫폼 (도매 상품 사진·영상 → 소매 제공, 건당 2,000원), SaaS 월정액 44만~165만원
- **V2 목표**: SNS(피드·스토리·DM·쇼츠) + SaaS(브랜드몰·AI콘텐츠·주문·배송·분석) + 마켓플레이스(오픈·직거래) 통합
- **GitHub**: https://github.com/moongoby/newtalk-v2-api- (private, 끝에 하이픈 주의)
- **V1 사이트**: https://newtalk.kr

## 인프라
- **서버 IP**: 114.207.244.86
- **SSH**: ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86
- **프로젝트 경로**: /srv/newtalk-v2/
- **Docker 서비스**: app(Laravel, 8080), nginx(V1, 80), db(MySQL 8, 3306), redis(6379), frontend(Next.js, 3000)
- **NAS**: Synology, 내부 192.168.30.23, 외부 183.96.69.193

## 기술 스택
- Backend: Laravel 12 (PHP 8.3), Sanctum 인증, Spatie Permission (6역할: super_admin, admin, wholesale, retail, md, purchaser)
- Frontend: Next.js 16, TypeScript, Tailwind CSS, shadcn/ui, Zustand, TanStack Query
- DB: MySQL 8 (47+ 테이블 마이그레이션 완료)
- Cache: Redis 7
- Infra: Docker Compose, Nginx
- AI: 향후 AI 콘텐츠 생성, 추천 엔진

## V2 서비스 아키텍처 8레이어
1. SNS 소셜 엔진 — 홈 피드, 탐색, 스토리, 쇼츠, DM, 팔로우·찜
2. 도매 SaaS 브랜드 인프라 — 브랜드 페이지, 소매 회원가입·승인, AI 자동 콘텐츠, 주문·배송·대시보드
3. 소매 커머스 허브 — 피드→사입주문→내 쇼핑몰 원클릭등록→위탁배송
4. 마켓플레이스 거래 엔진 — 오픈(수수료 3~5%), 직거래(1~2%), 정산
5. AI 인텔리전스 — 트렌드·사입추천·자동콘텐츠·맞춤피드
6. 확장 — 일본 크로스보더, 라이브 B2B
7. 셀러 확장 엔진 — 다채널 자동등록(카페24·네이버·쿠팡), SNS 연동(인스타·틱톡·유튜브), 자동 마케팅
8. 콘텐츠 팩토리 — 스튜디오 + AI 생성 엔진, NAS 연동

## 수익 모델
- SaaS 월정액: 44만~165만원 (프로·프리미엄)
- 거래 수수료: 오픈 3~5%, 직거래 1~2%
- 콘텐츠 과금: 건당 2,000원
- 위탁배송 수수료
- 셀러 도구: SNS 자동게시 초과 건당 500원, 다채널 등록 수수료
- 콘텐츠 스튜디오: 베이직(무료/월10만) → 프로(44만) → 프리미엄(110~165만)
- 프리미엄 노출(스폰서드 카드), 데이터 서비스

## 완료 항목
- [x] R0: 프로젝트 초기화 — Laravel 12, Docker Compose, MySQL·Redis, Nginx (v0.1.0, 2026-02-21)
- [x] R1: 백엔드 API 기반 — Sanctum 인증, RBAC 6역할, V1 사입 시스템 API, 47+ DB 테이블 (v1.0.0, 2026-02-22)
- [x] R2-FRONT-001: Next.js 16 셋업 — 인증·레이아웃·대시보드·Docker, 커밋 ce541c5 (v1.1.0, 2026-02-23)
- [x] V2 종합 기획서 작성 (NT-V2-PLAN-002-FINAL)
- [x] V2 아키텍처 문서 작성 (NT-V2-ARCHITECTURE)
- [x] 문서 버전관리 체계 구축 (docs 폴더 구조화)
- [x] GitHub 계정 통합 (moongoby 단일 계정)

## 진행 중
- [ ] R2-FRONT-001-DEPLOY: 프론트엔드 Docker 빌드·실행, 외부 접속 확인 (http://114.207.244.86:3000)
- [ ] 문서 버전관리 실제 적용 확인 (docs/ 하위 구조 서버 검증)

## 다음 작업 (우선순위)
1. R2-FRONT-001-DEPLOY 완료 — Docker 빌드, 방화벽, 접속 테스트
2. R2-FRONT-002 홈 피드 UI — 피드 카드, 무한 스크롤, 탐색 탭
3. R2-FRONT-003 상품 상세·찜·공유
4. R2-FRONT-004 브랜드 페이지 — 도매 프로필, 소매 회원가입·승인
5. R2-FRONT-005 도매 대시보드 — 상품 관리, 주문 현황, 콘텐츠 업로드
6. R2-API-001 SNS 엔진 API — 피드, 팔로우, 찜, 검색
7. R2-API-002 브랜드 페이지 API — 스토어 CRUD, 소매 가입·승인
8. R2-FRONT-006 DM 기능
9. R2-FRONT-007 쇼츠 플레이어
10. R3-FRONT-001 장바구니·사입 주문

## 로드맵
- R2 (0~8주): 프론트 셋업, 인증, 홈 피드, 상품 상세·찜, 브랜드 페이지, SNS/브랜드 API
- R3 (8~16주): 사입 주문·결제·위탁배송, 카페24 연동, DM, 쇼츠, 정산
- R4 (16~24주): AI 추천·스토리·라이브·일본 확대·유튜브쇼핑·틱톡·자동 마케팅

## 핵심 파일 경로
- 기획서: docs/planning/NT-V2-PLAN-002-FINAL.md
- 아키텍처: docs/architecture/NT-V2-ARCHITECTURE.md
- 인수인계: docs/handover/HANDOVER.md
- CHANGELOG: docs/CHANGELOG.md
- 보고서: docs/reports/R2-FRONT-001-report.md
- 스크립트: docs/scripts/
- V1 분석: docs/v1-analysis/
- 프론트엔드: frontend/ (Next.js 16)
- 백엔드 API: app/Http/Controllers/Api/
- 라우트: routes/api.php
- Docker: docker-compose.yml, frontend/Dockerfile
- 환경변수: .env, frontend/.env.local (.gitignore 대상)

## 테스트 계정
- 관리자: admin@newtalk.kr / NewTalk2026!@# (super_admin)

## 절대 준수 규칙
1. V1 소스코드·DB 수정 금지 (READ-ONLY)
2. 변경 전 반드시 백업 (.bak.{YYYYMMDD_HHMMSS})
3. Git 커밋 전 민감정보 검사 (password, secret, key, token)
4. .env.local, node_modules/, .next/ 커밋 금지
5. 커밋 접두사: [DOCS], [R2-FRONT-XXX], [R2-API-XXX], [INFRA]
6. Docker 변경 시 기존 서비스 영향도 확인
7. 작업 완료 후 CONTEXT.md 갱신, CHANGELOG 업데이트
8. 대화 종료 시 인계서 작성
9. Git 커밋 후 반드시 push
10. 토큰 80%에서 인계서 작성·새 대화 인계

## 커서(Cursor) 필수 규칙
1. SSH 접속 후 실제 파일 존재 확인 — 추측 금지
2. docker-compose.yml 수정 전 반드시 .bak 백업
3. 프론트 빌드는 Docker 내부에서 실행 (서버 Node.js 미설치 가능)
4. Git 푸시: GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_newtalk -o StrictHostKeyChecking=no" git push origin {브랜치}
5. 작업 완료 후 docs/reports/에 보고서 작성 + CHANGELOG 갱신
6. 문서 수정 시 버전·변경이력 테이블 갱신

## V2 핵심 기능 4가지
1. SNS 요소 도입 — 도매 콘텐츠를 소매가 피드로 보고 팔로우·찜·공유 (피드+스토리+DM+쇼츠)
2. SaaS 모델 — 도매가 브랜드몰 운영·콘텐츠 제작·소매 유치·주문 관리 올인원, 월정액 44만~165만원
3. 소매 직접 구매 — 소매가 뉴톡 내에서 도매 상품 사입 주문, 마켓플레이스 역할
4. 도매몰 내 소매 회원가입 — 도매 브랜드 페이지에 소매 별도 가입, 독립 스토어+통합 계정

## 8레이어 아키텍처
1. SNS 소셜 엔진 (피드, 탐색, 스토리, 쇼츠, DM, 팔로우·찜)
2. 도매 SaaS 브랜드 인프라 (브랜드 페이지, 소매 회원가입·승인, AI 콘텐츠, 주문·배송·대시보드)
3. 소매 커머스 허브 (피드→사입→내 쇼핑몰 원클릭등록→위탁배송)
4. 마켓플레이스 거래 엔진 (오픈 3~5%, 직거래 1~2%, 정산)
5. AI 인텔리전스 (트렌드·사입추천·자동콘텐츠·맞춤피드)
6. 확장 (일본 크로스보더, 라이브 B2B)
7. 셀러 확장 엔진 (카페24·네이버·쿠팡 자동등록, 인스타·틱톡·유튜브 SNS 연동, 자동 마케팅)
8. 콘텐츠 팩토리 (스튜디오+AI 생성 엔진, NAS 연동)

## 수익 모델
- SaaS 월정액 44만~165만원, 거래 수수료 3~5%/1~2%, 콘텐츠 건당 2,000원
- 위탁배송 수수료, 셀러 도구(SNS 자동게시 초과 건당 500원), 스폰서드 카드, 데이터 서비스
- 콘텐츠 스튜디오: 베이직(무료/10만) → 프로(44만) → 프리미엄(110~165만)

## 완료 항목
- [x] R0: 프로젝트 초기화 — Laravel 12, Docker Compose, MySQL·Redis, Nginx (v0.1.0, 2026-02-21)
- [x] R1: 백엔드 API (Sanctum, RBAC 6역할, 사입 API, 47+ 테이블) — v1.0.0, 2026-02-22
- [x] R2-FRONT-001: Next.js 16 셋업 (인증·레이아웃·대시보드·Docker) — ce541c5, v1.1.0, 2026-02-23
- [x] R4-FRONT-001: 거래처 제도 UI — 소매 신청/도매 관리/전용가, 10컴포넌트 6페이지, 브랜드 페이지 "거래처 신청" (v3.6.0, 2026-02-26)

## 진행 중
- [ ] R2-FRONT-001-DEPLOY: Docker 빌드·실행, 외부 접속 확인 (114.207.244.86:3000)

## 다음 작업
1. R2-FRONT-001-DEPLOY 완료
2. R2-FRONT-002 홈 피드 UI
3. R2-FRONT-003 상품 상세·찜·공유
4. R2-FRONT-004 브랜드 페이지
5. R2-API-001 SNS 엔진 API
6. R2-API-002 브랜드 페이지 API

## 로드맵
- R2 (0~8주): 프론트 셋업, 인증, 홈 피드, 상품 상세, 브랜드 페이지, SNS API
- R3 (8~16주): 사입 주문, 결제, 위탁배송, 카페24 연동, DM, 쇼츠, 정산
- R4 (16~24주): AI 추천, 스토리, 라이브, 일본 확대, 유튜브쇼핑, 틱톡, 자동 마케팅
