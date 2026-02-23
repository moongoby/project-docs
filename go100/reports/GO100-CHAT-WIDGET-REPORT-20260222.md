# CUR-GO100-CHAT-WIDGET 보고서
작업일: 2026-02-22

## AI 대화 API

- **URL**: `POST /api/go100/ai/chat`
- **백엔드**: `backend/app/routers/go100/ai_router.py` (prefix `/api/go100/ai`)
- **요청**: `{ message: string, user_id: number, risk_tolerance?: RiskTolerance, session_id?: string }`  
  (백엔드는 추가로 `conversation_history`, `user_message` 지원)
- **응답**: `OrchestrationResult` — `reply_to_user`(사용자 응답 문구), `session_id`, `status`, `strategy_card_id` 등  
  프론트 타입 `ChatResponse`의 `message`와 백엔드 `reply_to_user` 호환을 위해 위젯에서는 `reply_to_user ?? message` 사용.

## 생성 파일

- **ChatWidget.tsx** (`frontend/src/go100/components/ChatWidget.tsx`):  
  우하단 FAB, 열기/닫기 토글, 대화 패널(헤더·메시지 영역·입력·전체화면/닫기 버튼), `chatWithAI` 호출, `session_id` localStorage 유지, 로딩/에러 처리, 모바일 전체화면·데스크톱 우하단 반응형.
- **레이아웃 수정**: `frontend/src/app/(protected)/layout.tsx` — `ChatWidget` import 및 렌더링 추가.  
- **index.ts**: `ChatWidget` export 추가.

## 전체화면 대화 페이지

- **경로**: `/go100/chat` — `frontend/src/app/(protected)/go100/chat/page.tsx` (기존 유지).
- **위젯 [전체화면] 버튼**: `router.push("/go100/chat")` 로 연결.
- **사이드바 "백억이"**: 전역 사이드바는 `/llm`, GO100 내부 사이드바(Go100Sidebar) "AI 대화"는 `/go100/chat` 연결 유지.

## 빌드 결과

- **tsc**: `npx tsc --noEmit` — 에러 0건.
- **build**: `npm run build` — 성공 (Next.js 14.2.35).

## 컴플라이언스

- [x] V4.1 핵심 파일 수정 최소화 (go100_* 및 protected 레이아웃만 수정)
- [x] .env/.bak 커밋 없음
- [x] 파일 헤더 주석 포함 (CUR-GO100-CHAT-WIDGET, 2026-02-22)

## 커밋

- 해시: `5a891210c91b4f9c504d7f7c7766923173b38073`
- 메시지: `feat: CUR-GO100-CHAT-WIDGET - 백억이 플로팅 대화 위젯`

## 서비스 확인

- `sudo systemctl restart go100-frontend` 실행 후 `/dashboard`, `/strategy-cards` 307(인증 리다이렉트) 확인.
