# GO100 FRONTEND FIX 완료 보고서 — 2026-02-21

## 작업 개요

| 항목 | 내용 |
|------|------|
| 작업 ID | CUR-GO100-FRONTEND-FIX |
| 브랜치 | phase-2c-command-center |
| 범위 | GO100 전용 코드만 수정 (`frontend/src/go100/`, `app/(protected)/go100/`) |
| 규칙 | V4.1 공통 프론트엔드 파일 미수정, 모든 수정 파일 첫 줄 `// CUR-GO100-FRONTEND-FIX, 2026-02-21` |

---

## 1. TASK 1 — "로딩 중..." 무한 로딩 수정

### 1-1. 원인 및 조치

| 구분 | 내용 |
|------|------|
| 원인 | API 호출이 `localhost:8002`로 직접 가서 외부 접속 시 연결 불가 → 요청 실패 시에도 `.catch()`로 예외를 삼켜 로딩만 유지 |
| 조치 | GO100 전용 클라이언트는 브라우저에서 상대 경로(`/api/go100`) 사용, 대시보드 훅은 실패 시 에러 상태로 전환 |

### 1-2. 수정/추가 파일

**`frontend/src/go100/api/go100Api.ts`**
- `BASE`: `process.env.NEXT_PUBLIC_GO100_API_URL` 있으면 해당 URL, 없으면 브라우저는 `"/api/go100"`, SSR은 `http://localhost:8002`.
- axios 인스턴스 `go100Client` 신규 생성 (브라우저 `baseURL: ""` → 동일 출처 요청, Next rewrites로 8002 프록시).
- 모든 GO100 API 호출을 `go100Client`로 통일, 401 시 로그인 리다이렉트 인터셉터 유지.

**`frontend/next.config.mjs`**
- `/api/go100/:path*` → 백엔드 프록시 rewrite 추가 (기존 `/api/:path*`와 함께 유지).

**`frontend/src/go100/hooks/useDashboard.ts`**
- `Promise.all` 내부 `.catch(() => ...)` 제거 → 하나라도 실패 시 `catch` 블록에서 `setError` + `setLoading(false)` 실행, 무한 로딩 방지.

**`frontend/src/go100/components/DashboardContent.tsx`**
- 에러 시 안내 문구 추가:  
  `"데이터를 불러올 수 없습니다. 새로고침하거나 잠시 후 다시 시도해주세요."`

**`frontend/src/app/(protected)/go100/error.tsx`** (신규)
- GO100 라우트 전용 에러 바운더리.
- 메시지: "데이터를 불러올 수 없습니다. 새로고침하거나 잠시 후 다시 시도해주세요."
- 버튼: "다시 시도", "GO100 대시보드" (최소 터치 영역 44px).

---

## 2. TASK 2 — 전략카드 초보자 친화 UI

### 2-1. 신규 페이지/컴포넌트

**`frontend/src/go100/components/StrategyCardDetail.tsx`** (신규)
- 모바일 우선, 가독성 중심 레이아웃.
- **한눈에 보기**: 유형/위험 뱃지, 전략명, 한 줄 요약, 4개 핵심 지표(수익률·최대손실폭·승률·백억이 평가), 연환산 복리 수익률.
- **이 전략은 이렇게 작동해요**: 3단계 StepCard(종목 찾기 → 매수 타이밍 → 분할 매도) + 안전장치 박스.
- **상세 설정 탭(고급)**: 종목선정 조건 / 매수·매도 규칙 / 분할익절 설정 / 위험관리(기존 `RiskConfigForm` 사용), 변경 시 "변경사항 적용 & 재백테스트", "원래대로".
- **백억이에게 수정 요청하기**: 입력창 + 수정 이력 타임라인.

**`frontend/src/go100/components/strategy/`** (신규 디렉터리)

| 파일 | 역할 |
|------|------|
| `Badge.tsx` | 유형 뱃지(scalping=파랑, swing=초록), 위험등급(high=빨강, medium=amber, low=회색) |
| `MetricBox.tsx` | 큰 숫자(text-2xl) + 라벨 + 선택 툴팁, 색상 green/red/blue/purple/gray |
| `StepCard.tsx` | 단계 번호·아이콘·제목·설명·디테일·툴팁(용어 설명) |
| `EditableParamTable.tsx` | 파라미터 테이블, 인라인 수정·저장·취소 |
| `PartialExitVisualizer.tsx` | 분할익절 단계 시각화(단계별 %·매도비율·손절선 이동) |
| `ModificationHistory.tsx` | 수정 이력 타임라인(날짜·변경 요약·전후 비교·재백테스트 결과) |
| `Tooltip.tsx` | 용어 설명 팝업(클릭 토글, 44px 터치 영역) |
| `Tabs.tsx` / `Tab` | 탭 컴포넌트(첫 탭 기본 선택) |
| `index.ts` | 위 컴포넌트 export |

### 2-2. 공통 스타일 규칙

- 모바일 가독성: 최소 터치 영역 44px.
- 폰트: 제목 `text-xl`, 본문 `text-sm`, 지표 숫자 `text-2xl`.
- 색상: 수익 `green-600`, 손실 `red-600`, 중립 `gray-600`, 강조 `blue-600`.
- 라운드: 카드 `rounded-2xl`, 내부 요소 `rounded-lg`.
- 말투: "~해요", "~입니다" 혼용.

### 2-3. 기존 코드 연동

**`frontend/src/app/(protected)/go100/strategies/[id]/page.tsx`**
- 기존 탭/카드 UI 제거.
- 서버에서 `card`, `lastRun`, `riskProfile` 조회 후 `StrategyCardDetail`에 전달.
- `summary` = `card.description`, `annualReturnEst` = 백테스트 수익률 기반 60일→연환산 추정.

**`frontend/src/go100/components/index.ts`**
- `StrategyCardDetail` export 추가.

---

## 3. TASK 3 — 빌드 확인

| 항목 | 결과 |
|------|------|
| `npx tsc --noEmit` | 성공 (exit 0) |
| `npm run build` | 성공 (Next.js 14.2.35) |
| GO100 라우트 | `/go100`, `/go100/strategies`, `/go100/strategies/[id]` 등 정상 번들 |

---

## 4. 수정·신규 파일 목록

### 수정
- `frontend/src/go100/api/go100Api.ts`
- `frontend/next.config.mjs`
- `frontend/src/go100/hooks/useDashboard.ts`
- `frontend/src/go100/components/DashboardContent.tsx`
- `frontend/src/go100/components/index.ts`
- `frontend/src/app/(protected)/go100/strategies/[id]/page.tsx`

### 신규
- `frontend/src/app/(protected)/go100/error.tsx`
- `frontend/src/go100/components/StrategyCardDetail.tsx`
- `frontend/src/go100/components/strategy/Badge.tsx`
- `frontend/src/go100/components/strategy/MetricBox.tsx`
- `frontend/src/go100/components/strategy/StepCard.tsx`
- `frontend/src/go100/components/strategy/EditableParamTable.tsx`
- `frontend/src/go100/components/strategy/PartialExitVisualizer.tsx`
- `frontend/src/go100/components/strategy/ModificationHistory.tsx`
- `frontend/src/go100/components/strategy/Tooltip.tsx`
- `frontend/src/go100/components/strategy/Tabs.tsx`
- `frontend/src/go100/components/strategy/index.ts`

---

## 5. 확인 체크리스트

- [ ] `localhost:3000/go100` — API 실패 시 "로딩 중..." 없이 에러 메시지·fallback 표시
- [ ] `localhost:3000/go100/strategies/14` — 전략 상세에서 한눈에 보기·작동 방식·고급 탭·AI 수정 요청 영역 표시
- [ ] V4.1 공통 프론트엔드 파일 미수정
- [ ] 모든 수정 파일 첫 줄에 `// CUR-GO100-FRONTEND-FIX, 2026-02-21` 포함

---

*작성일: 2026-02-21 | 작업 ID: CUR-GO100-FRONTEND-FIX*
