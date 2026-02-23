# CUR-GO100-CHATWIDGET-FIX-004 보고서

## 기본 정보
- 작업일: 2026-02-23 18:00 KST
- 서버: root@211.188.51.113
- 근거: CHATWIDGET-DIAG-001 진단 결과

## 근본 원인
tailwind.config.ts의 content 배열에 ./src/go100/** 경로가 없어서
ChatWidget(src/go100/components/ChatWidget.tsx)이 사용하는
CSS 유틸리티 클래스(fixed, bottom-6, right-6, z-[9999] 등)가
빌드 시 purge되어 FAB이 DOM에는 존재하지만 스타일 없이 미노출됨.

## 수정 내용
tailwind.config.ts content 배열에 추가:
"./src/go100/**/*.{js,ts,jsx,tsx,mdx}"

## 검증
- 빌드: npm run build 성공
- 빌드 산출물에서 FAB 클래스 존재 확인 (.next/static/chunks/9376-*.js 내 fixed bottom-6 right-6 z-[9999])
- go100-frontend 재시작 후 active
- 브라우저 확인: CEO 확인 대기

## GitHub URL
- 보고서: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-CHATWIDGET-FIX-004-20260223.md
