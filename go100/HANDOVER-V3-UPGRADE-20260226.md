# GO100(백억이) V3.0 업그레이드 인수인계서

**문서 ID**: HANDOVER-V3-UPGRADE-20260226  
**작성일**: 2026-02-26  
**목적**: GO100 프로젝트 현황·완료 Phase·DB·이슈·V3.0 확정 사항을 한 문서로 정리한 인수인계용 문서

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | GO100 (백억이) — AI 주식 트레이딩 어시스턴트 |
| **목표** | 투자금 100억 달성을 돕는 AI 트레이더 |
| **코드 레포** | kis-autotrade-v4 (브랜치: phase-2c-command-center) |
| **문서 레포** | project-docs (master) |
| **서버** | Ubuntu 24.04, Xeon Gold 5220, 15GB RAM, 99GB SSD → 250GB 확장 예정(₩10,000/월) |
| **DB** | PostgreSQL 16, kisautotrade, kis_admin, localhost:5432 |
| **서비스** | go100 (backend), go100-frontend (Next.js), Redis |
| **도메인** | https://go100.newtalk.kr |

---

## 2. 완료된 Phase 목록 (Phase 1~11)

### Wave 1–3 (완료)
- LLM 라우팅 폴백, 종목조회 핸들러, 인텐트 15→17개 확장
- 비동기 data_queries, Gemini function-calling, response_filter
- 대표 커밋: 0a7b5b34, 3ce667fe, bf4cd9b6 등

### Phase 4: 응답 포매팅 표준화
- response_formatter.py (헤더/푸터 포맷)

### Phase 5: Goal Engine + Portfolio Manager
- 테이블: go100_goals, go100_portfolios, go100_positions, go100_strategy_portfolios, go100_portfolio_allocations, go100_portfolio_snapshots
- 모듈: goal_engine.py, portfolio_manager.py

### Phase 6: Regime Engine + Proactive Reporter
- C-3: regime_engine.py (5레짐×3프로필=15조합)
- C-4: proactive_reporter.py, go100_reports 테이블
- 크론: 모닝(08:50), 장마감(15:40), 주간(토 09:00), 이벤트(*/5)

### Phase 7: Paper Trading
- go100_paper_accounts / orders / positions / snapshots
- paper_trading.py, 크론 16:10 장마감 후

### Phase 8: E2E 통합 검증
- 모듈 9/9, DB 15/15, 인텐트 17/17 PASS
- 디스크 89% (84GB/99GB) — 주의

### Phase 9: 실매매 연동
- go100_live_trading_config / orders / daily_summary
- live_trading.py, 7단계 안전장치, KIS V4 OrderService 재사용
- 인텐트: live_start / status / stop / enable

### Phase 10-A: 성과 대시보드
- dashboard_router.py (7 API), 프런트 7 컴포넌트, recharts
- 라우트: /go100/dashboard

### Phase 10-B: 베타 모니터링
- go100_usage_logs, usage_logger.py, monitor_router.py (4 API)
- health_monitor.py (5분 크론), 베타 체크리스트

### Phase 11: Agentic Architecture 설계
- agent_tools.py (21개 도구), agent_core.py (최대 5라운드)
- GO100_AGENT_MODE 환경변수 토글

### 기타 완료
- 크론 6건 신규 등록 완료
- 디스크 D-2 긴급 정리 실행 완료
- 베타 테스트 Round 1 완료, 인수인계 문서 커밋 완료

---

## 3. 현재 DB 테이블 (go100_*)

| 구분 | 테이블 | 비고 |
|------|--------|------|
| 전략/백테스트 | go100_strategy_cards(3), go100_backtest_runs(0), go100_optimization_runs | |
| 목표/포트폴리오 | go100_goals(스키마만), go100_portfolios(0), go100_positions(0) | 데이터 0건 |
| 전략·스냅샷 | go100_strategy_portfolios, go100_portfolio_allocations, go100_portfolio_snapshots | |
| 시장·리포트 | go100_global_market(0), go100_reports | |
| 페이퍼 | go100_paper_accounts / orders / positions / snapshots | |
| 실매매 | go100_live_trading_config / orders / daily_summary | |
| 모니터링 | go100_usage_logs | |
| 기존 공용 | ohlcv_daily(다년치), stock_fundamentals(2,439), strategy_cards(62), v4_users(4), accounts(7), v4_positions(5), 분봉 파티션(0.75~1.15GB each) | |

---

## 4. LLM 스택

- **인텐트 분류**: Gemini 2.5 Flash (폴백: Claude Haiku)
- **전략 검증**: Claude Opus 4.6
- **비용**: 약 $15/월 (100유저 기준)

---

## 5. 핵심 이슈

1. **디스크 89%** — 250GB 확장 필요
2. **데이터 공백**: backtest_runs / portfolios / positions / goals 모두 0건
3. **go100_global_market** 무데이터
4. **인수인계 원문 2개** project-docs 등록 필요

---

## 6. V3.0 기획 확정 사항 (합의본)

### 6-1. 비용 관점
- LLM 비용 절감은 우선순위 제외. 수익 대비 운영비 1% 미만
- 시그널 정확도·체결 품질에 자원 집중

### 6-2. 버전 로드맵
| 버전 | 코드명 | 핵심 | 시기 |
|------|--------|------|------|
| v1.0 | 정보원 | 데이터 조회 | 완료 |
| v2.0 | 분석가 | LLM 자동판단·시그널·경험축적 | 1–4주 |
| v3.0 | 트레이더 | 전략 자동진화·크로스마켓·실매매 검증 | 4–10주 |
| v4.0 | 천재 | 자기복기·포트폴리오 최적화·개인화 | 10–16주 |

### 6-3. 6대 핵심 레이어 (대표 지시)
1. **멀티-모델 LLM**: Opus 4.6(대화/도구), Sonnet 4(일일 요약), Opus 4.6 T=0.9(전략 가설)
2. **크로스마켓 시그널**: SOX→반도체, USD/KRW→외국인, US10Y→성장주, CSI300→중국
3. **이벤트-드리븐**: DART 공시, FOMC/BOK, 뉴스 센티멘트 + 과거 통계
4. **포트폴리오 최적화**: 상관 매트릭스, CVaR, 신규 종목 영향 예측
5. **경험 DB**: 매 거래 로깅 (레짐, 섹터, 시그널, 근거, 결과)
6. **개인화**: CEO 리스크 성향, 보유기간, 섹터 전문성, 자본 한도

### 6-4. 대표 피드백 반영
- 인프라(디스크/데이터품질) 우선
- Agentic 전환은 단계적 (Layer 0 분류기 → 점진적 확대)
- 모든 시그널/전략에 수익 검증 단계 필수
- **환각 5중 방어**: 시스템 프롬프트, _source 메타, 필터, 무결성 체크, 주간 감사
- **과적합 방지 5단계**: In-sample, Out-of-sample, 레짐별, 충격, 파라미터 민감도
- **실매매 삼중 방어**: circuit-breaker, watchdog, 증권사 사전설정
- **레이턴시 3층**: Gemini Flash(50–200ms) → 템플릿(200–800ms) → Opus Agent(2–5s)

### 6-5. 백테스트-실매매 괴리 보정 엔진
- go100_experience_log 확장 (source: backtest/paper/live, slippage_expected/actual 등)
- go100_gap_analysis (동일 전략·종목·시점 괴리 자동 매칭)
- gap_calibrator.py: 괴리 측정 → 백테스트 파라미터 자동 조정 → 신뢰도 A/B/C/D
- 실매매 유니버스 필터: 시총 3천억+, 일 거래대금 30억+, 스프레드 0.3% 이내
- 포지션 사이징: A 100%, B 70%, C 40%, D 0%
- 프리마켓 시그널 재검증 (08:30, 해외시장 대조)

### 6-6. 데이터 수집 계획 (확정)
- **과거 일괄**: 상장폐지 OHLCV, 분봉 1년(100종목), 틱 3개월(50종목), 투자자별 매매동향 3년(200종목), PIT 재무 5년, 오버나이트 갭(MV)
- **실시간**: 호가 10단계 5분 스냅샷, 체결 틱, 투자자 매매동향 16:20, 당일 1분봉 16:30, 호가/틱 통계 집계, 갭 MV 17:00
- **신규 테이블**: go100_delisted_ohlcv, go100_minute_bars, go100_tick_data(파티션), go100_investor_flow, go100_fundamentals_pit, go100_overnight_gap(MV), go100_orderbook_snapshots(파티션), go100_realtime_ticks(파티션), go100_orderbook_daily_stats, go100_tick_daily_stats, go100_cross_market_signals, go100_signal_performance, go100_experience_log, go100_gap_analysis, go100_calibration_params, go100_trading_cost_params, go100_user_profile

---

## 7. 문서·레포 참조

- **본 인수인계서**: `project-docs/go100/HANDOVER-V3-UPGRADE-20260226.md`
- **상세 기획서**: `project-docs/go100/RPT-GO100-BAEKOGI-V3-MASTER-PLAN-20260226.md`
- **레포**: kis-autotrade-v4 (phase-2c-command-center), project-docs (master)

---

*인수인계서 끝.*
