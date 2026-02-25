# ShortFlow SaaS 대시보드 기획서

**버전:** 1.0  
**작성일:** 2026-02-24  
**목적:** B2C SaaS 회원용 Next.js 대시보드 범위·화면·API·단계 정의

---

## 1. 개요

- **대상:** ShortFlow 유료/무료 구독 회원 (B2C)
- **역할:** 회원이 자신의 YouTube 채널·상품·작업·수익을 관리하고 파이프라인을 트리거하는 웹 대시보드
- **기존 대시보드와 관계:** 기존 Streamlit 대시보드(8501)는 내부 운영 모니터링용 유지, 본 문서는 **회원 전용 SaaS 대시보드(Next.js, 3000)** 를 대상으로 함

---

## 2. 기술 스택

| 구분 | 기술 |
|------|------|
| 프레임워크 | Next.js 14+ (App Router) |
| 스타일 | Tailwind CSS |
| 인증 | Supabase Auth (이메일/비밀번호, 소셜 확장 가능) |
| API 통신 | Supabase Client + Worker API (FastAPI) 프록시/직접 호출 |
| 배포 | Docker (포트 3000), 동일 shortflow-net |

---

## 3. 화면 구성

### 3.1 비로그인

| 경로 | 화면 | 설명 |
|------|------|------|
| `/` | 랜딩 | 서비스 소개, 요금제 요약, 로그인/회원가입 CTA |
| `/login` | 로그인 | 이메일/비밀번호, "비밀번호 찾기" 링크 |
| `/signup` | 회원가입 | 이메일, 비밀번호, 약관 동의 → 가입 후 자동 로그인 → 대시보드 리다이렉트 |

### 3.2 로그인 후 (공통 레이아웃)

- **헤더:** 로고, 내 계정(플랜 표시), 로그아웃
- **사이드바:** Overview, 채널, 상품·작업, 수익(Phase2), 설정, 이용약관/개인정보처리방침 링크
- **하단:** 통신판매업 신고번호 표기 (필수)

### 3.3 대시보드 화면 (1차 범위)

| 경로 | 화면 | 1차 내용 |
|------|------|----------|
| `/dashboard` | Overview | 카드: 연결 채널 수, 이번 달 작업 수, 완료/실패 건수, 플랜명·만료일. 최근 작업 목록(테이블). |
| `/dashboard/channels` | 채널 관리 | 연동 YouTube 채널 목록, "채널 연결" 버튼(플레이스홀더). |
| `/dashboard/jobs` | 작업 목록 | tenant 기준 jobs 목록, 상태·상품명·생성일, 필터. |
| `/dashboard/products` | 상품·픽 | daily_picks(tenant) 목록, 상태, "상품 추가" 플레이스홀더. |
| `/dashboard/settings` | 설정 | 프로필(이메일, 표시명), 플랜 정보, 결제 연동 전 "결제 수단 관리" 플레이스홀더. |
| `/dashboard/billing` | 요금·결제 | 현재 플랜, 다음 결제일, "결제하기" → 결제툴 API 연동 전까지 안내 문구. |

### 3.4 정적 페이지

| 경로 | 내용 |
|------|------|
| `/terms` | 이용약관 |
| `/privacy` | 개인정보처리방침 |
| `/footer` | 하단 컴포넌트에 통신판매업 신고번호 표기 |

---

## 4. API 연동

### 4.1 Supabase 직접 사용 (대시보드 → Supabase)

- **인증:** `supabase.auth.signInWithPassword`, `signUp`, `signOut`, `getSession`, `onAuthStateChange`
- **테넌트 데이터:** RLS 적용 후 `supabase.from('tenants').select()`, `from('channels').select()`, `from('jobs').select()`, `from('daily_picks').select()` 등 (tenant_id 자동 필터)

### 4.2 Worker API (선택)

- **트리거:** 파이프라인 수동 실행 시 `POST /api/v1/pipeline/daily` 등 (tenant_id 헤더 또는 body로 전달하도록 Worker 확장)
- **상태 조회:** Worker health, job 상태는 Supabase jobs 테이블로 충족 가능

### 4.3 환경 변수 (대시보드)

- `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` (브라우저 노출)
- `NEXT_PUBLIC_APP_URL` — 공식 도메인: **https://shotflow.newtalk.kr** (콜백·리다이렉트용)

---

## 5. 인증·멀티테넌트 연동

- 로그인 사용자 = Supabase `auth.uid()`
- `tenants.owner_id = auth.uid()` 로 1:1 매핑 (B2C)
- 회원가입 시 `tenants` 행 1건 생성, `owner_id = auth.uid()`, `email = user.email`, `plan = 'free'`
- 모든 tenant 소유 테이블 조회/변경은 RLS로 `tenant_id IN (SELECT id FROM tenants WHERE owner_id = auth.uid())` 로 제한

---

## 6. 결제 연동 전(1차) 범위

- **DB:** `subscriptions` 테이블 (tenant_id, plan, status, current_period_end, external_id 등)
- **UI:** "현재 플랜", "다음 결제일", "업그레이드/결제하기" 버튼 → 클릭 시 "결제 수단 연동 준비 중" 또는 "곧 오픈" 안내
- **결제 API 연동 시:** 동일 테이블·화면에 PG사 API 호출만 추가

---

## 7. 단계별 일정

| 단계 | 내용 | 산출물 |
|------|------|--------|
| **1차** | 기획 확정, Next.js 프로젝트 생성, 레이아웃·라우팅·플레이스홀더 페이지, 로그인/회원가입 UI, Supabase Auth 연동, 멀티테넌트 스키마·RLS, 결제용 테이블·플레이스홀더 UI | 기획문서, saas-dashboard 앱, SQL 마이그레이션, 1차 보고서 |
| 2차 | 채널 연결 플로우(YouTube OAuth 연동), 작업/상품 목록 실데이터 연동 | - |
| 3차 | 수익 대시보드, 결제 툴 API 연동 | - |

---

## 8. 파일 구조 (1차 목표)

```
/data/shortflow/
├── saas-dashboard/           # Next.js SaaS 대시보드
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx          # 랜딩
│   │   ├── login/page.tsx
│   │   ├── signup/page.tsx
│   │   ├── dashboard/
│   │   │   ├── layout.tsx    # 인증 필수 레이아웃
│   │   │   ├── page.tsx      # Overview
│   │   │   ├── channels/page.tsx
│   │   │   ├── jobs/page.tsx
│   │   │   ├── products/page.tsx
│   │   │   ├── settings/page.tsx
│   │   │   └── billing/page.tsx
│   │   ├── terms/page.tsx
│   │   └── privacy/page.tsx
│   ├── components/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx        # 통신판매업 신고번호
│   ├── lib/
│   │   └── supabase.ts       # client, server
│   └── package.json
├── sql/
│   ├── 005_tenants_channels_rls.sql
│   └── 006_subscriptions.sql
└── docs/plans/
    └── saas_dashboard_plan.md  # 본 문서
```

---

## 9. 완료 조건 (1차)

- [ ] 본 기획문서 저장
- [ ] Next.js(saas-dashboard) 생성, 랜딩/로그인/회원가입/대시보드 플레이스홀더 페이지 동작
- [ ] Supabase Auth 로그인/회원가입/로그아웃 동작
- [ ] 멀티테넌트 스키마(tenants, channels, tenant_id, RLS) 적용
- [ ] 결제용 subscriptions 테이블 및 대시보드 내 플레이스홀더 UI
- [ ] 1차 작업 보고서 작성
