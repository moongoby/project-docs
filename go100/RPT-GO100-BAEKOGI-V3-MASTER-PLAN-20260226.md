# 백억이(GO100) V3.0 천재 트레이더 마스터 플랜

**문서 ID**: RPT-GO100-BAEKOGI-V3-MASTER-PLAN-20260226  
**작성일**: 2026-02-26  
**목적**: v1→v4 버전 로드맵, V2/V3/V4 상세 설계, 데이터 수집·괴리 보정·안전장치·일정·KPI를 담은 통합 기획서

---

## 1. Executive Summary (1페이지)

GO100(백억이)은 **투자금 100억 달성**을 목표로 하는 AI 주식 트레이딩 어시스턴트다. KIS·키움 API 연동, 17개 인텐트, Goal/Portfolio/Regime/Paper/Live·대시보드·모니터링·Agentic 설계까지 **Phase 1~11**이 완료된 상태이며, **v2.0 분석가 → v3.0 트레이더 → v4.0 천재** 단계로 확장한다.

**핵심 전략**: (1) **멀티-모델 LLM**으로 대화(Opus 4.6)·요약(Sonnet 4)·전략가설(Opus T=0.9) 분리, (2) **크로스마켓 시그널**(SOX, USD/KRW, US10Y, CSI300)과 **이벤트-드리븐**(DART, FOMC/BOK, 뉴스)으로 시그널 품질 강화, (3) **경험 DB·괴리 보정 엔진**으로 백테스트-실매매 괴리 최소화(Month 3 ≤1.5%), (4) **전략 자동 진화**와 **5단계 과적합 방지**, (5) **환각 5중·실매매 3중·과적합 5단계** 안전장치 유지.

**즉시 조치**: 디스크 89% → 250GB 확장, 데이터 공백(backtest_runs/portfolios/positions/goals 0건) 해소, 인수인계서·본 기획서 project-docs 등록. **성공 기준**: 환각률 0%, Intent 정확도 ≥98%, 괴리 Month 3 ≤1.5%, A/B등급 전략 ≥60% 시 실매매 본격화.

---

## 2. 현재 시스템 진단

### 2.1 완료 Phase (Phase 1~11)

| Phase | 내용 | 상태 |
|-------|------|------|
| 1–3 | LLM 라우팅·폴백, 인텐트 15→17, data_queries·Gemini function-calling·response_filter | 완료 |
| 4 | response_formatter.py 응답 포매팅 표준화 | 완료 |
| 5 | Goal Engine, Portfolio Manager (go100_goals/portfolios/positions/strategy_portfolios/allocations/snapshots) | 완료 |
| 6 | regime_engine.py (5레짐×3프로필), proactive_reporter.py, go100_reports, 크론 모닝/장마감/주간/이벤트 | 완료 |
| 7 | Paper Trading (go100_paper_*), paper_trading.py, 크론 16:10 | 완료 |
| 8 | E2E 통합 검증 9/9·15/15·17/17 PASS | 완료 |
| 9 | 실매매 연동 (go100_live_*), live_trading.py, 7단계 안전장치 | 완료 |
| 10-A | dashboard_router 7 API, 프런트 7 컴포넌트, /go100/dashboard | 완료 |
| 10-B | go100_usage_logs, usage_logger, monitor_router 4 API, health_monitor 크론 | 완료 |
| 11 | agent_tools 21개, agent_core 5라운드, GO100_AGENT_MODE 토글 | 완료 |

### 2.2 DB 현황

- **go100_***: strategy_cards(3), backtest_runs(0), optimization_runs, goals(스키마만), portfolios(0), positions(0), strategy_portfolios, portfolio_allocations, portfolio_snapshots, global_market(0), reports, paper_*, live_*, usage_logs.
- **공용**: ohlcv_daily(다년치), stock_fundamentals(2,439), strategy_cards(62), v4_users(4), accounts(7), v4_positions(5), 분봉 파티션(0.75~1.15GB each).

### 2.3 데이터 공백

- go100_backtest_runs, go100_portfolios, go100_positions, go100_goals: **0건**.
- go100_global_market: **무데이터**.

### 2.4 인프라 제약

- **디스크**: 99GB SSD 사용률 89%(84GB) → 250GB 확장 필요(₩10,000/월).
- **서버**: Ubuntu 24.04, Xeon Gold 5220, 15GB RAM.

---

## 3. 버전 로드맵 (v1.0~v4.0)

| 버전 | 코드명 | 핵심 | 시기 |
|------|--------|------|------|
| v1.0 | 정보원 | 데이터 조회 | 완료 |
| v2.0 | 분석가 | LLM 자동판단·시그널·경험축적 | 1–4주 |
| v3.0 | 트레이더 | 전략 자동진화·크로스마켓·실매매 검증 | 4–10주 |
| v4.0 | 천재 | 자기복기·포트폴리오 최적화·개인화 | 10–16주 |

---

## 4. V2.0 상세 설계 (분석가)

### 4.1 Agentic 전환

- **Layer 0**: Gemini 2.0 Flash — 질문 분류(simple/data/analysis/action), 50–200ms.
- **simple/data**: 템플릿 또는 DB 조회 200–800ms.
- **analysis/action**: Claude Opus 4.6 Agent 2–5s, 21개 도구(agent_tools.py) 자동 선택·호출.
- **GO100_AGENT_MODE** env로 기존 플로우와 단계적 전환, 롤백 가능.

### 4.2 멀티-모델 LLM

- **대화/도구**: Claude Opus 4.6.
- **일일 요약/배치**: Claude Sonnet 4.
- **전략 가설 생성**: Claude Opus 4.6 temperature=0.9.
- 비용 절감 우선순위 제외, 시그널 정확도·체결 품질에 자원 집중.

### 4.3 크로스마켓 시그널

- **테이블**: go100_cross_market_signals, go100_signal_performance.
- **신호**: SOX→반도체, USD/KRW→외국인, US10Y→성장주, CSI300→중국.
- 매일 07:00 수집, 모닝 브리핑 반영; 정확도 55% 미만 시그널 제외.

### 4.4 경험 DB

- **go100_experience_log**: market_snapshot, action, outcome, regime, sector, strategy, source(backtest/paper/live), slippage_expected/actual, fill_rate, time_to_fill, overnight_gap_pct, volume_participation_pct, market_impact_pct 등.
- 매 거래(백테스트/페이퍼/실매매) 로깅하여 괴리 분석·보정 입력으로 사용.

### 4.5 데이터 수집 (V2 기반)

- 과거: 상장폐지 OHLCV, 분봉 1년(100종목), 틱 3개월(50종목), 투자자 매매동향 3년(200종목), PIT 재무 5년, 오버나이트 갭 MV.
- 실시간: 호가 5분 스냅샷, 체결 틱, 16:20 투자자동향, 16:30 당일 1분봉, 16:40/16:50 호가·틱 통계, 17:00 갭 MV 리프레시.

---

## 5. V3.0 상세 설계 (트레이더)

### 5.1 전략 자동 진화

- **strategy_evolution.py**: 매주 04:00 실행.
- 성과 평가 → 파라미터 변이 → LLM 전략 생성 → 자동 백테스트.
- **5단계 검증**: In-sample(3yr, Sharpe≥1) → Out-of-sample(1yr, 차이≤50%) → 레짐별 MDD → 외부 충격 시뮬 → 파라미터 민감도.
- 통과: CANDIDATE, 미통과: REJECTED.

### 5.2 이벤트-드리븐

- DART 공시 수집 → 과거 서프라이즈 통계 → 실시간 알림.
- 매크로 캘린더(FOMC, BOK) 연동, 뉴스 센티멘트 + 과거 통계.

### 5.3 백테스트-실매매 괴리 보정 엔진

- **go100_gap_analysis**: 동일 전략·종목·시점 backtest vs live/paper 괴리 자동 매칭.
- **gap_calibrator.py**: 60일 괴리 측정 → 슬리피지/거래량/갭 파라미터 자동 조정 → 신뢰도 A/B/C/D.
- **실매매 유니버스**: 시총 3천억+, 일 거래대금 30억+, 스프레드 0.3% 이내.
- **포지션 사이징**: A=100%, B=70%, C=40%, D=0%; D등급 실매매 차단.
- **프리마켓 재검증**: 08:30 야간 해외시장 대조 후 무효 시그널 취소.

---

## 6. V4.0 상세 설계 (천재)

### 6.1 경험 기반 판단·자기 복기

- 경험 DB 기반 사후 분석, 실패/성공 패턴 추출.
- 전략·레짐·시그널 파라미터 자동 보정.

### 6.2 포트폴리오 최적화

- 상관 매트릭스, CVaR, 스트레스 시뮬레이션.
- 신규 종목 편입 시 포트폴리오 영향 사전 예측.

### 6.3 개인화

- **go100_user_profile**: 리스크 성향, 보유 기간, 섹터 전문성, 자본 한도.
- 시스템 프롬프트·전략 파라미터에 자동 반영.

---

## 7. 데이터 수집 계획

### 7.1 과거 데이터 일괄 수집

| 데이터 | 소스 | 예상량 |
|--------|------|--------|
| 상장폐지 OHLCV | FinanceDataReader KRX-DELISTING | ~500MB |
| 과거 분봉 1년(100종목) | 키움 REST ka10080 | ~1.5GB |
| 과거 틱 3개월(50종목) | 키움 REST ka10079 | ~3–5GB |
| 투자자별 매매동향 3년(200종목) | KIS REST 종목별투자자매매동향(일별) | ~200MB |
| PIT 재무제표 5년 | DART OpenAPI + OpenDartReader | ~100MB |
| 오버나이트 갭 | ohlcv_daily MATERIALIZED VIEW | 0(뷰) |

### 7.2 실시간 수집 (장중)

| 데이터 | 소스 | 주기 | 월 증가량 |
|--------|------|------|----------|
| 호가 10단계 스냅샷 | KIS WebSocket 실시간-002 | 5분 | ~50MB |
| 체결 틱 | KIS WebSocket 실시간-003 | 실시간(배치 INSERT) | ~2–3GB |
| 투자자 매매동향 | KIS REST | 16:20 일 1회 | ~20MB |
| 당일 1분봉 | KIS REST | 16:30 일 1회 | 누적 |
| 호가 통계 집계 | 자체 계산 | 16:40 | 미미 |
| 틱 통계 집계 | 자체 계산 | 16:50 | 미미 |
| 오버나이트 갭 갱신 | MV REFRESH | 17:00 | 0 |

### 7.3 API 데이터 수집 가능 범위

- **KIS**: 일봉(기간 무제한, 1회 100건), 분봉(당일만 1분봉, 1회 30건), 호가(실시간만).
- **키움**: 일봉(무제한, 1회 900건), 분봉(1년치 다양한 간격), 틱(수개월), 호가(실시간만).
- 키움 OpenAPI+는 Windows 전용; REST(api.kiwoom.com)는 OS 무관.
- **사전 확인**: KIWOOM_APP_KEY/SECRET, DART_API_KEY, FinanceDataReader 설치 여부.

### 7.4 신규 테이블 목록

go100_delisted_ohlcv, go100_minute_bars, go100_tick_data(파티션), go100_investor_flow, go100_fundamentals_pit, go100_overnight_gap(MV), go100_orderbook_snapshots(파티션), go100_realtime_ticks(파티션), go100_orderbook_daily_stats, go100_tick_daily_stats, go100_cross_market_signals, go100_signal_performance, go100_experience_log, go100_gap_analysis, go100_calibration_params, go100_trading_cost_params, go100_user_profile.

---

## 8. 백테스트-실매매 동일 조건 설계

### 8.1 7가지 괴리(갭)

1. **체결가**: 종가 가정 vs 호가 스프레드.
2. **거래량 제약**: 소형주 시장충격 미반영.
3. **타이밍 지연**: 시그널 16:10 → 주문 익일 09:05(17시간 갭).
4. **비용 구조**: 슬리피지 0.1%(대형주) vs 소형주 0.3~0.5%.
5. **심리적 개입**: CEO 확인 지연.
6. **레짐 전환**: 일봉 단위 판단의 1~2일 지연.
7. **생존 편향**: 상장폐지 누락 → 연 2~3%p 과대 추정.

### 8.2 실매매 시뮬레이터급 백테스트

- **호가 기반 체결**: ask1/bid1, 잔량 초과 시 2호가~.
- **거래량 한도**: 대형 10%, 중형 5%, 소형 3%.
- **비용 일치**: KIS 동일(수수료 0.015%, 세금 0.18%, 슬리피지 실측).
- **PIT 유니버스**: 상장폐지 포함, IPO +5영업일 후 편입.
- **오버나이트 갭**: 익일 시가 기준 매매.
- **go100_trading_cost_params** 동적 로드.

### 8.3 괴리 보정

- gap_calibrator: 60일 괴리 측정 → gap_source 분류 → 슬리피지/거래량/갭 계수 조정 → go100_calibration_params 반영 → 신뢰도 A/B/C/D 부여.

---

## 9. 안전장치

### 9.1 환각 5중 방어

1. 시스템 프롬프트 절대 규칙.
2. 도구 결과 _source 메타데이터.
3. response_filter.py 강화(숫자 교차검증, 확정 예측 표현 교체).
4. data_integrity_check.py 일일 실행.
5. 사용 로그 + 주간 감사(환각률 목표 0%).

### 9.2 과적합 방지 5단계

In-sample(3yr, Sharpe≥1) → Out-of-sample(1yr, 차이≤50%) → 레짐별 MDD → 외부 충격 시뮬 → 파라미터 민감도.

### 9.3 실매매 삼중 방어

1. **서비스 내부**: circuit-breaker(일 손실 3%), 자동 stop-loss 주문.
2. **독립 watchdog**: systemd unit, 30s 체크 → 재시작 → API 청산 → 알림.
3. **증권사**: stop-loss, 주문 한도, 100% 증거금 사전 설정.

---

## 10. 인프라·운영

### 10.1 디스크

- 현재 99GB SSD 89% 사용 → 250GB 확장 즉시 신청.
- 파티션/로그 로테이션·과거 데이터 보관 정책 명확화.

### 10.2 크론

- 모닝 08:50, 장마감 15:40, 페이퍼 16:10, 투자자 16:20, 분봉 16:30, 호가/틱 집계 16:40/16:50, 갭 17:00, 주간 토 09:00, 전략 진화 일 04:00, 이벤트/헬스 */5 등 기존·신규 통합 관리.

### 10.3 LLM 비용

- ~$15/월(100유저) → 멀티모델 후 ~$35/월 예상.
- 수익 대비 운영비 1% 미만 목표, 정확도 우선.

### 10.4 Watchdog

- 30s 주기 체크, 이상 시 재시작·API 청산·알림, 증권사 한도와 병행 점검.

---

## 11. 주차별 실행 일정 (Week 0~16)

| 주차 | 구간 | 핵심 |
|------|------|------|
| Week 0 | 준비 | 디스크 확장, 크론 정리, 인수인계서·기획서 project-docs 등록 |
| Week 1 | v2 | Layer 0(Gemini 2.0 Flash) 질문 분류만 도입 |
| Week 2–3 | v2 | data 경로 템플릿/DB 조회 연동 |
| Week 4 | v2 | analysis/action → Opus 4.6 Agent, 21개 도구, GO100_AGENT_MODE 토글 |
| Week 5–6 | v2/v3 | 크로스마켓 시그널 수집·모닝 브리핑, 경험 DB 스키마·수집 |
| Week 7–8 | v3 | 전략 진화 5단계 검증, 이벤트 드리븐 수집·알림 |
| Week 9–10 | v3 | 실매매 시뮬레이터급 백테스트, gap_calibrator 측정·보정 |
| Week 11–12 | v3/v4 | 괴리 Month 2 ≤3%, 신뢰도 A/B/C/D 적용 |
| Week 13–14 | v4 | 자기 복기, 포트폴리오 최적화(상관/CVaR/스트레스) |
| Week 15–16 | v4 | go100_user_profile 개인화, 괴리 Month 3 ≤1.5%, A/B등급 ≥60% 검증 후 실매매 본격화 |

---

## 12. 성공 지표

| 지표 | 목표 |
|------|------|
| 환각률 | 0% |
| Intent 정확도 | ≥98% |
| 백테스트-실매매 괴리 | Month 1 ≤5%, Month 2 ≤3%, Month 3 ≤1.5% |
| 시그널 정확도(크로스마켓 등) | ≥55% 유지, 미달 시그널 제외 |
| 레이턴시 | simple <1s, data <2s, analysis <5s |
| A/B등급 전략 비율 | ≥60% 시 실매매 본격 가동 |

---

## 문서 위치

- **인수인계서**: `project-docs/go100/HANDOVER-V3-UPGRADE-20260226.md`
- **본 기획서**: `project-docs/go100/RPT-GO100-BAEKOGI-V3-MASTER-PLAN-20260226.md`
- **레포**: kis-autotrade-v4 (phase-2c-command-center), project-docs (master)
- **도메인**: https://go100.newtalk.kr

---

*문서 끝.*
