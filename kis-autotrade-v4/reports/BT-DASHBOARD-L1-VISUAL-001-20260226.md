# BT-DASHBOARD-L1-VISUAL-001 구현 보고서

**프로젝트:** KIS AutoTrade V4.1  
**브랜치:** phase-2c-command-center  
**날짜:** 2026-02-26  
**우선순위:** P0 (CEO 직접 지시)  
**목표:** 백테스트 대시보드를 차트 중심 시각화 도구로 전면 재구성

---

## 1. 구현 요약

| # | 항목 | 상태 |
|---|------|------|
| 1 | admin.html 백업 (배포 서버에서 수동 실행) | 사용자 실행 |
| 2 | v4_stock_master 생성 + 종목명 수집 스크립트 | ✅ |
| 3 | bt_dashboard.py discoveries date/condition 필터 + 종목명 JOIN | ✅ |
| 4 | bt_dashboard.py trading-dates, daily-risk-log, data-coverage 추가 | ✅ |
| 5 | bt_chart.py strategy-compare 종목명 + timeframe 파라미터 | ✅ |
| 6 | AST 검증 통과 | ✅ |
| 7 | backtest-dashboard.js 전면 재작성 | ✅ |
| 8 | admin.css 시그널·캘린더·차트 스타일 추가 | ✅ |
| 9 | kis-v41-api 재시작 (CEO 승인 후 배포 서버에서 실행) | 사용자 실행 |
| 10 | L1-1~L1-3 브라우저 검증 | 배포 후 수행 |

---

## 2. 구현된 3개 화면 상세

### L1-1: 캘린더 히트맵 (메인)

- **위치:** `#bt-calendar-view`
- **구성:** 상단 KPI 카드 4개(세션, 총 거래수, 평균 승률, 실매매 준비도) + 세션 선택 드롭다운 + 월별 캘린더 그리드
- **동작:** `GET /api/v1/backtest/sessions/{session_id}/trading-dates` 로 일별 요약(발굴수, 거래수, 승수, 일PnL, halt, regime) 수신 후 캘린더 렌더링
- **캘린더 셀:** PnL > 0 녹색(#dcfce7), PnL < 0 적색(#fee2e2), 거래 0건 회색(#f9fafb), halt일 🚫 표시
- **클릭:** 날짜 클릭 → L1-2(일자별 발굴 리스트)로 전환

### L1-2: 일자별 발굴 종목 리스트

- **위치:** `#bt-daily-discovery-view`
- **구성:** 뒤로 버튼 + 날짜(요일) 헤더 + 조건 탭(C1~C7 + 전체) + 발굴 테이블 + 발굴 합계/탈락 사유
- **API:** `GET .../discovery-stats?date=YYYY-MM-DD`, `GET .../discoveries?date=...&condition_id=...&sort=score_desc&limit=100`
- **테이블 컬럼:** 순위 | 종목명(코드) | DESK점수 | 시각 | 통과(✅/❌) | 전략/탈락사유
- **클릭:** 행 클릭 → L1-3(전체화면 차트)로 전환

### L1-3: 전체화면 차트 + 시그널 패널

- **위치:** `#bt-fullchart-view`
- **구성:** 뒤로 버튼 + 종목명(코드) + 날짜 + 타임프레임 버튼(1m/3m/5m/10m/30m/60m/1d) + LightweightCharts 영역(60vh) + 시그널 패널
- **API:** `GET /api/v1/backtest/chart/strategy-compare/{session_id}/{stock_code}/{date}?timeframe=5m`
- **차트:** 캔들(한국식 상승 빨강/하락 파랑), 거래량 히스토그램, VWAP/BB/MA20 라인, 발굴/진입/청산 마커
- **시그널 패널:** 실행된 전략(진입가·청산가·수익률), 발굴 이력, 미실행 시그널

---

## 3. API 변경사항

### bt_dashboard.py

- **GET /sessions/{session_id}/discoveries**  
  - 쿼리: `date`, `condition_id`(또는 `condition_code`), `sort`(기본 `score_desc`), `limit`  
  - `v4_bt_discoveries` + `LEFT JOIN v4_stock_master` → `stock_name` 반환  
  - 정렬: `desk_score DESC NULLS LAST` 또는 `trade_date, trade_time`

- **GET /sessions/{session_id}/discovery-stats**  
  - 쿼리: `date`(선택)  
  - 응답 추가: `by_reject_reason` (탈락 사유별 건수)

- **GET /sessions/{session_id}/trades**  
  - `LEFT JOIN v4_stock_master` → `COALESCE(sm.stock_name, ...)` 로 종목명 반환

- **신규**  
  - `GET /sessions/{session_id}/daily-risk-log` — v4_bt_daily_risk_log 일별 halt/위반  
  - `GET /sessions/{session_id}/trading-dates` — 캘린더용 일별 요약(발굴수, 거래수, wins, daily_pnl_pct, halted, regime)  
  - `GET /data-coverage` — 6개 데이터셋 테이블 건수 + C1~C7 활성/비활성/부분 판정

### bt_chart.py

- **GET /strategy-compare/{session_id}/{stock_code}/{date}**  
  - `session_id`: 문자열(v4_bt_sessions.session_id)  
  - 쿼리: `timeframe`(기본 5m)  
  - `v4_stock_master` 조회 → `stock_name` 반환  
  - 응답: `candles`, `indicators`, `markers`, `trades`, `discoveries`, `unexecuted_signals`, `stock_name`

---

## 4. DB/스키마

- **v4_stock_master** (신규): `stock_code`(PK), `stock_name`, `market`, `updated_at`  
  - 마이그레이션: `backend/migrations/BT_DASHBOARD_L1_VISUAL_001_stock_master.sql`  
  - 수집 스크립트: `scripts/data_collect/collect_stock_master.py` (pykrx 기반 KOSPI/KOSDAQ)

---

## 5. 프론트엔드 파일

- **admin.html:** `#section-backtest` 를 L1-1/L1-2/L1-3/L2 뷰용 div 구조로 교체
- **backtest-dashboard.js:** 전면 재작성 — `initBacktestDashboard`, `navigateTo`, `loadCalendar`, `renderCalendar`, `renderSummaryCards`, `loadDailyDiscovery`, `loadDiscoveryList`, `renderDiscoveryTable`, `loadFullChart`, `renderFullScreenChart`, `renderSignalPanel`, `switchTimeframe`, `goBack` 등
- **admin.css:** bt-calendar, bt-condition-tabs, signal-panel, signal-card, badge, tf-btn, kpi-card-danger/warning/success 추가

---

## 6. 검증 방법

1. **배포 서버**  
   - `cp /var/www/trading.newtalk.kr/admin.html /var/www/trading.newtalk.kr/admin.html.bak.20260226`  
   - `cp /var/www/.../js/backtest-dashboard.js .../backtest-dashboard.js.bak.20260226`  
   - 프로젝트에서 빌드/배포 후 `systemctl restart kis-v41-api` (monitor/scheduler 재시작 금지)

2. **브라우저**  
   - `https://trading41.newtalk.kr/admin.html#backtest` (또는 해당 도메인)  
   - 세션 선택 → 캘린더 표시 → 날짜 클릭 → 발굴 리스트 → 종목 클릭 → 차트·시그널 확인 → 뒤로가기·타임프레임 전환

3. **종목 마스터**  
   - 서버에서: `pip install pykrx`, `python3 scripts/data_collect/collect_stock_master.py`  
   - `SELECT market, COUNT(*) FROM v4_stock_master GROUP BY market;` (KOSPI ~950, KOSDAQ ~1800 수준 기대)

---

## 7. 준수 사항

- kis-v41-monitor, kis-v41-scheduler 재시작 금지
- strategy_cards ALTER/DROP/DELETE 금지
- v4_positions 직접 수정 금지
- .env/.bak 커밋 금지
- `datetime.now(timezone.utc)` 사용, typing.Any 금지, f-string 로깅 금지
- 기존 API/프론트 기능 훼손 없음

---

**작성:** BT-DASHBOARD-L1-VISUAL-001 지시서 기준 구현 완료. 배포 및 브라우저 검증은 배포 환경에서 수행.
