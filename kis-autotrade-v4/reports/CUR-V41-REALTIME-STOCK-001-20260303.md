# CUR-V41-REALTIME-STOCK-001 — 키움 실시간 연동 + 종목명(코드) 표기 통일

- **작업일**: 2026-03-03
- **커밋**: 2a831b8b (kis-autotrade-v4)
- **작업 범위**: 백엔드 4파일 + 프론트엔드 4파일 + DB 데이터 수정

---

## 발견 이슈 및 처리 결과

### I-1: paper_status 항상 "none" [FIXED]

| 항목 | 내용 |
|------|------|
| **증상** | 대시보드 summary API의 `paper_status: "none"` — 페이퍼 트레이딩이 ACTIVE인데도 미반영 |
| **원인** | `get_dashboard_paper_account_id()`가 `go100_paper_accounts` 테이블을 조회하는데 이 테이블이 **비어 있음**. 실제 데이터는 `go100_portfolios`에 존재 |
| **수정** | `data_queries.py:915` — `go100_paper_accounts` → `go100_portfolios` 직접 조회로 변경 |
| **결과** | `paper_status: "active"` 정상 표시 |

### I-2: live_status 항상 "none" [FIXED]

| 항목 | 내용 |
|------|------|
| **증상** | 라이브 트레이딩 스케줄(schedule_id=5) 활성 상태인데 `live_status: "none"` |
| **원인** | `dashboard_router.py` 두 곳에 `live_status = "none"` 하드코딩, 조건 분기 없음 |
| **수정** | `go100_strategy_cards.is_active = true` 확인 로직 추가 |
| **결과** | `live_status: "active"` 정상 표시 |

### I-3: total_asset = 0 [FIXED]

| 항목 | 내용 |
|------|------|
| **증상** | 대시보드 `total_asset: 0` — 실제 포트폴리오 자산이 미반영 |
| **원인** | `get_paper_performance(account_id)` 가 go100_paper_accounts의 account_id로 성과 조회하는데 테이블 비어있어 0 반환 |
| **수정** | go100_portfolios `SUM(current_cash + total_eval)` 합산으로 total_asset 산출 |
| **결과** | `total_asset: 14,999,700원` (포트폴리오 2개 합산) |

### I-4: stock_name NULL (go100_live_orders 14건 전부) [FIXED]

| 항목 | 내용 |
|------|------|
| **증상** | `/api/go100/live/orders` 응답의 `stock_name` 모두 NULL |
| **원인** | 주문 생성 시 stock_name 미기록. `go100_live_orders.stock_name` 컬럼 있으나 INSERT 시 미설정 |
| **수정 1** | `live_orders_router.py` SQL에 `LEFT JOIN stock_universe su` 추가, `COALESCE(lo.stock_name, su.stock_name, lo.stock_code)` |
| **수정 2** | DB UPDATE: user_id=2→3 이관 및 stock_name 일괄 채움 (14건) |
| **추가** | API 응답에 `display_name: "종목명(코드)"` 필드 신규 추가 |
| **결과** | `삼성전자(005930)` 형식으로 정상 표시 |

### I-5: paper positions/trades stock_name NULL 가능 [FIXED]

| 항목 | 내용 |
|------|------|
| **증상** | `/api/go100/paper-trading/{id}/positions`, `/trades` 에서 stock_name NULL 가능 |
| **원인** | `paper_service.py`의 get_positions/get_trades 쿼리에 stock_universe JOIN 없음 |
| **수정** | `go100_positions`, `go100_trades` 쿼리에 `LEFT JOIN stock_universe su` 추가 |
| **결과** | `대원강업(000430)` 포지션 정상 표시 |

### I-6: 프론트엔드 종목명 표기 불일치 [FIXED]

| 파일 | 기존 | 변경 |
|------|------|------|
| `ActivityFeed.tsx:53` | `{a.stock_name ?? a.stock_code}` | `{a.stock_name ? \`${a.stock_name}(${a.stock_code})\` : a.stock_code}` |
| `TradeTable.tsx:39` | `{t.stock_name \|\| t.stock_code}` | `{t.stock_name ? \`${t.stock_name}(${t.stock_code})\` : t.stock_code}` |
| `dashboard/PositionTable.tsx:48` | 종목명 + 코드 2줄 분리 | `종목명(코드)` 단일 표기 |
| `go100/PositionTable.tsx:42` | `{p.stock_name \|\| p.stock_code}` | `{p.stock_name ? \`${p.stock_name}(${p.stock_code})\` : p.stock_code}` |

### I-7: accounts.alias 컬럼 오류 (이전 작업) [FIXED]

- `/api/go100/trade/accounts` → 500 에러 (`alias` 컬럼 없음, 실제 컬럼명 `account_alias`)
- 커밋 6fdfcd17에서 수정 완료

---

## 잔존 이슈 (미처리)

| # | 이슈 | 상태 | 비고 |
|---|------|------|------|
| R-1 | go100 대시보드 홈의 `paper_status` OverviewCard 미반영 | 미처리 | API는 "active"지만 UI 카드 렌더링 로직 별도 확인 필요 |
| R-2 | `/api/v1/health` 404 | 미처리 | 헬스체크 경로 미등록 (기능 영향 없음) |
| R-3 | 일중 실시간 가격 조회 없음 | 구조적 한계 | GO100 엔진이 REST 폴링 기반, 일일 종가만 사용 |
| R-4 | 키움 WebSocket 미연동 | 미처리 | 체결/호가 실시간 구독 없음, REST polling만 |
| R-5 | go100_portfolios.total_eval 미업데이트 | 미처리 | 장중 현재가 반영 안 됨 (일일 배치로만 갱신) |

---

## 검증 결과

```
대시보드 summary (moongoby@naver.com):
  paper_status: active ✅
  live_status:  active ✅
  total_asset:  14,999,700원 ✅

live orders:
  삼성전자(005930) FILLED @216,500원 ✅

paper positions (portfolio_id=6):
  대원강업(000430) 465주 @4,295원 ✅

프론트엔드 빌드: 성공 ✅
go100.newtalk.kr: HTTP 200 ✅
```

---

## 변경 파일

**백엔드**:
- `backend/app/services/go100/ai/data_queries.py` — paper_account_id 조회 수정
- `backend/app/routers/go100/dashboard_router.py` — paper/live_status + total_asset 로직
- `backend/app/routers/go100/live_orders_router.py` — stock_universe JOIN + display_name
- `backend/app/services/go100/paper_trading/paper_service.py` — positions/trades JOIN

**프론트엔드**:
- `frontend/src/go100/components/dashboard/ActivityFeed.tsx`
- `frontend/src/go100/components/dashboard/PositionTable.tsx`
- `frontend/src/go100/components/TradeTable.tsx`
- `frontend/src/go100/components/PositionTable.tsx`

**커밋**: 2a831b8b (kis-autotrade-v4, phase-2c-command-center)
