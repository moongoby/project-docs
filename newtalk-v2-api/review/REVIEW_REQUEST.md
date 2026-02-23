# 코드 검수 요청서
> 작성일: 2026-02-23
> 작업ID: R2-FRONT-001
> 브랜치: feature/R2-FRONT-001-setup

## 검수 대상 파일
| 파일 | 원본 경로 | 검수 포인트 |
|------|----------|------------|
| R2-FRONT-001_api.ts | frontend/src/lib/api.ts | API 클라이언트 구조, 에러 처리, 토큰 관리 |
| R2-FRONT-001_auth-store.ts | frontend/src/stores/auth-store.ts | Zustand 상태관리, persist, 보안 |
| R2-FRONT-001_middleware.ts | frontend/src/middleware.ts | 인증 체크, 역할별 리다이렉트 |
| R2-FRONT-001_AuthController.php | app/Http/Controllers/Api/AuthController.php | Sanctum 인증, 토큰 발급, 보안 |

## 아키텍처 맥락
R2-FRONT-001은 Next.js 16 프론트엔드 초기 셋업으로, 인증 흐름(로그인→토큰→역할별 리다이렉트)과
API 통신 기반을 구축하는 작업. 이 4개 파일이 전체 프론트엔드의 인증·통신 기반이 됨.

## 검수 요청 사항
1. 인증 흐름에 보안 취약점이 없는지
2. 토큰 저장 방식(cookie vs localStorage)이 적절한지
3. 역할별 리다이렉트 로직이 6개 역할을 모두 커버하는지
4. API 에러 처리가 적절한지
5. 아키텍처 문서(NT-V2-ARCHITECTURE.md)와 일치하는지

## 민감정보 확인
- [x] 비밀번호 제거 완료
- [x] API 키/토큰 제거 완료
- [x] .env 값 하드코딩 없음
