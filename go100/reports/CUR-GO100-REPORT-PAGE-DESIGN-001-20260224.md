# CUR-GO100-REPORT-PAGE-DESIGN-001 — GO100 리포트 페이지 기획서

**발행:** 2026-02-24  
**우선순위:** P1  
**목적:** GO100 사용자를 위한 리포트 페이지 기획 (코드 수정 없음, 현황 분석 + 기획서만 작성)

---

## 1. 현황

### 1.1 기존 /reports 페이지 (V4)

- **경로:** `frontend/src/app/(protected)/reports/page.tsx`
- **API:** `/api/v1/reports` (backend `report_router.py`)
- **기능 요약:**
  - **목록:** 일간(DAILY)/주간(WEEKLY) 필터, 페이지네이션(20건). `v4_reports` 테이블 기반.
  - **상세:** 리포트 ID 선택 시 `html_content` HTML 렌더 (다크 배경, prose-invert).
  - **수동 생성:** "일간 생성" / "주간 생성" 버튼 → `POST /reports/generate` → `report_generator.generate_daily_report` / `generate_weekly_report`.
  - **재발송:** "재발송" 버튼 → `POST /reports/{id}/resend` → `report_sender.send_report` (이메일/텔레그램/슬랙).
- **데이터 소스:** `v4_trades`, `v4_account_holdings`, `v4_positions` (유저별 매매·포트폴리오). GO100 전용 테이블(go100_*) 미사용.
- **면책:** 페이지 하단 "본 리포트는 GO100에서 생성되었습니다. 투자 판단과 책임은 이용자 본인에게 있으며, AI/알고리즘 기반 정보는 참고용입니다."

### 1.2 report_router.py API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/reports` | 목록 (report_type, page, size). v4_reports 조회. |
| GET | `/reports/{report_id}` | 상세 (html_content, report_data 포함). |
| POST | `/reports/generate` | 수동 생성 (body: report_type DAILY\|WEEKLY, report_date 선택). |
| POST | `/reports/{report_id}/resend` | 재발송 (이메일/텔레그램/슬랙). |

### 1.3 report_generator.py 기능

- **데이터:** `v4_trades` 기간 집계(`_aggregate_from_v4_trades`), 종목별 성과(`_breakdown_by_stock_from_v4_trades`), `v4_account_holdings`/`v4_positions` 포트폴리오 스냅샷, 단순 MDD.
- **출력:** HTML 템플릿(`templates/`) 기반 일간/주간 HTML 렌더 → `v4_reports` INSERT/ON CONFLICT UPDATE.
- **함수:** `generate_daily_report(user_id, report_date)`, `generate_weekly_report(user_id, week_start)`.

### 1.4 report_sender.py 기능

- **입력:** report_id → v4_reports에서 한 건 조회.
- **채널:** 이메일(HTML 본문), 텔레그램(요약 텍스트), 슬랙(Block Kit). 환경변수: TELEGRAM_BOT_TOKEN, SLACK_WEBHOOK_URL, 사용자 이메일은 v4_users.
- **함수:** `send_report(report_id)` → 반환 `{ sent: [], failed: [], report_id }`.

### 1.5 GO100 데이터 소스 현황

| 테이블명 | row_count | 비고 |
|----------|-----------|------|
| go100_strategy_cards | 8 | 전략카드 (BACKTESTED/IDEA/PAPER_LIVE/RETIRED 등) |
| go100_fit_analysis | 40 | 피트 분석 |
| go100_desk_allocation | 2 | 데스크 배분 |
| go100_portfolios | 1 | 포트폴리오 1건 |
| go100_orders | 0 | 주문 |
| go100_positions | 0 | 포지션 |
| go100_trades | 0 | 체결 거래 |
| go100_portfolio_snapshots | 0 | 포트폴리오 스냅샷 |
| go100_backtest_runs | 0 | 백테스트 런 |
| go100_optimization_runs | 0 | 최적화 런 |
| go100_notifications | 0 | 알림 |
| go100_notification_settings | 0 | 알림 설정 |
| go100_account_reconciliation | 0 | 계정 정합 |
| go100_push_subscriptions | 0 | 푸시 구독 |
| go100_risk_disclaimers | 0 | 리스크 면책 |

**전략카드 샘플 (2026-02-24 기준):**  
카드 13~20 존재. BACKTESTED(13,14,19), PAPER_LIVE(15), IDEA(16,17,18,20). last_backtest_return / last_backtest_mdd / last_backtest_sharpe / last_backtest_at 일부 보유(13,14,15). allocated_amount, max_stocks 등 스키마 있음.

**레짐:** `v4_market_regime_daily` 552건. 최근: SIDEWAYS(KOSPI), MILD_TREND_DOWN(KOSDAQ) 등.

**백테스트/최적화:** `go100_backtest_runs` 0건, `go100_optimization_runs` 0건. (추후 백테스트·최적화 실행 시 적재 예정.)

---

## 2. 사용자 분석

### 2.1 타겟 사용자

- 주식 투자 초보~중급.
- AI 자동매매(GO100)를 사용하는 개인 투자자.
- 투자 결과를 쉽게 이해하고 싶어함.
- 전문 용어보다 직관적 시각화 선호.

### 2.2 사용자가 알고 싶은 것 (핵심 질문별)

| 구분 | 사용자 질문 | 대응 데이터/기능 |
|------|-------------|------------------|
| **일간** | 오늘 매매 결과(종목, 수익/손실, 체결가, 수량) | go100_trades, go100_orders |
| 일간 | 오늘 포트폴리오 변동(총 자산, 평가손익, 수익률) | go100_portfolios, go100_portfolio_snapshots |
| 일간 | 오늘 시장 레짐(강세/약세/횡보) | v4_market_regime_daily |
| 일간 | 활성 전략 상태(어떤 전략이 돌고 있는지) | go100_strategy_cards (is_active, card_status) |
| **주간** | 주간 수익률 추이(일별 그래프) | go100_portfolio_snapshots 일별 |
| 주간 | 주간 매매 요약(총 거래 수, 승률, 평균 수익) | go100_trades 집계 |
| 주간 | 전략별 성과 비교 | go100_trades + go100_card_id |
| 주간 | 레짐 변화 타임라인 | v4_market_regime_daily |
| **월간** | 월간 수익률(벤치마크 대비) | 스냅샷 + 지수 데이터 |
| 월간 | 전략별 기여도, MDD/샤프 등 리스크 지표 | go100_portfolio_snapshots, 카드별 집계 |
| 월간 | 최적화 이력(백억이가 어떤 조정을 했는지) | go100_optimization_runs |
| **백테스트** | 카드별 백테스트 결과 이력 | go100_backtest_runs |
| 백테스트 | 최적화 전후 비교 | go100_optimization_runs |
| 백테스트 | 레짐별 성과 분석 | v4_backtest_regime_analysis |
| **종합** | 전체 자산, 전략 포트폴리오 구성, 리스크 모니터링 | go100_portfolios, 카드/포지션 요약 |

---

## 3. GO100 리포트 페이지 구성안

### 3.1 페이지 구조: /go100/reports

- **경로:** `/go100/reports` (기존 V4 `/reports`와 별도. GO100 전용.)
- **레이아웃:** 상단 탭 4개 — 일간 / 주간 / 월간 / 백테스트.

#### 탭 1: 일간 리포트

- **오늘의 매매** — 종목, 매수/매도, 체결가, 수량, 손익, 수익률 (go100_trades, go100_orders).
- **포트폴리오 현황** — 총 자산, 평가손익, 일간 수익률, 현금 비중 (go100_portfolios, go100_portfolio_snapshots).
- **시장 레짐** — 오늘 레짐(아이콘+설명), KOSPI/KOSDAQ 등 (v4_market_regime_daily).
- **활성 전략** — 전략명, 상태, 오늘 매매 건수 (go100_strategy_cards + go100_trades).
- **알림 요약** — 오늘 발생 알림(손절/익절/체결 등) (go100_notifications).

#### 탭 2: 주간 리포트

- **주간 수익률 차트** — 일별 누적 수익률 라인 차트 (go100_portfolio_snapshots).
- **주간 매매 요약** — 총 거래 수, 승률, 평균 수익, 최대 수익/손실 (go100_trades 집계).
- **전략별 성과 비교** — 바 차트(전략별 수익률).
- **레짐 타임라인** — 주간 레짐 변화 시각화 (v4_market_regime_daily).
- **주간 베스트/워스트** — 가장 수익 좋은/나쁜 종목.

#### 탭 3: 월간 리포트

- **월간 수익률** — 벤치마크(KOSPI) 대비 라인 차트.
- **전략별 기여도** — 파이 차트 또는 스택 바.
- **리스크 지표** — MDD, 샤프비율, 변동성.
- **최적화 이력** — 백억이 최적화 내역 타임라인 (go100_optimization_runs).
- **월간 종합 평가** — AI 한 줄 요약(Phase 4).

#### 탭 4: 백테스트 리포트

- **카드별 백테스트 이력** — go100_backtest_runs 기반.
- **최적화 전후 비교** — go100_optimization_runs 기반.
- **레짐별 성과** — v4_backtest_regime_analysis 기반 (기존 백테스트 분석 API 활용).
- **수익 곡선** — Lightweight Charts 활용.

#### 공통 기능

- **PDF 다운로드** — 각 탭 리포트를 PDF로 저장.
- **이메일 발송** — 기존 report_sender 활용 또는 GO100 전용 발송.
- **자동 리포트** — 매일/매주/매월 자동 생성 + 이메일 발송(알림 설정과 연동).
- **기간 선택** — 커스텀 기간 리포트 생성.

---

## 4. 필요한 신규 API

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /api/go100/reports/daily | 일간 리포트 데이터 (날짜 쿼리) |
| GET | /api/go100/reports/weekly | 주간 리포트 데이터 (주 시작일 쿼리) |
| GET | /api/go100/reports/monthly | 월간 리포트 데이터 (년월 쿼리) |
| GET | /api/go100/reports/backtest-history | 백테스트 이력 (카드/기간 필터) |
| GET | /api/go100/reports/optimization-history | 최적화 이력 (카드 필터) |
| POST | /api/go100/reports/generate-pdf | PDF 생성 (탭/기간 지정) |
| POST | /api/go100/reports/send-email | 이메일 발송 (리포트 ID 또는 생성 옵션) |

---

## 5. 필요한 프론트 컴포넌트

| 컴포넌트 | 설명 |
|----------|------|
| /go100/reports/page.tsx | 리포트 메인 (탭 구조) |
| DailyReportTab.tsx | 일간 리포트 탭 |
| WeeklyReportTab.tsx | 주간 리포트 탭 |
| MonthlyReportTab.tsx | 월간 리포트 탭 |
| BacktestReportTab.tsx | 백테스트 리포트 탭 |
| ReportEquityChart.tsx | 수익 곡선 차트 |
| ReportTradeTable.tsx | 매매 내역 테이블 |
| ReportRegimeTimeline.tsx | 레짐 타임라인 |
| ReportStrategyComparison.tsx | 전략 비교 차트 |
| ReportPdfButton.tsx | PDF 다운로드 버튼 |

---

## 6. 데이터 의존성

| 데이터 | 소스 테이블 | 현재 상태 |
|--------|-------------|----------|
| 매매 내역 | go100_orders, go100_trades | 0건 |
| 포지션 | go100_positions | 0건 |
| 포트폴리오 | go100_portfolios, go100_portfolio_snapshots | 1건, 0건 |
| 백테스트 | go100_backtest_runs | 0건 |
| 최적화 | go100_optimization_runs | 0건 |
| 레짐 | v4_market_regime_daily | 552건 |
| 알림 | go100_notifications | 0건 |
| 전략카드 | go100_strategy_cards | 8건 |
| 레짐별 백테스트 | v4_backtest_regime_analysis | (백테스트 실행·분석 후 적재) |

---

## 7. 구현 우선순위

1. **Phase 1 (MVP):** 백테스트 리포트 탭 — go100_backtest_runs 데이터 활용. (현재 0건이므로 스키마·API·UI 먼저 구현, 데이터 적재 후 연동.) v4_backtest_regime_analysis 연동 시 레짐별 성과 표시.
2. **Phase 2:** 일간 리포트 — 매매/포지션/스냅샷 시작 후 (go100_trades 등 적재 후).
3. **Phase 3:** 주간/월간 리포트 + PDF + 이메일.
4. **Phase 4:** AI 요약(백억이가 리포트 코멘트 생성).

---

## 8. 참고

- 기존 V4 `/reports`: 일간/주간 성과, v4_trades 기반, 수동 생성, 이메일 재발송. GO100 전용 테이블 미사용.
- GO100 전용 `/go100/reports` 페이지를 별도로 두어 V4 `/reports`와 독립적으로 운영.
- Lightweight Charts 라이브러리 활용(오전 차트 작업에서 이미 도입됨).
- report_sender: 이메일(HTML), 텔레그램(요약), 슬랙(Block Kit). GO100 리포트용으로 확장 시 채널 재사용 가능.
