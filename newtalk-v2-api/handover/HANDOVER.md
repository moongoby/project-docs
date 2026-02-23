# 뉴톡 V2 프로젝트 인수인계서

**버전**: 1.0.0
**최종수정**: 2026-02-23
**목적**: 신규 개발자·AI 에이전트가 프로젝트를 즉시 이해하고 작업할 수 있도록 하는 종합 인계 문서

---

## 변경 이력
| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0.0 | 2026-02-23 | R1 완료 + R2 착수 상태 기준 초판 |
| 1.4.0 | 2026-02-23 | R2-API-001 + R2-FRONT-002 완료 (피드·팔로우·찜 API, 홈 피드·탐색 UI) |

---

## 1. 프로젝트 개요

뉴톡 V2는 V1(CodeIgniter 2.x/PHP 5.4)을 Laravel 12 + Next.js 16으로 재구축하는 프로젝트.
SNS형 B2B SaaS 마켓플레이스로 진화 중.

**핵심 이해관계자**: CEO (moongoby@gmail.com) – 사입 시스템 유일 의사결정자.

---

## 2. 접속 정보

### 서버 (rfree-009)
```
SSH: ssh -p 7916 -i ~/.ssh/id_ed25519_newtalk root@114.207.244.86
OS: Ubuntu 20.04
CPU: AMD EPYC 7262 8-Core
RAM: 16 GB
Disk: 875 GB
IP: 114.207.244.86 (V2), 114.207.244.87 (V1 어드민)
Docker: 28.1.1, Compose v2.35.1
```

### V2 Docker 스택 (/srv/newtalk-v2/)
```
app:      PHP 8.3-FPM (Laravel 12)
nginx:    1.25-alpine → :8080
db:       MySQL 8.0 → :3307
redis:    Redis 7 → :6380
frontend: Next.js 16 → :3000 (R2 추가)
```

### DB 접속
```
V1 (읽기 전용): mysql -u pigupuser -p -h 127.0.0.1 -P 3306 autoda
  비밀번호: /home/danharoo/www/application/config/database.php 참조
V2 (읽기/쓰기): mysql -u newtalk_v2_user -p -h 127.0.0.1 -P 3307 newtalk_v2
  비밀번호: /srv/newtalk-v2/.env.docker 참조
```

### NAS
```
Synology DS1821+, IP 192.168.30.23
image-auto 컨테이너: :8100
```

### Git
```
레포: git@github.com:moongoby/newtalk-v2-api-.git (끝 하이픈 주의)
웹: https://github.com/moongoby/newtalk-v2-api-
```

### URL
```
V2 API: http://114.207.244.86:8080
V2 Frontend: http://114.207.244.86:3000
V1: http://114.207.244.86
```

### 테스트 계정 (비밀번호: [REDACTED])
```
admin@newtalk.kr (관리자)
md@newtalk.kr (MD)
purchaser@newtalk.kr (사입자)
wholesale@newtalk.kr (도매)
retail@newtalk.kr (소매)
outsource@newtalk.kr (외주)
```

---

## 3. 작업 규칙 (필독)

### 3.1 절대 금지
- V1 소스 코드 수정 금지
- V1 DB 쓰기 금지 (읽기만 허용)
- .env.docker, 비밀번호 등 민감정보 Git 커밋 금지

### 3.2 백업
- 파일 수정 전 반드시: .bak.{YYYYMMDD_HHMMSS}

### 3.3 Git 규칙
- 커밋 접두사: [R{라운드}-{TASK번호}] 또는 [DOCS]
- 예: [R1-003] 발주 API, [R2-FRONT-001] Next.js 셋업, [DOCS] 기획서 수정
- 빈 테이블 커밋 금지

### 3.4 Docker 명령
```
docker compose --env-file .env.docker exec app php artisan {command}
docker compose --env-file .env.docker exec app composer {command}
```

### 3.5 보고서
- 위치: /srv/newtalk-v2/docs/reports/{TASK-ID}-report.md
- 필수 항목: 파일 목록, 실행 결과, 테스트 결과, Git SHA

---

## 4. 완료된 작업

### R0: 인프라 구축
- Laravel 12 + Docker 환경
- V1 스키마 추출 (226 테이블)
- 38 테이블 마이그레이션
- Spatie RBAC (6 roles, 36 permissions)
- GitHub 레포 + .cursorrules (129줄)

### R1-TASK-001: 인증 + RBAC
- Sanctum 인증 API
- 커밋: 37ad7e4
- 브랜치: feature/R1-TASK-001-auth

### R1-TASK-002: 상품 CRUD API
- 모델, 이미지, 옵션, 카테고리, 역할별 접근
- 커밋: 876f4b3
- 브랜치: feature/R1-TASK-002-products

### R1-TASK-003: 발주·입고·바코드 API
- 7단계 발주 상태 전이, 입고→수량 자동 갱신, 바코드 일괄 생성
- 커밋: 555ee03 (구현 완성)
- 브랜치: feature/R1-TASK-003-purchasing

### R1-TASK-004: 사입 대시보드 API
- admin 전용 6개 엔드포인트 (summary, suppliers, trend, recent-orders, recent-inbounds, alerts)
- 커밋: 67f0a64
- 브랜치: feature/R1-TASK-004-dashboard

### R1-TASK-005: 기본 대시보드 + V1 마이그레이션
- 역할별 overview + admin stats 엔드포인트
- V1→V2 마이그레이션 커맨드 3개 (users, products, wholesale)
  - users: 79,459건 dry-run 확인
  - products: 77,111건 dry-run 확인 (active 12,585)
  - wholesale: 1,818건 dry-run 확인
- 커밋: be662c7
- 브랜치: feature/R1-TASK-005-migration

### R2-FRONT-001: Next.js 프로젝트 셋업
- Next.js 16 프로젝트 구조, 인증(로그인/회원가입), 역할별 라우팅
- 관리자 대시보드 + 사입 대시보드 화면
- 소매/도매/MD/사입자 레이아웃
- 커밋: ce541c5
- 브랜치: feature/R2-FRONT-001-setup

### R2-FRONT-001-DEPLOY: 프론트엔드 배포
- Rate Limiting + 역할 라우트 + 401 로그아웃 + Docker 기동
- 커밋: 870c007
- 브랜치: feature/R2-FRONT-001-setup
- 접속: http://114.207.244.86:3000

---

## 5. 현재 진행 중인 작업

### 별도 진행 중 (다른 Cursor 대화)
- NAS 이미지 연동
- 콘텐츠 파이프라인

---

## 6. 다음 작업 큐

| 순서 | Task ID | 설명 |
|------|---------|------|
| 1 | R2-FRONT-002 | 소매 홈 피드 + 탐색 |
| 2 | R2-API-001 | 소셜 엔진 API (피드/팔로우/찜) |
| 3 | R2-FRONT-003 | 상품 상세 + 찜 |
| 4 | R2-FRONT-004 | 도매 브랜드 페이지 |
| 5 | R2-API-002 | 브랜드 페이지 API |
| 6 | R2-FRONT-005 | 관리자 사입 대시보드 상세 |
| 7 | R2-FRONT-006 | 도매 콘텐츠 업로드 |
| 8 | R2-API-003 | AI 콘텐츠 처리 API (NAS 연동) |
| 9 | R2-API-004 | 카페24 API 연동 |

---

## 7. 주요 문서 위치

```
/srv/newtalk-v2/
├── docs/
│   ├── planning/
│   │   └── NT-V2-PLAN-002-FINAL.md      ← 기획서 (8레이어, 66화면)
│   ├── architecture/
│   │   └── NT-V2-ARCHITECTURE.md         ← 시스템 아키텍처
│   ├── handover/
│   │   └── HANDOVER.md                   ← 이 문서 (인수인계서)
│   ├── reports/
│   │   ├── R1-TASK-001-report.md
│   │   ├── R1-TASK-002-report.md
│   │   ├── R1-TASK-003-report.md
│   │   ├── R1-TASK-004-report.md
│   │   ├── R1-TASK-005-report.md
│   │   └── R2-FRONT-001-report.md
│   ├── v1-analysis/
│   │   └── v1-purchasing-analysis.md
│   ├── scripts/
│   │   └── (런북 스크립트들)
│   ├── CHANGELOG.md                      ← 전체 변경 이력
│   └── README.md                         ← docs 디렉터리 안내
├── .cursorrules                          ← Cursor 작업 규칙 (129줄)
├── frontend/                             ← Next.js 16 (R2)
├── src/ 또는 루트                         ← Laravel 12
├── docker-compose.yml
└── .env.docker                           ← DB/Redis 비밀번호 (커밋 금지)
```

---

## 8. 기존 시스템 보호 (System A~D)

| ID | 설명 | 규칙 |
|---|---|---|
| A | V1 웹 (114.207.244.86:80) | 수정 금지 |
| B | V1 어드민 (114.207.244.87) | 수정 금지 |
| C | NAS image-auto (192.168.30.23:8100) | 별도 진행 |
| D | ShortFlow AI 쇼츠 | 별도 진행 |

---

## 9. 알려진 이슈

1. **auth_code 90 사용자 65,580명**: V1에서 역할 미분류. 분석 후 소매/도매 분류 필요.
2. **V1 products 마이그레이션**: 컬럼명 차이(g_idx, GoodsName 등) 해결 완료 (be662c7).
3. **R1 브랜치 미병합**: develop에 R1 브랜치들 아직 미병합. R2 전에 정리 필요.
4. **Docker src/ vs 루트**: app 서비스의 마운트가 ./src:/var/www/html인지 확인 필요.
