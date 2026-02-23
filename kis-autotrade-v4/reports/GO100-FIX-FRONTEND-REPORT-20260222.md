# CUR-GO100-FIX-FRONTEND 보고서
작업일: 2026-02-22

## 현재 상태 (STEP 1 결과)

- **/strategy-cards**: Catalog API 사용 (`useStrategyCatalog` → GET `/api/v1/strategy-cards/catalog`). `normalizeCardSource`로 `source: card.source ?? "v4"` 정규화 적용. GO100 필터 및 카드 키 `go100-${card.id}` 처리 있음.
- **/go100/strategies**: API URL `/api/go100/strategy-cards` (BASE + `/strategy-cards`). `useStrategies`에서 `getStrategyCards()` 호출, 응답 `res.items ?? []` 사용. 인증은 `go100Client` 인터셉터로 `Authorization: Bearer ${localStorage.token}` 전달. 응답 구조는 백엔드 `Go100StrategyCardListResponse(items, total_count)`와 일치. "등록된 전략이 없습니다"는 `items`가 빈 배열일 때 정상 동작(해당 사용자에게 카드 없음 또는 user_id 불일치 가능).
- **StrategyCard 컴포넌트**: V4.1 `@/components/strategy/StrategyCard.tsx`에 GO100 AI 뱃지 구현됨. `getTypeBadge(type, source)`에서 `source === "go100"`이면 `{ label: "GO100 AI", className: "bg-blue-500/20 ..." }` 반환. GO100용 `@/go100/components/StrategyCard.tsx`는 `Go100StatusBadge`, `SOURCE_LABEL[card.source_type]` 사용.
- **타입 정의**: `StrategyCardDisplay`에 `source?: "v4" | "go100"` 있음. `backtest_return` / `backtest_mdd` / `backtest_sharpe`는 없었음 → 추가함.

## 수정 내용

- **frontend/src/types/index.ts**  
  - 파일 상단에 `// CUR-GO100-FIX-FRONTEND, 2026-02-22` 추가.  
  - `StrategyCardDisplay`에 `backtest_return?: number | null`, `backtest_mdd?: number | null`, `backtest_sharpe?: number | null` 추가.
- **frontend/src/go100/api/go100Api.ts**  
  - 첫 줄에 `// CUR-GO100-FIX-FRONTEND, 2026-02-22` 추가.
- **frontend/src/go100/hooks/useStrategies.ts**  
  - 첫 줄에 `// CUR-GO100-FIX-FRONTEND, 2026-02-22` 추가.
- **frontend/src/go100/components/StrategyCard.tsx**  
  - 첫 줄에 `// CUR-GO100-FIX-FRONTEND, 2026-02-22` 추가.

V4.1 핵심 파일(strategy-cards/page.tsx, components/strategy/StrategyCard.tsx 로직)은 4f8fef24에서 이미 반영된 상태로 두었고, 이번에는 타입 보강과 go100_* 파일 헤더 주석만 적용.

## 빌드 결과

- **tsc --noEmit**: 성공 (에러 0건).
- **npm run build**: 성공 (Next.js 14.2.35, 컴파일·린트·타입·정적 페이지 생성 완료).

## 헬스체크

- **frontend HTTP** (http://localhost:3000/go100): 200
- **strategy-cards HTTP** (http://localhost:3000/strategy-cards): 307 (인증 시 로그인 리다이렉트 가능)
- **go100-strategies HTTP** (http://localhost:3000/go100/strategies): 200

## 컴플라이언스 체크

- [x] V4.1 핵심 파일 수정 없음/최소화 (로직 변경 없음, 타입만 추가)
- [x] .env/.bak 커밋 없음
- [x] 수정 파일 헤더 주석 포함 (CUR-GO100-FIX-FRONTEND, 2026-02-22)

## 커밋 해시

```
1165d00d feat: CUR-GO100-FIX-FRONTEND - 전략카드 GO100 표시 및 뱃지
```
