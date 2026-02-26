# CUR-GO100-UNIVERSE-SCREEN-AUDIT-001
> 조사일: 2026-02-24 17:10 KST | 우선순위: P1

## 목적
전략카드의 universe_filter(종목발굴) 결과를 사용자가 확인할 수 있는 화면/API 존재 여부 조사

---

## 조사 결과

### 1. 프론트엔드 화면
| 항목 | 여부 | 비고 |
|------|------|------|
| 전략 상세 페이지 (/go100/strategies/[id]) universe_filter 표시 | ✅ 있음 | **조건 설명만** 표시 (describeUniverse, 종목 선정 조건). **실제 선정 종목 리스트는 없음** |
| 전략 목록 페이지 종목 미리보기 | ❌ 없음 | 전략카드 리스트에 종목 목록/미리보기 없음 |
| 별도 종목발굴 페이지 | ❌ 없음 | universe/종목발굴 전용 페이지 없음 |
| 백테스트 결과에서 종목 목록 | △ 부분 | `trade_log`에 **거래한 종목**만 있음. 시점별 universe 후보 전체는 미제공 |

- **universe 관련 프론트 파일**: `strategies/[id]/page.tsx`, `StrategyDetailModal.tsx`, `ruleDescriber.ts`, `backtest/page.tsx`, `strategy.ts`, `backtest.ts` 등에서 `universe_filter`를 **설명용**으로만 사용.

### 2. 백엔드 API
| 항목 | 여부 | 비고 |
|------|------|------|
| GO100 universe 전용 라우터 | ❌ 없음 | `/api/go100/universe/*` 없음. `backend/app/routers/go100/` 내 universe*.py 없음 |
| 종목발굴 실행(미리보기) API | ❌ 없음 | card_id + 기준일 → 종목 리스트 반환하는 API 없음 |
| 백테스트 내 종목 선정 결과 반환 | △ 부분 | `result_detail`에 `equity_curve`, `trade_log`만 저장·반환. `trade_log`로 거래 종목만 유추 가능. `universe_filter_snapshot`은 DB에 저장되나 **API 응답 스키마에 미포함** |

- **기존 universe 관련 API** (GO100과 무관):
  - `/api/v4/universe/*`: V4.1 유니버스 **버전 관리** (UniverseService).
  - `/api/v4/brain/universe/today`, `/api/v4/brain/universe/build`: ChiefAnalyst용 today_universe (개발/시스템용).
- **실행 경로**: `UniverseEngine.select_stocks(universe_filter, ref_date, db)`는 백테스트/페이퍼/라이브 엔진 내부에서만 호출됨. 외부 API로 노출되지 않음.

### 3. DB
| 항목 | 여부 | 비고 |
|------|------|------|
| 종목발굴 결과 저장 전용 테이블 | ❌ 없음 | `universe%`, `screen%`, `pick%` 이름의 테이블 없음 (코드·마이그레이션 기준) |
| 전략카드 universe_filter 내용 | ✅ 있음 | `go100_strategy_cards.universe_filter` (JSONB). 조건만 저장, **실행 결과(종목 리스트)는 저장하지 않음** |
| 백테스트 시 universe 스냅샷 | ✅ 있음 | `go100_backtest_runs.universe_filter_snapshot` (JSONB). API에서는 미반환. `stock_codes_used` (TEXT[]) 컬럼은 스키마에 있으나 서비스에서 미사용 |

- 조사 시 DB 접속은 Peer 인증 오류로 미실행(서버 211.188.51.113에서 직접 실행 필요).

### 4. 현황 요약
- **사용자가 “이 전략이 오늘 어떤 종목을 고르는지”를 볼 수 있는 화면/API는 현재 없음.**
- 전략 상세에서는 universe_filter **조건**만 자연어로 노출되고, **실제 선정 종목 리스트**는 어디에도 노출되지 않음.
- 백테스트는 내부적으로 UniverseEngine으로 종목을 선정하지만, 그 **선정 종목 목록**은 결과에 포함되지 않음. `trade_log`로 거래된 종목만 확인 가능.
- 따라서 **종목발굴 미리보기(실행 결과 확인) 기능**은 신규 기획·구현이 필요함.

---

## 기획 제안: 종목발굴 미리보기 기능

### 5-1. 사용자 니즈
- "내 전략이 오늘 어떤 종목을 골랐는지 보고 싶다"
- "백테스트 전에 종목 리스트를 먼저 확인하고 싶다"
- "전략 조건을 바꾸면 종목이 어떻게 달라지는지 비교하고 싶다"

### 5-2. 제안 기능
| 옵션 | 내용 |
|------|------|
| **A** | 전략 상세 페이지에 **"오늘의 추천종목"** 섹션 추가 (preview API 연동) |
| **B** | **종목발굴 미리보기 API**: `POST /api/go100/universe/preview` (card_id, base_date 선택 시 → 종목 리스트) |
| **C** | 백테스트 결과에 **선정 종목 목록** 포함 (시작일 기준 universe 후보 저장/반환) |
| **D** | 향후: 별도 **종목 스크리너** 페이지 |

### 5-3. 구현 우선순위
- **Phase 1**: 전략 상세에 추천종목 표시 + **preview API** (card_id + base_date → 종목 리스트)
- **Phase 2**: 백테스트 결과에 선정 종목 목록 포함 (또는 `universe_filter_snapshot` API 노출)
- **Phase 3**: 독립 스크리너 페이지

### 5-4. 필요 작업
| 구분 | 작업 |
|------|------|
| **신규 API** | `POST /api/go100/universe/preview` (card_id, base_date?) → `{ "codes": ["005930", ...], "names": [...] }`. 내부에서 `UniverseEngine.select_stocks(card.universe_filter, base_date, db)` 호출 |
| **프론트** | 전략 상세 페이지에 **UniversePreview** 컴포넌트 (preview API 호출 후 종목 리스트 표시) |
| **DB** | (선택) `go100_universe_snapshots` 테이블 — 일별 스냅샷 저장 시 캐시/이력용 |
| **백테스트** | (선택) 완료 시 `result_detail`에 `universe_codes` 또는 `stock_codes_used` 채우고, API 스키마·프론트에 노출 |

---

## 참고

### 전략카드 universe_filter 샘플 (코드 기준)
- `go100_strategy_cards.universe_filter`: JSONB, 형식 예: `{"type": "AND", "conditions": [{"type": "scope", "params": {"market": "ALL"}}, {"type": "market_cap", "params": {"rank": 200}}, ...]}`

### 관련 파일 목록
- **프론트**: `frontend/src/app/(protected)/go100/strategies/[id]/page.tsx`, `frontend/src/go100/components/StrategyDetailModal.tsx`, `frontend/src/go100/utils/ruleDescriber.ts`, `frontend/src/go100/types/strategy.ts`, `frontend/src/go100/types/backtest.ts`
- **백엔드**: `backend/app/services/go100/universe/engine.py`, `backend/app/services/go100/backtest/backtest_service.py`, `backend/app/services/go100/backtest/simulator.py`, `backend/app/services/go100/strategy/card_service.py`, `backend/app/routers/go100/` (universe 전용 라우터 없음)
- **DB**: `backend/migrations/020_go100_tables.sql` (go100_strategy_cards.universe_filter, go100_backtest_runs.universe_filter_snapshot, result_detail)

### OpenAPI 기준 universe 관련 경로 (참고)
- `/api/v1/market/universe`, `/api/v1/market/universe/search`
- `/api/v4/brain/universe/build`, `/api/v4/brain/universe/today`
- `/api/v4/universe`, `/api/v4/universe/active`, `/api/v4/universe/versions`, `/api/v4/universe/versions/{version_id}/activate`  
→ 위는 모두 **GO100 전략카드 universe_filter 미리보기**와는 별개.
