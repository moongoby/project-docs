# CUR-GO100-CHAT-POSITION-FIX 보고서
작업일: 2026-02-22

## 문제
채팅 위젯이 좌측 상단에 배치됨 (또는 데스크톱에서 패널 위치/간격 미통일)

## 원인
- FAB은 이미 `fixed bottom-6 right-6 z-50`로 되어 있었으나, 패널이 `sm:bottom-20`으로 FAB과 간격이 지시서 기준보다 작았음.
- 지시서 기준: 패널 `bottom-24 right-6`, FAB `bottom-6 right-6` 명시.

## 수정
- **파일**: `frontend/src/go100/components/ChatWidget.tsx`
- **헤더 주석**: `// CUR-GO100-CHAT-POSITION-FIX, 2026-02-22`
- **FAB**: `fixed bottom-6 right-6 z-50` 유지, 중복 `sm:bottom-6 sm:right-6` 제거.
- **패널**: `fixed z-50`, 모바일 `inset-0`, 데스크톱 `sm:inset-auto sm:bottom-24 sm:right-6 sm:w-96 sm:h-[500px]` 적용. 기존 `sm:bottom-20` → `sm:bottom-24`로 변경.
- **레이아웃**: `frontend/src/app/(protected)/layout.tsx`에서 ChatWidget은 이미 Sidebar/main과 동일 레벨에 있어 추가 수정 없음.

## 컴플라이언스
- [x] go100_strategy_cards 3건 유지
- [x] v4_positions OPEN 5건 유지
- [x] .env/.bak 커밋 없음 (해당 파일 미포함)
- [x] 파일 헤더 주석 포함

## 빌드
- `npx tsc --noEmit` 통과.
- `npm run build` 실패: `strategy-cards/page.tsx`의 기존 타입 오류(`Go100StrategyCardUpdate`에 `is_active` 없음). 본 작업(go100 파일만 수정) 범위 밖.

## 커밋
`51018376`
