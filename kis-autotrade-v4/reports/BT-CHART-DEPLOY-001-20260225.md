# BT-CHART-DEPLOY-001 백테스트 차트 배포 보고서
**작성일:** 2026-02-25
**우선순위:** P0 (CEO 차트 확인 지시)

## 1. 사전 확인
- **서비스:** kis-v41-api, kis-v41-monitor, kis-v41-scheduler 모두 `active`
- **strategy_cards:** 60건 (기대값 일치)
- **v4_positions OPEN:** 11건 (기대값 일치)
- **차트 관련 테이블:** v4_bt_sessions 3, v4_bt_trades 106, v4_bt_discoveries 6922, v4_bt_discovery_log 46657, v4_bt_daily_risk_log 24
- **최신 세션:** BT-DESK2-HARVEST-SHORT--20260225104710 (id=3, total_trades=101)
- **차트용 TRADE_ID:** 6 (v4_bt_trades.id 또는 trade_id 문자열), DISCOVERY_ID: 1

## 2. 라우터 등록
- **bt_chart_router:** main.py 100행 import, 390행 `app.include_router(bt_chart_router, prefix="/api/v1/backtest/chart")` 등록됨
- **bt_dashboard_router:** 99행 import, 389행 등록됨
- **AST 검증:** main.py, bt_chart.py, bt_dashboard.py 모두 OK

## 3. 프론트 빌드
- 백테스트 페이지: `(protected)/admin/backtest/`, `trades/[tradeId]`, `charts/`, `daily/`, `discovery/` 존재
- 컴포넌트: TimeframeSelector, TradeInfoPanel, DiscoveryPanel, TradeTimeline, GoalTracking, BacktestTradeChart 등 존재
- backtestChartApi.ts 존재 및 BASE="/api/v1/backtest/chart"
- `npm run build` 완료, 에러 0

## 4. API 재시작 (CEO 승인)
- 재시작 시각: 2026-02-25 (배포 시점)
- `systemctl restart kis-v41-api` 실행 후 5초 대기
- `systemctl is-active kis-v41-api` → active
- `/health` → 200, status ok, database/redis connected
- monitor/scheduler 재시작 없음, 둘 다 active 유지

## 5. API 엔드포인트 확인
| 엔드포인트 | 결과 | 비고 |
|------------|------|------|
| GET /api/v1/backtest/sessions?limit=5 | 200 | count=3, 세션 목록 정상 |
| GET /api/v1/backtest/sessions/{session_id} | 200 | 세션 상세 정상 |
| GET /api/v1/backtest/chart/trade/6 | 200 | candles, markers, highlightRanges, indicators, trade_info 포함 |
| GET /api/v1/backtest/chart/trade/6/timeframe/5m | 200 | 5분봉 리샘플 캔들 정상 |
| GET /api/v1/backtest/chart/discovery/1 | 200 | candles, markers, discovery_info, lifecycle |
| GET /api/v1/backtest/chart/daily-summary/3/20260106 | 200 | trades 배열, candles(해당일 KOSPI), discoveries |
| GET /api/v1/backtest/sessions/{id}/goal-tracking | 200 | criteria, all_pass, diagnostics |
| GET /api/v1/backtest/readiness | 200 | all_ready, checklist, strategies |

**배포 중 수정 사항:**
- `v4_bt_trades`에 없는 컬럼 `desk_score` 제거, trade 조회 시 경로 인자로 `id`(숫자) 지원 추가 (WHERE id = :tid 또는 trade_id = :tid)
- daily-summary: 경로 `session_id`는 v4_bt_sessions.id(정수). 내부에서 session_id 문자열 조회 후 v4_bt_trades 조회에 사용하도록 수정
- daily-summary: `trades_result.mappings().fetchall()` 동기 호출로 수정 (await 제거)
- strategy-compare: 동일하게 session_id 정수 → 문자열 조회 후 사용

## 6. 프론트 접속 확인
- `curl -s -o /dev/null -w "%{http_code}" https://trading41.newtalk.kr/admin/backtest` → **200**
- Next 빌드 디렉터리 `.next/` 존재, next-server 프로세스 동작 확인

## 7. CEO 접속 경로
- **백테스트 대시보드:** https://trading41.newtalk.kr/admin/backtest
- 세션 선택 후 거래 클릭 → 차트 보기
- 발굴 탭 → 차트 보기
- 일일 타임라인 → 날짜 클릭 시 daily-summary (session_id는 세션 목록의 id 값 사용, 예: 3)

## 완료 체크리스트
| # | 항목 | 확인 |
|---|------|------|
| 1 | DB 데이터 확인 (세션/거래/발굴) | ✅ |
| 2 | bt_chart.py + bt_dashboard.py 라우터 등록 | ✅ |
| 3 | npm run build 에러 0 | ✅ |
| 4 | kis-v41-api 재시작 (CEO 승인) | ✅ |
| 5 | health 200 | ✅ |
| 6 | /api/v1/backtest/sessions 200 | ✅ |
| 7 | /api/v1/backtest/chart/trade/{id} 200 + 캔들 데이터 | ✅ |
| 8 | /api/v1/backtest/chart/discovery/{id} 200 | ✅ |
| 9 | /api/v1/backtest/chart/daily-summary 200 | ✅ |
| 10 | 프론트 /admin/backtest 접속 가능 | ✅ |
| 11 | 보고서 push + URL 200 | (아래 수행) |
| 12 | monitor/scheduler 영향 없음 (재시작 안 함) | ✅ |
