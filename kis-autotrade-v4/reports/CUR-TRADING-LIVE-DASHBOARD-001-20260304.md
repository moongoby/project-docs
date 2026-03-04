---
project: KIS
task_id: CUR-TRADING-LIVE-DASHBOARD-001
completed_at: 2026-03-04T15:15:00+09:00
---

# CUR-TRADING-LIVE-DASHBOARD-001 실행 결과

## 태스크 정보
- **목표**: 모의계좌·실계좌 매매 결과 실시간 대시보드 구축
- **작업 날짜**: 2026-03-04

---

## 생성 파일

| 파일 | 설명 |
|------|------|
| `backend/app/api/v1/trading_dashboard_router.py` | Part 1 — 백엔드 API 6개 엔드포인트 + SSE |
| `backend/app/main.py` | trading_dashboard_router 임포트·등록 추가 |
| `frontend/src/app/(protected)/go100/trading/dashboard/page.tsx` | GO100 라우트 페이지 |
| `frontend/src/go100/pages/TradingDashboardPage.tsx` | GO100 React 대시보드 컴포넌트 |
| `frontend/src/go100/api/tradingDashboardApi.ts` | GO100 API 클라이언트 |
| `frontend/static/js/dashboard.js` | V4.1 정적 대시보드 JS |
| `backend/tests/test_trading_dashboard_router.py` | 단위 테스트 15건 |

---

## Part 1 — 백엔드 API

### 엔드포인트 목록

| 엔드포인트 | 설명 |
|-----------|------|
| `GET /api/v1/trading/dashboard/summary` | 오늘 채널별 수익률·거래수 요약 |
| `GET /api/v1/trading/dashboard/positions` | 보유 포지션 실시간 목록 |
| `GET /api/v1/trading/dashboard/orders` | 일별 주문 체결 내역 |
| `GET /api/v1/trading/dashboard/performance` | 기간별 성과 차트 데이터 (1W|1M|3M|ALL) |
| `GET /api/v1/trading/dashboard/signals` | 당일 시그널 발생·통과·차단 현황 |
| `SSE /api/v1/trading/dashboard/stream` | 실시간 이벤트 스트림 |

### 주요 설계 결정
- JWT user_id 기반 인증: CEO(user_id=2)는 전체 조회, 일반은 본인 데이터
- `account_type` 파라미터: paper/live/all 구분
- SSE: 신규 체결 시 `new_trade` 이벤트, 30초마다 heartbeat
- 포지션 캐시: 응답에 `cached_at` + `cache_ttl_sec=1` 포함
- 실계좌: `STATUS: INACTIVE` (FORBIDDEN_ACCOUNT_IDS 가드)

---

## Part 2 — 프론트엔드

### GO100 (Next.js)
- **URL**: `/go100/trading/dashboard`
- **컴포넌트**: `TradingDashboardPage.tsx`
  - AccountSwitcher: 전체/모의계좌/가상매매 탭 전환
  - SummaryCard: 4채널 요약 카드
  - PositionTable: 보유 포지션 테이블 (수익/손실 색상)
  - OrderHistoryTable: 당일 체결 내역 (스크롤)
  - SignalFeed: 시그널 통과율 바
  - 성과 데이터: 기간 선택 (1W/1M/3M/ALL)
  - SSE 실시간 이벤트 피드 (신규 체결 하이라이트)
  - 1분 자동 갱신

### V4.1 (정적 JS)
- **파일**: `frontend/static/js/dashboard.js`
- 6개 API 엔드포인트 호출
- 테이블 렌더: 요약·포지션·체결·시그널
- SSE 스트림 연결 + 5초 자동 재연결
- `global.TradingDashboard.loadAll()` 전역 노출

---

## 단위 테스트 결과

```
backend/tests/test_trading_dashboard_router.py — 15건

TestImport::test_trd_1_router_import_ok         PASSED
TestImport::test_trd_2_file_syntax_ok            PASSED
TestImport::test_trd_3_endpoints_defined         PASSED
TestHelpers::test_trd_4_ceo_uid_check            PASSED
TestHelpers::test_trd_5_sse_endpoint_has_streaming_response PASSED
TestHelpers::test_trd_6_main_py_router_registered PASSED
TestHelpers::test_trd_7_account_type_params      PASSED
TestHelpers::test_trd_8_performance_periods      PASSED
TestFrontend::test_trd_9_go100_page_exists       PASSED
TestFrontend::test_trd_10_trading_dashboard_page_component PASSED
TestFrontend::test_trd_11_trading_dashboard_api_ts PASSED
TestFrontend::test_trd_12_v41_dashboard_js       PASSED
TestFrontend::test_trd_13_page_imports_component PASSED
TestFrontend::test_trd_14_component_has_sse      PASSED
TestFrontend::test_trd_15_v41_js_api_calls       PASSED

15 passed in 0.26s
```

---

## 완료 조건 체크

- [x] API 6개 엔드포인트 구현 (summary/positions/orders/performance/signals/stream)
- [x] GO100 프론트 /go100/trading/dashboard 페이지 생성
- [x] V4.1 프론트 dashboard.js 생성
- [x] SSE 스트림 연결 (new_trade + heartbeat 이벤트)
- [x] CEO 계정(user_id=2) 전체 조회, 일반 사용자 본인 데이터만
- [x] 단위 테스트 15건 ALL PASS
