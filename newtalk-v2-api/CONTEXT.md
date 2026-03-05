# 뉴톡 V2 — 프로젝트 컨텍스트

**문서 버전**: v5.0.0
**최종 갱신**: 2026-03-05

---

## 1. 프로젝트 개요

- **V2 목표**: V1(CodeIgniter 2.x/PHP 5.4)을 Laravel 12 + Next.js 16으로 재구축, SNS형 B2B SaaS 마켓플레이스로 진화.
- **GitHub**: https://github.com/moongoby/newtalk-v2-api- (끝 하이픈 주의)
- **V1**: 114.207.244.86 (운영), 114.207.244.87 (어드민) — 수정 금지.

---

## 2. 인프라

- **서버**: rfree-009, Ubuntu 20.04, IP 114.207.244.86 (V2), 114.207.244.87 (V1 어드민)
- **SSH**: `ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86`
- **Docker**: Docker 28.1.1, Compose v2.35.1. 프로젝트 경로: `/srv/newtalk-v2` (또는 워크스페이스 `/root/newtalk-v2`)
- **NAS**: Synology DS1821+, 192.168.30.23, image-auto :8100

---

## 3. 기술 스택

- **백엔드**: Laravel 12, PHP 8.3-FPM, Sanctum, Spatie Permission (RBAC 6역할)
- **DB**: MySQL 8.0 (:3307), Redis 7 (:6380)
- **프론트**: Next.js 16 (Node 20), App Router, shadcn/ui
- **API 게이트웨이**: Nginx 1.25-alpine (:8080)

---

## 4. V2 서비스 아키텍처 8레이어

1. SNS 소셜 엔진 (피드, 탐색, 스토리, 쇼츠, DM, 팔로우·찜)
2. 도매 SaaS 브랜드 인프라 (브랜드 페이지, 소매 회원가입·승인, AI 콘텐츠, 주문·배송·대시보드)
3. 소매 커머스 허브 (피드→사입→내 쇼핑몰 원클릭등록→위탁배송)
4. 마켓플레이스 거래 엔진 (오픈 3~5%, 직거래 1~2%, 정산)
5. AI 인텔리전스 (트렌드·사입추천·자동콘텐츠·맞춤피드)
6. 확장 (일본 크로스보더, 라이브 B2B)
7. 셀러 확장 엔진 (카페24·네이버·쿠팡 자동등록, 인스타·틱톡·유튜브 SNS 연동, 자동 마케팅)
8. 콘텐츠 팩토리 (스튜디오+AI 생성 엔진, NAS 연동)

---

## 5. 수익 모델

- SaaS 월정액 44만~165만원, 거래 수수료 3~5% / 직거래 1~2%, 콘텐츠 건당 2,000원
- 위탁배송 수수료, 셀러 도구(SNS 자동게시 초과 건당 500원), 스폰서드 카드, 데이터 서비스
- 콘텐츠 스튜디오: 베이직(무료/10만) → 프로(44만) → 프리미엄(110~165만)

---

## 6. 완료 항목 (64건)

### R0 ~ R1
- [x] R0: 프로젝트 초기화 (Laravel 12, Docker, MySQL, Redis) — v0.1.0, 2026-02-21
- [x] R1: 백엔드 API (Sanctum, RBAC 6역할, 사입 API, 47+ 테이블) — v1.0.0, 2026-02-22

### R2 (프론트엔드 + API 기반)
- [x] R2-FRONT-001: Next.js 16 셋업 — ce541c5, v1.1.0, 2026-02-23
- [x] R2-FRONT-001-DEPLOY: 프론트엔드 Docker 배포 — 870c007, v1.2.0, 2026-02-23
- [x] R2-API-001: SNS 소셜 엔진 API — 520353b, v1.3.0, 2026-02-23
- [x] R2-FRONT-002: 홈 피드 + 탐색 UI — 520353b, v1.4.0, 2026-02-23
- [x] R2-FIX-001: 검수 피드백 반영 — v1.4.1, 2026-02-24
- [x] R2-FRONT-003: 상품 상세·찜·공유 UI — 520353b, v1.5.0, 2026-02-24
- [x] R2-API-002: 브랜드 페이지 API — 520353b, v1.6.0, 2026-02-24
- [x] R2-FRONT-004: 브랜드 페이지 UI — 520353b, v1.6.0, 2026-02-24
- [x] R2-FIX-002: 코드 검수 피드백 — 520353b, v1.6.1, 2026-02-24
- [x] R2-FRONT-005: 관리자 구매 대시보드 상세 — v1.7.0, 2026-02-24
- [x] R2-FRONT-006: 도매 콘텐츠 업로드 UI — 520353b, v1.8.0, 2026-02-24
- [x] R2-API-003: AI 콘텐츠 처리 API — 520353b, v1.9.0, 2026-02-25
- [x] R2-API-004: 카페24 API 연동 — 520353b, v2.0.0, 2026-02-25

### R3 (마켓플레이스 + 결제 + 배송 + DM + 쇼츠 + 정산)
- [x] R3-API-001: 사입 주문 API (장바구니 + 주문) — 87cb07b, v2.1.0, 2026-02-25
- [x] R3-FRONT-001: 사입 주문·장바구니 UI — b798049, v2.2.0, 2026-02-25
- [x] R3-API-002: 결제 연동 API (토스페이먼츠) — b798049, v2.3.0, 2026-02-25
- [x] R3-FRONT-002: 결제 UI — b798049, v2.4.0, 2026-02-25
- [x] R3-API-003: 배송 API — b798049, v2.5.0, 2026-02-25
- [x] R3-FRONT-003: 배송 UI — b798049, v2.6.0, 2026-02-25
- [x] R3-API-004: DM API — b798049, v2.7.0, 2026-02-26
- [x] R3-FRONT-004: DM UI — v2.8.0, 2026-02-26
- [x] R3-API-005: Shorts API — v2.9.0, 2026-02-26
- [x] R3-FRONT-005: Shorts UI — v2.10.0, 2026-02-26
- [x] R3-API-006: 정산 API — v2.11.0, 2026-02-26
- [x] R3-FRONT-006: 정산 UI — v2.12.0, 2026-02-26

### R4 (거래처 + 스토리 + AI + 셀러 + 콘텐츠 + SNS + 위탁배송)
- [x] R4-API-001: 거래처 제도 API — v3.1.0, 2026-02-26
- [x] R4-API-002: 스토리 API — v3.2.0, 2026-02-26
- [x] R4-API-003: AI 맞춤 피드 + 추천 엔진 — v3.3.0, 2026-02-26
- [x] R4-API-004: 셀러 채널 관리 API — v3.4.0, 2026-02-26
- [x] R4-API-005: 콘텐츠 파이프라인 API — v3.5.0, 2026-02-26
- [x] R4-FRONT-006: 콘텐츠 파이프라인 UI — v3.14.0, 2026-02-26
- [x] R4-FRONT-001: 거래처 제도 UI — v3.6.0, 2026-02-26
- [x] R4-FRONT-002: 스토리 UI — v3.7.0, 2026-02-26
- [x] R4-FRONT-003: AI 추천 피드 UI + 소매 마이페이지 — v3.8.0, 2026-02-26
- [x] R4-API-006: SNS 자동 게시 API — v3.9.0, 2026-02-26
- [x] R4-API-007: 위탁배송 고도화 + 드롭십 API — v3.10.0, 2026-02-26
- [x] DOCS-FIX-007: SHA 교체 + ARCHITECTURE 재작성 — 2026-02-26
- [x] R4-FRONT-004: 셀러 채널 관리 UI — v3.12.0, 2026-02-26
- [x] R4-FRONT-005: SNS 자동 게시 UI — v3.13.0, 2026-02-26
- [x] R4-FRONT-007: 위탁배송·드롭십 UI — v3.15.0, 2026-02-26

### 문서 수정
- [x] DOCS-FIX-008: 4대 핵심 문서 정합성 복구 (이 작업) — v3.11.0, 2026-02-26
- [x] DOCS-FIX-009: R4 최종 문서 정합성 복구 — v3.15.0, 2026-02-27
- [x] R4 라운드 종결 (API 7 + FRONT 7) — 2026-02-27
- [x] DOCS-SETUP-001: CEO-DIRECTIVES.md 생성 + HANDOVER.md 표준 8섹션 전환 — v4.0.0, 2026-02-28

### R5 (Phase A~B)
- [x] R5-PLAN-DRAFT-001: R5 Phase B 기획 초안 + V1 이미지 경로 조사 — 98050a7, 2026-03-01
- [x] R5-B2-MIGRATE-001: 결제+배송+정산+쇼츠 12테이블 마이그레이션 — 55c73b4, v4.4.0, 2026-03-01
- [x] ROUTE-CONNECT-B1-001: B-1 라우트 연결 35EP, 총 142라우트 — f39ef28, v4.3.0, 2026-03-02
- [x] ROUTE-CONNECT-B2-001: 결제+배송+정산+쇼츠 라우트 연결 36EP — 26ee445, v4.5.0, 2026-03-02
- [x] R5-B3-001: 거래처+스토리+AI추천+셀러채널 10테이블 + 25EP 라우트 — 8013204, v4.6.0, 2026-03-03
- [x] INTEGRATION-CHECK-001: 203라우트 전수 통합 검수 + 빈 모델 2개 fillable 수정 — a3eeb96, 2026-03-04
- [x] API-TEST-001: 스모크+Feature Test 완료 — 8c4b0e1, 2026-03-04
- [x] CODE-REVIEW-001: R1~R4 코드 검수 완료 (203라우트, 97테이블) — 2026-03-04

### 운영 + 데이터
- [x] V1-HOTFIX-001: V1 이미지 캐시 버스팅 + GoodsEtc73 즉시 반영 — 9463cfa, 2026-03-04
- [x] SEEDER-001: 시더 8개 (UserSeeder·CategorySeeder·ProductSeeder·OrderSeeder·PurchaseOrderSeeder·ShortSeeder·SettlementSeeder·PartnershipSeeder), users=17, products=46 — da42612, v4.9.0, 2026-03-05
- [x] V1-HOTFIX-002: V1 이미지 동일 파일명 덮어쓰기 수정 (3파일, 3버그) — 0f1de87, 2026-03-05
- [x] NTV2-VERIFY-001: 500 에러 7/7 해소 HTTP 재확인, DropshipService·FulfillmentService·ContentPipelineService 구현 — 0f1de87, v4.8.0, 2026-03-05
- [x] DOCS-SYNC-003: HANDOVER v5.0 + CEO-DIRECTIVES v1.1 정합성 복구 — v4.9.0, 2026-03-05

### R5 프론트엔드 + API
- [x] R5-FRONT-SETTLE-001: 정산 프론트엔드 전체 구현 (settlement-api.ts 6함수, wholesale/admin 페이지 4개, 컴포넌트 5개, 레이아웃 2곳, 빌드 에러 0, API 200) — 5a1390b, v5.1.0, 2026-03-05
- [x] R5-FRONT-PIPELINE-001: 콘텐츠 파이프라인 관리자 UI (파이프라인 목록·상세·생성 3페이지+6컴포넌트) — 8c63353, v5.2.0, 2026-03-05
- [x] R5-API-HEALTH-001: GET /api/health 200, DB/Redis/Disk 모니터링 엔드포인트 추가 — d58a3fd, v5.2.0, 2026-03-05

### 감사 + 스모크 테스트
- [x] FRONTEND-AUDIT-001: 프론트엔드 전수 감사 (412 ts/tsx, 78 page.tsx, 12영역 100% 매핑) — 0ddc519, 2026-03-05
- [x] API-SMOKE-002: 스모크 재테스트 (6계정 로그인 성공, 500에러 0, products=46/orders=2/shorts=10/settlements=5) — f793574, 2026-03-05

---

## 7. 진행 중

(없음)

---

## 8. 다음 작업

- admin 상품 CRUD (관리자 상품 등록·수정·삭제 UI)
- 드롭십 개선 (위탁배송 드롭십 프로세스 고도화)
- R4-FRONT-005/006/007 재검토 (SNS 자동게시·콘텐츠파이프라인·드롭십 UI 기능 보완)
- R5 기획 확정 대기 (일본 크로스보더, 라이브 B2B)

---

## 9. 로드맵

- R2 완료 (프론트 셋업, 인증, 피드, 상품 상세, 브랜드, 콘텐츠, 카페24)
- R3 완료 (사입 주문, 결제, 배송, DM, 쇼츠, 정산)
- R4 **완료** (거래처, 스토리, AI 추천, 셀러 채널, 콘텐츠 파이프라인, SNS 자동게시, 위탁배송·드롭십 — API 7건 + FRONT 7건)
- R5 대기 (일본 크로스보더, 라이브 B2B)

---

## 10. 핵심 파일 경로

```
docs/CONTEXT.md, docs/CHANGELOG.md
docs/architecture/NT-V2-ARCHITECTURE.md
docs/handover/HANDOVER.md
docs/reports/*.md
frontend/ (Next.js 16)
routes/api.php, app/Http/Controllers/
```

---

## 11. 테스트 계정

비밀번호는 `.env` 또는 `.env.docker` 참조 (인계서·문서에 평문 기록 금지).

- admin@newtalk.kr (관리자)
- md@newtalk.kr (MD)
- purchaser@newtalk.kr (사입자)
- wholesale@newtalk.kr (도매)
- retail@newtalk.kr (소매)
- outsource@newtalk.kr (외주)

---

## 12. 절대 준수 규칙

- V1 소스·DB 수정 금지 (V1 읽기 전용)
- .env.docker, 비밀번호 등 민감정보 Git 커밋 금지
- 파일 수정 전 백업: `.bak.{YYYYMMDD_HHMMSS}`

---

## 13. 커서 필수 규칙

- 커밋 접두사: `[R{라운드}-{TASK}]` 또는 `[DOCS]`
- 코드 변경 시 테스트·린트 확인 후 커밋
