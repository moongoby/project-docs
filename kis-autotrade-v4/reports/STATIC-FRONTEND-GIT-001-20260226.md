# STATIC-FRONTEND-GIT-001 실행 보고서
**일자:** 2026-02-26
**목적:** 정적 HTML 파일 git 관리 편입

## 변경사항
- frontend/static/ 디렉토리 신규 생성
- admin.html, js/backtest-dashboard.js, css/admin.css 편입
- scripts/deploy_static.sh 배포 스크립트 추가
- kis-v41-rules.md에 정적 프론트엔드 관리 규칙 추가

## 배포 흐름
frontend/static/ 수정 → git commit → bash scripts/deploy_static.sh → 서빙 디렉토리 동기화

## 규칙
- /var/www/ 직접 수정 금지
- frontend/static/ 수정 시 CEO + Claude PM 승인 필수
