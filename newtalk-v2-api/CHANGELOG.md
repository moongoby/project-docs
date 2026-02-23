# 뉴톡 V2 변경 이력 (CHANGELOG)

모든 주요 변경 사항을 기록합니다. [Semantic Versioning](https://semver.org/) 준수.

---

## [Unreleased]
- R2-FRONT-001-DEPLOY: Frontend Docker 기동 대기

## [1.1.0] - 2026-02-23
### Added
- R2-FRONT-001: Next.js 16 프로젝트 셋업 (ce541c5)
- 로그인/회원가입 화면
- 역할별 레이아웃 (소매/도매/관리자/MD/사입자)
- 관리자 대시보드 + 사입 대시보드 (R1 API 연동)
- AuthController (POST login/logout, GET me)
- Docker Compose frontend 서비스 구성

### Documentation
- NT-V2-PLAN-002-FINAL.md: 통합 기획서 v1.0.0
- NT-V2-ARCHITECTURE.md: 시스템 아키텍처 v1.0.0
- HANDOVER.md: 인수인계서 v1.0.0
- docs/ 디렉터리 구조 표준화

## [1.0.0] - 2026-02-22
### R1 완료
- R1-001: Sanctum 인증 + RBAC (37ad7e4)
- R1-002: 상품 CRUD API (876f4b3)
- R1-003: 발주·입고·바코드 API (555ee03)
- R1-004: 사입 대시보드 API (67f0a64)
- R1-005: 기본 대시보드 + V1 마이그레이션 (be662c7)

## [0.1.0] - 2026-02-21
### R0 완료
- Laravel 12 + Docker 환경 구축
- V1 스키마 추출 (226 테이블)
- 38 테이블 마이그레이션
- Spatie RBAC 시더 (6 roles, 36 permissions)
- GitHub 레포 생성, .cursorrules 작성
