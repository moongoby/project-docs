# CUR-GO100-BACKTEST-CARD-LIST-FIX-001 — 백테스트 전략 드롭다운 GO100 카드 노출

**발행:** 2026-02-24  
**우선순위:** P0

## 문제

- `/backtest` 페이지 전략 드롭다운에 V4.1 카드(DESK* 등)만 노출되고 GO100 전략카드(`go100_strategy_cards`)가 미노출됨.
- 백테스트 실행 불가 → 실매매 전 필수 수정.

## 원인

- 백엔드 `list_cards_for_backtest`는 이미 `go100_strategy_cards`를 병합해 반환하고 있었음.
- 다만 (1) V4.1 카드에 `source`가 없어 프론트 구분이 애매할 수 있고, (2) GO100 카드에 `universe_filter`/`entry_rules`/`exit_rules`가 없어 백테스트 페이지에서 “종목 자동 선정 조건” 표시가 불완전할 수 있음.
- 프론트 `StrategyCard` 타입에 `source`, `go100_card_id` 등이 없어 for-backtest 응답 타입이 불명확함.

## 수정 내용

### 백엔드

- **`backend/app/schemas/strategy_card_schemas.py`**
  - `StrategyCardResponse`에 `source` 주석 정리 (`"v4" | "go100"`).
  - `universe_filter`, `entry_rules`, `exit_rules` 필드 추가 (CUR-GO100-BACKTEST-CARD-LIST-FIX-001, 백테스트 드롭다운 GO100 universe 표시용).
- **`backend/app/services/strategy_card_service.py`**
  - CUR-GO100-BACKTEST-CARD-LIST-FIX-001 주석 추가.
  - `list_cards_for_backtest`:
    - V4.1 카드에 `source="v4"` 명시 (`model_copy(update={"source": "v4"})`).
    - GO100 쿼리에 `universe_filter`, `entry_rules`, `exit_rules` 포함 후 응답에 세팅.
- **`backend/app/api/v1/strategy_cards_router.py`**
  - CUR-GO100-BACKTEST-CARD-LIST-FIX-001 주석 추가.

### 프론트엔드

- **`frontend/src/types/index.ts`**
  - `StrategyCard`에 `source?: "v4" | "go100"`, `go100_card_id?: number | null`, `universe_filter`, `entry_rules`, `exit_rules` 추가 (for-backtest 응답 타입 정합).
- **`frontend/src/app/(protected)/backtest/page.tsx`**
  - CUR-GO100-BACKTEST-CARD-LIST-FIX-001 주석 추가 (for-backtest API의 source/go100_card_id 활용).

## 검증

- **for-backtest API:** 로그인 후 `GET /api/v1/strategy-cards/for-backtest` 호출 시 `source: "v4"` / `source: "go100"`, `go100_card_id` 포함 여부 확인.
- **드롭다운:** `/backtest` 접속 후 전략 선택 드롭다운에서 GO100 카드가 `[GO100] 전략명` 형태로 노출되는지 확인.
- **배포 후:** 로그인 계정으로 `/backtest` 접속하여 위 항목 재확인 권장.

## 빌드/배포

- Python compile: 통과  
- tsc: 통과  
- npm build: 통과  
- go100: active (running)  
- go100-frontend: active (running)  
- kis-v41-* 서비스: 재시작 없음 (지시 준수)

## 브랜치/배포

- 브랜치: `fix/CUR-GO100-BACKTEST-CARD-LIST-FIX-001` → `phase-2c-command-center` 머지 후 푸시 완료.
- 배포: `systemctl restart go100`, `systemctl restart go100-frontend` 실행 완료.

## 백업

- 경로: `/root/backups/20260224-backtest-card-fix/`  
- 대상: `frontend/src/app/(protected)/backtest/page.tsx` 등 관련 파일.
