# GO100(백억이) v3.0 천재 트레이더 버전업 — 인수인계·기획서

**문서 ID**: GO100-HANDOVER-V3-PLANNING-20260226  
**최종수정**: 2026-02-26 KST  
**목적**: 신규 개발자·AI 에이전트가 GO100 프로젝트 현황·로드맵·설계를 즉시 파악하고 v2→v4 실행에 참여할 수 있도록 하는 종합 인계·기획 문서

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|-----------|
| 1.0 | 2026-02-26 | 초판 — Phase 1~10 완료 현황, v2/v3/v4 상세 설계, 데이터 수집·안전장치·일정·KPI·리스크 포함 |

---

## 1. Executive Summary

GO100(백억이)은 **AI 주식 트레이딩 어시스턴트**로, 한국투자증권(KIS) 및 키움증권 API와 연동하여 데이터 조회·분석·시그널·페이퍼/실매매를 제공한다. **Phase 1~10**까지 기본 인프라, LLM 라우팅, 17개 인텐트, Goal Engine, C-3 레짐 엔진, C-4 리포터, E-1 페이퍼 트레이딩, E2E 검증, 실매매 연동, 성과 대시보드, 베타 모니터링이 완료된 상태이다.

**핵심 전환**: 키워드 기반 인텐트 → **Agentic Architecture**(LLM이 21개 도구 자동 선택·호출), 단일 LLM → **3-Layer Dispatcher + 멀티모델**(Gemini 2.0 Flash / Claude Opus 4.6 / Claude Sonnet 4), 백테스트와 실매매 간 **7가지 괴리**를 측정·보정하는 **괴리 보정 엔진** 도입, **전략 자동 진화·이벤트 드리븐·크로스마켓 시그널**로 v3.0 트레이더, **자기 복기·포트폴리오 최적화·개인화**로 v4.0 천재 단계로 확장한다.

**성공 지표**: 환각률 0%, Intent 정확도 ≥98%, 백테스트-실매매 괴리 Month 3 ≤1.5%, A/B등급 전략 비율 ≥60% 시 실매매 본격 가동. **긴급 조치**: 디스크 89% → 250GB 확장 즉시, 미등록 크론 5건 등록 완료, 인계서 2건 project-docs 등록 필요.

---

## 2. 현재 시스템 진단

### 2.1 완료 현황 (Phase 1~10)

| Phase | 내용 | 상태 |
|-------|------|------|
| 1–3 | 기본 인프라, LLM 라우팅, 인텐트 15→17개, 데이터 쿼리, 응답 필터링 | 완료 |
| 4 | 응답 포매팅 표준화 | 완료 |
| 5 | Goal Engine, Portfolio Manager, Strategy Portfolio | 완료 |
| 6 | C-3 Adaptive Regime Engine (5레짐×3리스크=15 배분), C-4 Proactive Reporter (모닝/종가/주간/이벤트) | 완료 |
| 7 | E-1 Paper Trading (슬리피지 0.1%, 수수료 0.015%, 세금 0.18%) | 완료 |
| 8 | E2E 통합검증 (모듈 9/9, 테이블 15/15, 인텐트 17/17 PASS) | 완료 |
| 9 | 실매매 연동 (7단계 안전장치, KIS OrderService 재사용, circuit breaker 일 3%) | 완료 |
| 10-A | 성과 대시보드 (API 7개, 프런트 컴포넌트 7개, recharts) | 완료 |
| 10-B | 베타 모니터링 (usage_logs, monitor API 4개, health_monitor 크론) | 완료 |

### 2.2 프로젝트·인프라 요약

- **프로젝트명**: GO100 (백억이) — AI 주식 트레이딩 어시스턴트  
- **서버**: Ubuntu 24.04, Xeon Gold 5220 4-core, 15GB RAM, 99GB SSD(84GB 사용 89%) → 250GB 확장 예정  
- **레포**: kis-autotrade-v4 (branch: phase-2c-command-center), project-docs (master)  
- **DB**: PostgreSQL 16 (kisautotrade), Redis  
- **연동 증권사**: KIS 한국투자증권 (REST + WebSocket), 키움증권 (REST API + OpenAPI+)  
- **LLM**: 현재 Gemini 2.5 Flash (fallback Claude Haiku), 비용 ~$15/월/100유저  
- **도메인**: go100.newtalk.kr  

### 2.3 DB 테이블 현황

- **go100_*** 테이블 15개 + 보조 테이블  
- **ohlcv_daily**: 다년치 일봉, 분봉 파티션(0.75~1.15GB each)  
- **stock_fundamentals**: 2,439건 (최신 스냅샷만, PIT 아님)  
- **strategy_cards**: 62건 (V4), **go100_strategy_cards**: 3건  
- **go100_backtest_runs**, **go100_portfolios**, **go100_positions**, **go100_orders**, **go100_trades**: 모두 0건  
- **v4_users**: 4명, **accounts**: 7건  

### 2.4 핵심 문제점

#### 2.4.1 키워드 매칭 한계

- 인텐트 처리가 **키워드 → C2SC(LLM) → 핸들러** 방식  
- 누락 키워드로 "백억이가 천재되냐" 같은 오류 발생  
- **해결**: Agentic Architecture 전환 (LLM이 도구 자동 선택·호출)  

#### 2.4.2 백테스트 ↔ 실매매 괴리 7가지

1. **체결 가격 차이**: 종가 가정 vs 호가 스프레드  
2. **거래량 제약**: 소형주 시장충격 미반영  
3. **타이밍 지연**: 시그널 16:10 → 주문 익일 09:05 (17시간 갭)  
4. **비용 구조 차이**: 슬리피지 0.1%는 대형주 기준, 소형주 0.3~0.5%  
5. **심리적 개입**: CEO 확인 단계 지연  
6. **레짐 전환 속도**: 일봉 단위 판단은 급락에 1~2일 지연  
7. **생존 편향**: 상장폐지 종목 누락 → 연 2~3%p 과대 추정  

#### 2.4.3 데이터 갭 7가지 (부재/불완전)

1. **호가 잔량(Order Book)** — 과거 없음, 실시간 수집 필수  
2. **체결 틱 데이터** — 과거 키움 수개월만, 실시간 수집 필수  
3. **상장폐지 종목 OHLCV** — FinanceDataReader KRX-DELISTING으로 해결  
4. **Point-in-Time 재무제표** — DART OpenAPI로 해결  
5. **투자자별 매매동향 히스토리** — KIS/키움 API로 해결  
6. **시장충격 모델** — 호가잔량 축적 후 구현  
7. **오버나이트 갭 체계화** — 기존 ohlcv_daily에서 materialized view 생성  

---

## 3. 버전 로드맵 (v1→v4)

| 버전 | 코드명 | 핵심 | 시기 |
|------|--------|------|------|
| v1.0 | 정보원 | 데이터 조회 | 완료 |
| v2.0 | 분석가 | LLM 자동 판단·시그널·경험 축적 | 1–4주 |
| v3.0 | 트레이더 | 전략 자동 진화·크로스마켓·실매매 검증 | 4–10주 |
| v4.0 | 천재 | 자기 복기·포트폴리오 최적화·개인화 | 10–16주 |

---

## 4. v2.0 상세 설계 (분석가)

### 4.1 LLM 3-Layer Dispatcher

- **Layer 0**: Gemini 2.0 Flash (50–200ms) — 질문 분류 (simple / data / analysis / action)  
- **simple / data**: 템플릿 또는 직접 DB 조회 (200–800ms, LLM 미사용)  
- **analysis / action**: Claude Opus 4.6 Agent (2–5s)  
- **단계적 전환**: Week 1 Layer 0만, Week 2–3 data, Week 4 analysis/action  

### 4.2 멀티-모델 LLM

- **대화/Agent Core**: Claude Opus 4.6  
- **배치 보고서/시그널 요약**: Claude Sonnet 4  
- **전략 아이디어 생성**: Claude Opus 4.6 (temperature=0.9)  
- **비용 관점**: "수익 나면 비용은 문제 아님" — 정확도에 자원 집중, 비용 최적화 우선순위 제외  

### 4.3 Agentic Architecture (21개 도구)

- **agent_tools.py**: 시장(3) + 종목(4) + 업종(3) + 포트폴리오(3) + 전략(3) + 레짐(2) + 페이퍼/실매매(2) + 보고서(1)  
- **agent_core.py**: 최대 5라운드, 라운드당 3개 도구, 병렬 비동기 실행  
- **GO100_AGENT_MODE** env 토글로 기존 로직과 전환 가능  

### 4.4 크로스마켓 선행 시그널

- **테이블**: go100_cross_market_signals  
- **신호**: SOX→반도체, USD/KRW→외국인, US10Y→성장주, China CSI300  
- 매일 07:00 수집, 모닝 브리핑 포함  
- **성과 추적**: go100_signal_performance (정확도 ≥55% 미만 시 제외)  

### 4.5 경험 DB

- **테이블**: go100_experience_log (JSONB: market_snapshot, action, outcome, regime, vkospi, sector, strategy)  
- **확장 컬럼**: source(backtest/paper/live), slippage_expected/actual, fill_rate, time_to_fill, overnight_gap_pct, volume_participation_pct, market_impact_pct  
- **괴리 분석**: go00_gap_analysis (backtest_return vs live_return, gap_source 분류)  

---

## 5. v3.0 상세 설계 (트레이더)

### 5.1 전략 자동 진화 엔진

- 매주 04:00 **strategy_evolution.py** 실행  
- 성과 평가 → 파라미터 변이 → LLM 생성 전략 → 자동 백테스트  
- **5단계 검증**: In-sample(3yr, Sharpe≥1) → Out-of-sample(1yr, 차이≤50%) → 레짐별 MDD → 외부 충격 시뮬 → 파라미터 민감도  
- 통과 시 **CANDIDATE**, 미통과 **REJECTED**  

### 5.2 이벤트-드리븐 엔진

- DART 공시 수집 → 과거 서프라이즈 통계 → 실시간 알림  
- 매크로 캘린더 (FOMC, BOK) 연동  

### 5.3 실매매 시뮬레이터 수준 백테스트

- **호가 기반 체결 시뮬레이션**: ask1/bid1, 잔량 초과 시 2호가~  
- **거래량 제한**: 대형 10%, 중형 5%, 소형 3%  
- **비용 완전 일치**: KIS와 동일 (수수료 0.015%, 세금 0.18%, 슬리피지 실측)  
- **Point-in-Time 유니버스**: 상장폐지 포함, IPO +5영업일 후 편입  
- **오버나이트 갭 반영**: 익일 시가 기준 매매  
- **go100_trading_cost_params** 테이블에서 비용 파라미터 동적 로드  

### 5.4 백테스트-실매매 괴리 보정 엔진

- **gap_calibrator.py**: 측정(60일 괴리 집계) → 보정(슬리피지/거래량/갭 파라미터 자동 조정) → 신뢰도 등급(A/B/C/D)  
- **D등급** 전략은 실매매 자동 차단  
- **포지션 사이징**: A=100%, B=70%, C=40%, D=0%  
- **프리마켓 시그널 재검증**: 08:30에 야간 해외시장 대조 후 무효 시그널 취소  

---

## 6. v4.0 상세 설계 (천재)

### 6.1 자기 복기

- 경험 DB 기반 사후 분석, 실패/성공 패턴 추출, 전략·레짐·시그널 파라미터 자동 보정  

### 6.2 포트폴리오 최적화

- 상관 매트릭스, CVaR, 스트레스 시뮬레이션  
- 신규 종목 편입 시 포트폴리오 영향 사전 예측  

### 6.3 사용자 개인화

- **go100_user_profile**: 리스크 성향, 보유 기간, 섹터 선호, 자본 한도  
- 시스템 프롬프트와 전략 파라미터에 자동 반영  

---

## 7. 데이터 수집 계획

### 7.1 KIS vs 키움 API 최적 소스 매핑

| 데이터 | 소스 | 비고 |
|--------|------|------|
| 일봉 OHLCV | 키움 | 1회 900건, 기간 무제한 |
| 분봉 OHLCV | 키움 1년치, KIS 당일 | KIS 당일 → 매일 수집으로 누적 |
| 틱 데이터 | 키움 수개월, KIS WebSocket | 실시간 |
| 투자자별 매매동향 | KIS REST | 일별, 기간 무제한 |
| 호가 잔량 | KIS WebSocket | 실시간만 → 5분 스냅샷 수집 |
| 상장폐지 OHLCV | FinanceDataReader | KRX-DELISTING |
| PIT 재무제표 | DART OpenAPI | 2020~현재 분기별 |
| 오버나이트 갭 | ohlcv_daily | materialized view |

### 7.2 신규 테이블 목록

- go100_delisted_ohlcv, go100_minute_bars, go100_tick_data(파티션)  
- go100_investor_flow, go100_fundamentals_pit, go100_overnight_gap(MV)  
- go100_orderbook_snapshots(파티션), go100_realtime_ticks(파티션)  
- go100_orderbook_daily_stats, go100_tick_daily_stats  
- go100_cross_market_signals, go100_signal_performance  
- go100_experience_log, go00_gap_analysis, go100_calibration_params  
- go100_trading_cost_params, go100_user_profile  

### 7.3 크론 스케줄 (기존 + 신규)

| 시각 | 작업 |
|------|------|
| 07:00 | 교차시장 시그널 수집 |
| 08:30 | 글로벌 데이터 수집 (기존) |
| 08:50 | 모닝 브리핑 |
| 15:40 | 장마감 리포트 |
| 16:10 | 페이퍼 트레이딩 |
| 16:20 | 투자자별 매매동향 수집 |
| 16:30 | 당일 분봉 수집 (KIS) |
| 16:40 | 호가 통계 집계 |
| 16:50 | 틱 통계 집계 |
| 17:00 | 오버나이트 갭 뷰 리프레시 |
| 19:30 | 재무제표 수집 (기존) |
| 토 09:00 | 주간 리포트 |
| 일 04:00 | 전략 진화 엔진 |
| */5 | 이벤트 알림, 헬스 모니터 |

---

## 8. 백테스트-실매매 괴리 보정 엔진 (상세)

- **측정**: 60일 단위로 backtest_return vs live_return(또는 paper_return) 괴리 집계, gap_source(체결가/거래량/타이밍/비용/심리/레짐/생존편향) 분류  
- **보정**: 슬리피지·거래량 한도·갭 반영 계수 자동 조정, go100_calibration_params 반영  
- **신뢰도 등급**: A/B/C/D, D등급 전략 실매매 차단, 포지션 사이징 A=100%, B=70%, C=40%, D=0%  
- **프리마켓 재검증**: 08:30 야간 해외 시장 데이터로 전일 16:10 시그널 재검증, 무효 시 취소  

---

## 9. 안전장치

### 9.1 환각 방지 5중 방어

1. **시스템 프롬프트 절대 규칙**  
2. **도구 결과에 _source 메타데이터**  
3. **response_filter.py 강화** (숫자 교차검증, 확정 예측 표현 교체)  
4. **data_integrity_check.py** 일일 실행  
5. **사용 로그 + 주간 감사** (환각률 목표 <0.1% → 0%)  

### 9.2 실매매 삼중 방어

1. **서비스 내부**: circuit-breaker (일 손실 3%) + 자동 stop-loss 주문  
2. **독립 watchdog**: systemd unit, 30s 체크 → 재시작 → API 청산 → 알림  
3. **증권사 측**: stop-loss, 주문 한도, 100% 증거금 사전 설정  

### 9.3 과적합 방지 (전략 진화 5단계)

- In-sample(3yr, Sharpe≥1) → Out-of-sample(1yr, 차이≤50%) → 레짐별 MDD → 외부 충격 시뮬 → 파라미터 민감도 검증  

---

## 10. 인프라·비용·일정

### 10.1 인프라

- **서버**: Ubuntu 24.04, Xeon Gold 5220 4-core, 15GB RAM, 99GB SSD → 250GB 확장 예정  
- **디스크**: 현재 89% 사용 → 확장 즉시 신청  

### 10.2 비용

- **서버**: ₩15k → ₩25k/월 (디스크 확장 후)  
- **LLM**: $15 → $35/월 (멀티모델 후)  
- **총 월 비용**: ₩75k~₩83k  
- **CEO 방침**: "수익이 나면 비용은 질문 없다" — 정확도 우선  

### 10.3 일정 (버전별)

- v2.0: 1–4주  
- v3.0: 4–10주  
- v4.0: 10–16주  

---

## 11. 성공 지표 (KPI)

| 지표 | 목표 |
|------|------|
| 환각률 | <0.1% → 최종 0% |
| Intent 정확도 | ≥98% |
| 응답 레이턴시 | simple <1s, data <2s, analysis <5s |
| 크로스마켓 시그널 정확도 | ≥60% |
| 백테스트-실매매 괴리 | Month 1 ≤5%, Month 2 ≤3%, Month 3 ≤1.5% |
| A/B등급 전략 비율 | ≥60% 시 실매매 본격 가동 |

---

## 12. 주차별 실행 계획 (Week 0~16)

| 주차 | 구간 | 핵심 |
|------|------|------|
| Week 0 | 준비 | 디스크 확장, 미등록 크론 5건 등록, 인계서 project-docs 등록 |
| Week 1 | v2 | Layer 0(Gemini 2.0 Flash) 질문 분류만 도입 |
| Week 2–3 | v2 | data 경로 템플릿/DB 조회 연동 |
| Week 4 | v2 | analysis/action → Claude Opus 4.6 Agent, Agentic 21개 도구, GO100_AGENT_MODE 토글 |
| Week 5–6 | v2/v3 | 크로스마켓 시그널 수집·모닝 브리핑, 경험 DB 스키마·수집 |
| Week 7–8 | v3 | 전략 진화 엔진 5단계 검증, 이벤트 드리븐 수집·알림 |
| Week 9–10 | v3 | 실매매 시뮬레이터급 백테스트(호가/거래량/비용/PIT/갭), gap_calibrator 측정·보정 |
| Week 11–12 | v3/v4 | 괴리 Month 2 ≤3% 목표, 신뢰도 등급 A/B/C/D 적용 |
| Week 13–14 | v4 | 자기 복기(경험 DB 분석), 포트폴리오 최적화(상관/CVaR/스트레스) |
| Week 15–16 | v4 | go100_user_profile 개인화, 괴리 Month 3 ≤1.5%, A/B등급 ≥60% 검증 후 실매매 본격화 |

---

## 13. 리스크 및 대응 방안

| 리스크 | 대응 |
|--------|------|
| 디스크 부족으로 수집·백테스트 중단 | 250GB 확장 즉시 신청·적용, 파티션/로그 로테이션 강화 |
| 키워드→Agent 전환 시 기존 플로우 오류 | GO100_AGENT_MODE env로 단계 전환, 롤백 가능 |
| 괴리 보정 미달로 실매매 손실 | D등급 차단, 포지션 사이징 B/C 축소, 60일 재측정 |
| LLM 비용 급증 | 멀티모델에서 simple/data 경로 비중 확대, 캐시 강화 (CEO 방침상 정확도 우선) |
| 크로스마켓/이벤트 데이터 지연·누락 | 07:00/매크로 크론 모니터링, 알림 시 정확도 55% 미만 시그널 제외 |
| 전략 진화 과적합 | 5단계 검증 유지, OOS 차이≤50%, 파라미터 민감도 검사 |
| 실매매 삼중 방어 우회 | watchdog 30s 체크·재시작·API 청산·알림 유지, 증권사 한도 재점검 |

---

## 14. 긴급 이슈 및 참조

### 14.1 긴급 이슈

- **디스크 89%** → 250GB 확장 즉시 신청  
- **미등록 크론 5건** → 등록 완료 (베타 테스트 병렬)  
- **인계서 2건 project-docs 미등록** → 등록 필요  

### 14.2 문서 위치

- **본 인수인계·기획서**: `project-docs/go100/GO100-HANDOVER-V3-PLANNING-20260226.md`  
- **레포**: kis-autotrade-v4 (phase-2c-command-center), project-docs (master)  
- **도메인**: go100.newtalk.kr  

---

*문서 끝.*
