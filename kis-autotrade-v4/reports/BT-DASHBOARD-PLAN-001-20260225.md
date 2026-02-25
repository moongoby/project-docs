# 백테스트 분석 대시보드 기획서

- 문서번호: BT-DASHBOARD-PLAN-001
- 작성일: 2026-02-25
- 작성자: CEO
- 상태: 승인 → 구현 착수
- 프로젝트: KIS AutoTrade V4.1

---

## 1. 기획 배경

현재 백테스트 결과 확인은 서버 SSH 접속 → 로그 파일 직접 조회로만 가능하다.
CEO가 실시간으로 백테스트 진행 상황과 결과를 확인하고,
전략의 실매매 전환 여부를 판단할 수 있는 관리자 대시보드가 필요하다.

## 2. 핵심 철학

결과만 보여주는 것이 아니라, **전략 의도 검증**과 **실매매 전환 근거**를 제공한다.
단순 수익률 나열이 아닌 "왜 이 거래가 발생했고, 의도대로 작동했는가"를 추적한다.

## 3. CEO 7대 질문 (대시보드 설계 기준)

### Q1. 각 데스크가 어떤 종목을 발굴·추천하는가?
- 조건별(C1~C7) 발굴 현황 시각화
- 발굴 빈도, 전략 전달률, 상위 발굴 종목 Top 20
- 일별 발굴 히트맵 (날짜 × 조건코드)

### Q2. 각 전략이 어떤 타이밍에 들어갔는가? 익절/청산은 어떻게 했는가?
- 거래 카드: 진입시간 → 청산시간, 진입가 → 청산가, 수익률, 보유시간
- 진입 사유(entry_reason), 청산 사유(exit_reason) 명시
- 청산 유형별 분석: TARGET_PROFIT, STOP_LOSS, TIMEOUT, TRAILING, MANUAL
- 시간대별 진입/청산 분포 히스토그램

### Q3. 각각의 매매가 정확한 의도에 의해 이루어졌는가? 거래 횟수는?
- 의도 매칭 게이지 (0~100%)
- 의도 거래 vs 비의도 거래 비율
- 비의도 거래 목록 (원인, 의도점수)
- 비의도 비율 > 20% 시 경고 배너

### Q4. 의도한 거래의 수익률은?
- 전략별 수익률 비교 차트
- 의도별 수익률 비교 (INTENDED vs UNINTENDED)
- 시간대별 수익률 히트맵
- 에쿼티 커브 (일별 누적 PnL)

### Q5. 테스트 결과가 목표에 도달했는가? 미달 시 문제점과 수정 방향은?
- 6개 성공 기준 게이지:
  - 평균 수익률 E ≥ 0.3%
  - Calmar Ratio ≥ 1.5
  - Profit Factor ≥ 1.3
  - 최대 일손실 ≤ -3%
  - 일평균 거래수 2~5건
  - OOS/IS 비율 ≥ 0.6
- 미달 항목 자동 진단 + 파라미터 조정 제안

### Q6. 수익률 목표는 계속 올라가고 있는가?
- 세션별(버전별) 수익률 추이 라인 차트
- 파라미터 변경 이력 타임라인 (before/after 비교)
- 개선(↑ 녹색) / 악화(↓ 빨간색) 표시
- 수렴/발산 경고

### Q7. 실테스트가 가능한가? 실매매 기대 수익은?
- 5개 체크리스트 자동 판정:
  - 백테스트 1개 이상 PASS
  - OOS/IS ≥ 0.6 (과적합 아님)
  - 최대 일손실 ≤ -3%
  - Phase 3 스케줄러 등록
  - 서비스 정상 가동
- 전략별 기대수익 시뮬레이션 (보수적/중립/낙관 3단계)
- "실매매 전환" 버튼 (모든 조건 충족 시 활성화)

## 4. 추가 분석 기능 (베스트 프랙티스 연구 반영)

### 4.1 전략 상관관계 분석
- 전략 간 수익률 상관관계 히트맵
- 동시 손실 발생 빈도 (테일 리스크)
- 포트폴리오 분산 효과 측정

### 4.2 시장 레짐별 성과
- BULL/BEAR/SIDEWAYS/VOLATILE 레짐별 전략 수익률
- 레짐 전환 시점에서의 전략 적응력

### 4.3 슬리피지·체결 시뮬레이션
- 이론 체결가 vs 예상 실체결가 차이
- 호가 스프레드, 체결 지연 반영
- 실매매 전환 시 예상 성과 감소율

### 4.4 드로다운 원인 분석
- 최대 드로다운 구간 상세 (어떤 거래들이 연속 손실을 만들었는가)
- 드로다운 회복 시간 분석

### 4.5 캘린더 효과
- 요일별/월별/분기말 성과 차이
- 특정 이벤트(배당, 만기일, FOMC) 전후 성과

### 4.6 알림·이상 감지
- 비정상 거래 패턴 자동 감지
- 연속 손실 N회 이상 시 경고
- 거래 빈도 급변 시 경고

## 5. 데이터 모델

### 5.1 v4_bt_sessions (백테스트 세션)
세션 메타정보, 파라미터, 성과 지표, 목표 달성 여부를 저장한다.
주요 필드: session_id, strategy_name, status(RUNNING/PASS/FAIL),
start_date, end_date, capital, total_trades, win_rate,
avg_return_pct, total_return_pct, max_drawdown_pct,
calmar_ratio, profit_factor, max_daily_loss_pct,
avg_trades_per_day, oos_is_ratio, sharpe_ratio,
pass_criteria, fail_reasons, parameters, risk_params.

### 5.2 v4_bt_discoveries (발굴 기록)
조건별 종목 발굴 이력을 기록한다.
주요 필드: session_id, trade_date, stock_code, condition_code,
condition_score, desk_score, cs_score,
c1~c7 상세 지표, passed_to_strategy, reject_reason.

### 5.3 v4_bt_trades (거래 기록)
진입부터 청산까지 전체 거래 이력과 의도 검증을 기록한다.
주요 필드: session_id, trade_id, stock_code, strategy_name,
entry/exit 가격·시간·사유, pnl, pnl_pct, hold_seconds,
max_profit_pct, max_loss_pct,
intended_entry, intended_exit, intent_match_score.

### 5.4 v4_bt_versions (버전 이력)
파라미터 변경 전후 성과 비교를 기록한다.
주요 필드: version_tag, strategy_name, change_type,
parameters_before/after, return/calmar/pf before/after,
improvement, improvement_pct.

## 6. API 설계

### 6.1 세션 관리
- GET /api/v1/backtest/sessions – 세션 목록 (전략·상태 필터)
- GET /api/v1/backtest/sessions/{id} – 세션 상세

### 6.2 Q1 발굴 분석
- GET /api/v1/backtest/sessions/{id}/discoveries – 발굴 기록
- GET /api/v1/backtest/sessions/{id}/discovery-stats – 발굴 통계

### 6.3 Q2 거래 분석
- GET /api/v1/backtest/sessions/{id}/trades – 거래 목록
- GET /api/v1/backtest/sessions/{id}/exit-analysis – 청산 분석

### 6.4 Q3 의도 검증
- GET /api/v1/backtest/sessions/{id}/intent-analysis – 의도 분석

### 6.5 Q4 수익률 분석
- GET /api/v1/backtest/sessions/{id}/performance – 수익률
- GET /api/v1/backtest/sessions/{id}/daily-pnl – 일별 PnL

### 6.6 Q5 목표 추적
- GET /api/v1/backtest/sessions/{id}/goal-tracking – 목표 달성

### 6.7 Q6 추이 분석
- GET /api/v1/backtest/trend – 버전별 추이
- GET /api/v1/backtest/trend/sessions – 세션별 추이

### 6.8 Q7 실매매 준비도
- GET /api/v1/backtest/readiness – 준비도 판정

## 7. 프론트엔드 구조

### 7.1 페이지 구조
- /admin/backtest – 세션 목록 (필터, 카드 뷰)
- /admin/backtest/{sessionId} – 세션 상세 (7개 탭)

### 7.2 컴포넌트 (10개)
SessionList, DiscoveryPanel, TradeTimeline, IntentVerification,
PerformancePanel, GoalTracking, TrendChart, ReadinessCheck,
DailyPnlChart, ExitAnalysis

### 7.3 색상 규칙
- PASS/이익: 녹색 (#10B981)
- FAIL/손실: 빨간색 (#EF4444)
- RUNNING/진행: 파란색 (#3B82F6)
- 경고: 노란색 (#F59E0B)

## 8. 구현 우선순위

### Phase 1 (Day 1~3) – 즉시
DB 테이블 4개 생성, BtDataWriter 모듈, 기본 API 11개,
세션 목록 UI, 거래 목록 UI

### Phase 2 (Day 4~6)
의도 검증 로직, 목표 게이지 UI, 거래 카드 상세,
발굴 통계 차트, 청산 분석 차트

### Phase 3 (Day 7~8)
에쿼티 커브, 수익률 추이 차트,
실매매 체크리스트, 기대수익 시뮬레이터

### Phase 4 (Day 9~10)
레짐별 분석, 전략 상관관계, 슬리피지 시뮬,
캘린더 효과, 알림 시스템

## 9. 성공 기준

- CEO가 서버 접속 없이 관리자 페이지에서 백테스트 현황을 실시간 확인 가능
- 7대 질문 각각에 대한 답이 대시보드에서 즉시 확인 가능
- 실매매 전환 결정을 데이터 기반으로 내릴 수 있는 근거 제공
- 전략 개선 이력 추적으로 최적화 방향성 확인 가능

## 10. 변경 이력

| 날짜 | 버전 | 내용 |
|------|------|------|
| 2026-02-25 | v1.0 | 최초 작성, CEO 승인 후 구현 착수 |
