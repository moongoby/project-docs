# Supabase Auth 회원가입/로그인 연동 보고서

**작성일시:** 2026-02-24 14:00 KST  
**작업 유형:** 신규 개발  
**상태:** 완료  
**서버:** 114.207.244.86  
**프로젝트:** /data/shortflow  

## 1. 작업 개요

SaaS 대시보드(shotflow.newtalk.kr)에 Supabase Auth 기반 회원가입/로그인 기능을 연동했습니다.  
기존 더미 로그인을 실제 인증으로 교체하고, `@supabase/ssr` 기반 브라우저·서버 클라이언트로 쿠키 연동을 적용했습니다.

## 2. 변경 사항

| 파일 | 변경 내용 |
|------|----------|
| sql/010_profiles_table.sql | profiles 테이블 + RLS + 트리거 (full_name, company_name, role, plan) |
| saas-dashboard/lib/supabase-browser.ts | 브라우저 Supabase 클라이언트 (createBrowserClient) |
| saas-dashboard/lib/supabase-server.ts | 서버 Supabase 클라이언트 (createServerClient) |
| saas-dashboard/lib/supabase.ts | createBrowserClient 사용으로 변경 (기존 import 호환) |
| saas-dashboard/app/login/page.tsx | signInWithPassword 연동, 한글 에러 메시지, router.refresh() |
| saas-dashboard/app/register/page.tsx | signUp 연동 (이름, 회사명, 이메일, 비밀번호), 성공 후 /login 이동 |
| saas-dashboard/middleware.ts | getUser 기반 인증, 비인증→/login, /·/terms·/privacy 공개 |
| saas-dashboard/components/LogoutButton.tsx | createClient from supabase-browser, signOut |
| saas-dashboard/package.json | @supabase/ssr 추가 |
| saas-dashboard/.env.local | NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY (프로젝트 루트 .env 기준 생성) |

## 3. 테스트 결과

| 테스트 | 결과 |
|--------|------|
| npm run build (Docker 내) | ✅ 성공 |
| Lint | ✅ 에러 없음 |
| Docker build saas-dashboard | ✅ 성공 |
| Docker up saas-dashboard | ⚠️ 포트 3000 충돌 (newtalk-v2-frontend 사용 중) |

## 4. 선행 조건

- **대표님:** Supabase SQL Editor에서 `sql/010_profiles_table.sql` 실행 필요.  
  기존에 다른 스키마의 profiles 테이블이 있다면 마이그레이션 또는 테이블 교체 후 실행.

## 5. 백업

- 경로: `/data/shortflow/backups/20260224_140000_auth_integration`
- 내용: app_backup, components_backup, lib_backup, middleware.ts.bak, package.json.bak, sql_backup

## 6. 다음 작업 제안

- profiles SQL 실행 후 실제 회원가입/로그인 테스트
- 대시보드 헤더에 LogoutButton 노출 확인
- 프로필 수정 페이지 (full_name, company_name 등)
- 3000 포트 사용처 정리 후 saas-dashboard 컨테이너 기동 확인
