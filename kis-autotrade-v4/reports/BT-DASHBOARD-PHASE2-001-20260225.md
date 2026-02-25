# BT-DASHBOARD-PHASE2-001 백테스트 대시보드 Phase 2 구현 보고서

- **프로젝트:** KIS AutoTrade V4.1
- **브랜치:** phase-2c-command-center
- **작성일:** 2026-02-25
- **지시서:** BT-DASHBOARD-PHASE2-001
- **우선순위:** P1

---

## 1. 의도 검증 로직 설계 및 구현

### 1.1 BtIntentAnalyzer 모듈

**파일:** `backend/app/services/trading/desk2/tests/bt_intent_analyzer.py`

- **진입 의도 (intended_entry)**
  - 조건 1: `desk_score >= 70` → intended
  - 조건 2: `cs_score >= 55` → intended
  - 조건 3: 진입 시간 `09:15~14:30` → intended
  - 판정:
    - 3개 충족 → `intended_entry=True`, score 100
    - 2개 충족 → `intended_entry=True`, score 75
    - 1개 충족 → `intended_entry=False`, score 50
    - 0개 충족 → `intended_entry=False`, score 25

- **청산 의도 (intended_exit)**
  - `TARGET_PROFIT` → intended, score 100
  - `TRAILING_STOP` → intended, score 90
  - `STOP_LOSS` → intended, score 80
  - `TIMEOUT` → unintended, score 40
  - `DAILY_LIMIT` → unintended, score 30

- **intent_match_score** = (entry_score + exit_score) / 2

- **공개 API**
  - `analyze_entry_intent(desk_score, cs_score, entry_time) -> (intended: bool, score: float, notes: str)`
  - `analyze_exit_intent(exit_type) -> (intended: bool, score: float, notes: str)`
  - `analyze_trade(trade_data: dict) -> dict` (intended_entry, intended_exit, intent_match_score, intent_notes 반환)

- **규칙 준수:** `datetime.now(timezone.utc)`, `Any`, f-string 로깅 미사용

---

## 2. 신규 API 3개 상세

**파일:** `backend/app/routers/bt_dashboard.py`

### 2.1 거래 상세 API

- **엔드포인트:** `GET /api/v1/backtest/sessions/{session_id}/trades/{trade_id}`
- **설명:** 단일 거래 상세 (진입 신호, 청산 사유, 지표 스냅샷)
- **응답:** `{ "trade": { ... } }` 또는 `{ "error": "Trade not found" }`
- **SQL:** `v4_bt_trades`에서 `session_id`, `trade_id`로 1건 조회 (entry_signals, exit_reason, exit_type 등 전체 컬럼)

### 2.2 전략 비교 API

- **엔드포인트:** `GET /api/v1/backtest/compare?session_ids=id1,id2,...`
- **설명:** 복수 세션 성과 비교 (전략별 side-by-side 지표)
- **쿼리 파라미터:** `session_ids` (쉼표 구분, 최대 10개)
- **응답:** `{ "count": N, "sessions": [ ... ] }` — session_id, strategy_name, status, total_trades, win_rate, total_return_pct, calmar_ratio, profit_factor 등

### 2.3 일별 거래 상세 API

- **엔드포인트:** `GET /api/v1/backtest/sessions/{session_id}/daily/{date}`
- **설명:** 특정 날짜 거래 목록 + 해당일 PnL
- **응답:**
  - `date`: 요청한 날짜
  - `trades`: 해당일 `entry_date = date`인 거래 목록 (entry_time 순)
  - `summary`: trade_count, daily_pnl, avg_pnl_pct, wins, losses

---

## 3. 프론트엔드 컴포넌트 5개 구현

### 3.1 GoalTracking.tsx

- 6개 원형 게이지 (recharts `RadialBarChart`)
- 각 게이지: 현재값/목표값 표시, PASS=녹색, FAIL=빨간색
- 미달 항목: 진단 메시지 + 파라미터 제안 카드

### 3.2 TradeTimeline.tsx

- 거래 카드 리스트, 클릭 시 상세 펼침 (useTradeDetail)
- 카드: 종목명, 진입→청산 화살표, 가격, 수익률
- 진입 사유 태그, 청산 유형 배지, 보유 시간 프로그레스 바

### 3.3 DiscoveryPanel.tsx

- 조건별 바 차트 (C1~C7 발굴 건수)
- 전달률 도넛 차트 (발굴→전략 전달 비율)
- Top 20 종목 테이블

### 3.4 ExitAnalysis.tsx (신규)

- 청산 유형별 파이 차트
- 유형별 평균 수익률 바 차트
- 유형별 평균 보유 시간 바 차트
- 세션 상세 탭에 "청산 분석" 탭으로 추가

### 3.5 IntentVerification.tsx

- 의도 매칭 대형 게이지 (0~100%, RadialBarChart)
- INTENDED vs UNINTENDED 도넛 차트
- 비의도 거래 테이블 (정렬: intent_score ASC)
- 경고 배너 (비의도 > 20%)

---

## 4. 빌드 결과

- **명령:** `cd /root/kis-autotrade-v4/frontend && npm run build`
- **결과:** ✓ Compiled successfully, ✓ Generating static pages (34/34)
- **에러:** 0
- **컴포넌트 파일 수:** 8개 (`src/components/admin/backtest/*.tsx`)

---

## 5. 소스 검수 결과

| 항목 | 결과 |
|------|------|
| bt_intent_analyzer.py 판정 로직 | 진입 3요건/청산 5유형 명세대로 구현, 반환 타입 명확 |
| bt_dashboard.py 신규 API 3개 SQL | session_id/trade_id/date 조건 정확, v4_bt_trades/sessions만 사용 |
| 프론트 API 호출 경로 | `/api/v1/backtest/sessions/:id/trades/:tid`, `/compare`, `/sessions/:id/daily/:date` 사용 |
| recharts import | RadialBarChart, RadialBar, PieChart, Pie, BarChart, Bar, ResponsiveContainer, Tooltip, Legend, Cell 등 정상 사용 |

---

## 6. 완료 체크리스트

- [x] Phase 1 API 정상 동작 확인 (sessions, readiness, health)
- [x] BtIntentAnalyzer 구현
- [x] 신규 API 3개 추가 (거래 상세, 전략 비교, 일별 거래)
- [x] 프론트엔드 컴포넌트 5개 완성 (GoalTracking, TradeTimeline, DiscoveryPanel, ExitAnalysis, IntentVerification)
- [x] npm run build 에러 0
- [x] 소스 검수 완료
- [ ] 보고서 push curl 200 (Push 후 확인)

---

*서비스 재시작 없음. strategy_cards, v4_positions 미변경.*
