# GO100 FRONTEND FIX-2 완료 보고서 — 2026-02-21

## 작업 개요

| 항목 | 내용 |
|------|------|
| 작업 ID | CUR-GO100-FRONTEND-FIX2 |
| 브랜치 | phase-2c-command-center |
| 범위 | GO100 대시보드 404 해결, 전략카드 "내 전략" 연동, 대시보드 구성 |
| 규칙 | V4.1 프론트엔드 파일 수정 금지, GO100 코드만 수정, 수정 파일 첫 줄 `// CUR-GO100-FRONTEND-FIX2, 2026-02-21` |

---

## 1. TASK 1 — GO100 대시보드 404 해결

### 1-1. API 확인 결과

| 엔드포인트 | 결과 | 비고 |
|------------|------|------|
| `GET /api/go100/strategy-cards` | 404 Not Found | 라우터 미등록 |
| `GET /api/go100/portfolios` | 401 Not authenticated | 정상(인증 필요) |
| `GET /health` | 200 OK | 정상 |

**원인:** `backend/app/main.py`에 GO100 strategy-cards·store 라우터가 등록되어 있지 않아 `/api/go100/strategy-cards` 요청 시 404 발생.

### 1-2. 백엔드 조치

**`backend/app/main.py`**
- `go100_strategy_router` (prefix: `/api/go100/strategy-cards`), `go100_store_router` (prefix: `/api/go100`, 경로 `/store`) import 및 `app.include_router()` 등록.
- 적용 후 백엔드 재시작 필요.

### 1-3. useDashboard.ts

- **첫 줄:** `// CUR-GO100-FRONTEND-FIX2, 2026-02-21`
- API 호출을 **API별 개별 try/catch**로 분리 → 하나 실패해도 나머지 데이터 표시, 전체 에러로 막지 않음.
- 전략 목록: `getStrategyCards({ page: 1, page_size: 50 })` 1회 호출 후, 활성 개수·최근 5개를 클라이언트에서 계산.
- `todayTradesCount` 상태 추가 (오늘 거래 건수용, 현재 준비 중).

### 1-4. go100Api.ts

- **첫 줄:** `// CUR-GO100-FRONTEND-FIX2, 2026-02-21`
- 호출 URL은 백엔드 라우터와 일치 확인됨. 변경 없음.

### 1-5. DashboardContent.tsx

- **첫 줄:** `// CUR-GO100-FRONTEND-FIX2, 2026-02-21`
- **API 실패 시:** 빈 대시보드 표시(0건, 0원). "로딩 중..." 또는 빈 화면에 멈추지 않음.
- **데이터 없을 때:** "아직 데이터가 없습니다" + "전략을 만들어보세요" + **AI 대화 바로가기** 버튼.
- 로딩 스피너 제거, 항상 요약 카드·전략 목록 영역 렌더.
- 일부 API만 실패한 경우: "일부 데이터를 불러오지 못했습니다. 아래는 사용 가능한 정보입니다." 안내.

---

## 2. TASK 2 — GO100 전략카드가 "내 전략"에 표시

### 2-1. 전략 목록 페이지

**`frontend/src/app/(protected)/go100/strategies/page.tsx`**
- **첫 줄:** `// CUR-GO100-FRONTEND-FIX2, 2026-02-21`
- 서버 컴포넌트 → **클라이언트 컴포넌트**로 변경.
- `useStrategies()`로 `GET /api/go100/strategy-cards` 호출 (브라우저에서 토큰 전달, user_id는 백엔드에서 토큰으로 처리).
- GO100 "내 전략"은 GO100 전용 API만 사용. V4.1 "전체 전략" 탭은 수정하지 않음.

### 2-2. 전략카드 표시 정보

**`frontend/src/go100/components/StrategyCard.tsx`**
- **첫 줄:** `// CUR-GO100-FRONTEND-FIX2, 2026-02-21`
- 표시 항목: 전략명, 상태 뱃지(BACKTESTED / PAPER_LIVE / LIVE 등), 수익률, MDD, 생성일, **상세보기** 버튼 → `/go100/strategies/{id}`.

---

## 3. TASK 3 — GO100 대시보드 내용 구성

### 3-1. 상단 요약 카드 4개

| 카드 | 내용 |
|------|------|
| 활성 전략 수 | go100_strategy_cards 중 status IN (BACKTESTED, PAPER_LIVE, LIVE) 카운트 |
| Paper Trading | 포트폴리오 수, 평균 수익률 |
| Live Trading | 포트폴리오 수, 평균 수익률 |
| 오늘 거래 건수 | 준비 중(—) |

### 3-2. 전략 목록(최근 5개)

- `getStrategyCards` 결과를 `created_at` 기준 정렬 후 상위 5개 표시.
- 카드: 이름, 상태, 수익률, 생성일, 상세보기.

### 3-3. 새 전략 만들기

- 버튼 클릭 → `/go100/chat` (백억이 AI 대화).

### 3-4. API 실패 시

- 섹션별 독립 처리. 하나 실패해도 나머지 표시.
- 빈 데이터: "아직 데이터가 없습니다" + 안내.

---

## 4. TASK 4 — next.config.mjs 프록시

- `rewrites`: `/api/:path*`, `/api/go100/:path*` → `apiBase`(기본 `http://localhost:8002`) 유지.
- **첫 줄:** `// CUR-GO100-FRONTEND-FIX2, 2026-02-21`
- 404 지속 시: destination을 `http://127.0.0.1:8002`로 변경해볼 수 있음.
- CORS: 백엔드에서 `go100.newtalk.kr` 허용 여부 별도 확인.

---

## 5. TASK 5 — 빌드 & 배포

| 단계 | 결과 |
|------|------|
| `npx tsc --noEmit` | 성공 |
| `npm run build` | 성공 |

배포·서비스 재시작은 별도 진행.

---

## 6. 수정/추가 파일 목록

| 파일 | 변경 요약 |
|------|------------|
| `backend/app/main.py` | go100_strategy_router, go100_store_router import 및 include |
| `frontend/src/go100/api/go100Api.ts` | FIX2 헤더 |
| `frontend/src/go100/hooks/useDashboard.ts` | API별 fallback, 최근 5개·활성 개수 계산, todayTradesCount |
| `frontend/src/go100/components/DashboardContent.tsx` | 실패 시 빈 대시보드, AI 바로가기, 로딩 멈춤 제거 |
| `frontend/src/go100/components/StrategyCard.tsx` | MDD·생성일·상세보기 문구, FIX2 헤더 |
| `frontend/src/app/(protected)/go100/strategies/page.tsx` | 클라이언트 컴포넌트, useStrategies 사용 |
| `frontend/next.config.mjs` | FIX2 헤더 |

---

## 7. 적용 시 유의사항

1. **백엔드 재시작**  
   strategy-cards·store 라우터 반영을 위해 백엔드 프로세스 재시작 필요. 재시작 후 `/api/go100/strategy-cards`는 인증 시 200/401, 미인증 시 401 반환(404 아님).
2. **서비스 재시작**  
   빌드 완료 후 실제 서비스 재시작은 운영 계획에 따라 별도 진행.

---

*보고서 작성일: 2026-02-21*
