# DESK 2 데이터 총괄 인벤토리

**문서번호**: DESK2-DATA-MASTER-TABLE-001
**작성일**: 2026-02-24 | **대상**: CEO 직보

---

## 1. 백테스트용 히스토리컬 데이터

| # | 데이터명 | 테이블(예상) | 항목 | 용도 (Condition/Strategy) | 최소 범위 | 이상적 범위 | 우선순위 | 현재 상태 | 대체 가능 여부 | 비고 |
|---|---------|------------|------|--------------------------|----------|------------|---------|----------|--------------|------|
| H-01 | 1분봉 OHLCV | v4_minute_bar | ticker, datetime, O/H/L/C, volume, value | **전체** — 7개 Condition · 7개 Strategy 모두 의존 | KOSPI+KOSDAQ 상위 1,000종목 × 1년(250일) | 상위 1,000종목 × 3년 | **P0** | 433만 행 존재, 범위 미확인 | 대체 불가 | 3분봉·5분봉은 1분봉에서 집계 생성 가능 |
| H-02 | 일봉 OHLCV | v4_daily_price (추정) | ticker, date, O/H/L/C, volume, value, market_cap, shares | C1(갭 전일종가), C2(RVOL 20일평균), C4(RVOL), C5(피보나치 기준), C6(상관계수), TIER(시총필터) | 전 종목 × 2년 | 전 종목 × 5년 | **P0** | 미확인 | 대체 불가 | 시가총액 필드 필수 — TIER 엔진 의존 |
| H-03 | VI 발동·해제 이력 | 미정 | ticker, trigger_time, release_time, vi_type, trigger_price, pre_vi_price, post_vi_first_price, pre_vi_volume_5min | **C3**(VI 폭발) · **CHARLIE-VI** | 1년 | 2년 | **P1** | 미확보 추정 | 분봉에서 역추정 가능 (정확도 80~90%) | KRX 정보데이터시스템 또는 KIS API 확인 |
| H-04 | 수급(투자자별 매매) — 일별 | v4_investor_trading (추정) | ticker, date, foreign_buy/sell/net, institution_buy/sell/net, individual_net, foreign_holding_ratio | C4(수급전환), C7(순매수전환), DELTA-VWAP(CS 수급항목), GOLF-REVERSAL(CS 수급항목) | 전 종목 × 1년 | 전 종목 × 3년 | **P1** | 미확인 | 일별 데이터로 분별 대체 시 정밀도 하락 | 분별 수급은 H-05로 별도 분류 |
| H-05 | 수급(투자자별 매매) — 분별/시간별 | 미정 | ticker, datetime, foreign_net, institution_net, individual_net | C4(장중 순매수전환 실시간), C7(30분 내 전환 감지) | 상위 500종목 × 1년 | 상위 1,000종목 × 2년 | **P1** | 미확보 추정 | H-04(일별)로 대체 가능, 장중 전환 정밀도 하락 | KIS API 분별 조회 이력 축적 가능 |
| H-06 | 업종 지수 일봉 | v4_sector_price (추정) | sector_code, sector_name, date, O/H/L/C, volume, value | **C6**(업종 후발 대장주 감지) · **FOXTROT-SECTOR** · 레짐 판단 보조 | KRX 전 업종 × 2년 | KRX 전 업종 × 5년 | **P1** | 계획됨, 활성화 미확인 | 소속 종목 시총가중 평균으로 자체 구성 가능 | KRX 업종 분류 체계 확인 필요 |
| H-07 | 종목-업종 매핑 | 미정 | ticker, sector_code, sector_name, market_cap_rank_in_sector | C6(대장주·후발주 구분), 상관계수 산출 범위 한정, 동일업종 진입금지 규칙 | 전 종목 최신 | 매 분기 갱신 이력 | **P1** | 미확인 | KRX에서 수동 구축 가능 | 업종 재분류 이력이 있으면 이상적 |
| H-08 | 호가(Orderbook) 이력 | 미정 | ticker, datetime, bid/ask_price_1~10, bid/ask_vol_1~10, spread, buy_ratio | C1(스프레드 점수 15점), C3(호가 매수편향 15점), CHARLIE-VI(CS 호가편향 15점) | 상위 500종목 × 6개월 | 상위 1,000종목 × 1년 | **P3** | 미확보 추정 | Corwin-Schultz 스프레드 추정(일봉 H/L), 체결강도로 매수편향 대체 | 용량 방대, 백테스트에서는 대체 추천 |
| H-09 | 뉴스·공시 이력 | 미정 | ticker, datetime, headline, source, category(실적/수주/M&A/규제/테마/기타), sentiment | C1(뉴스존재 점수 20점), C7(악재필터 점수 20점), ALPHA-GAP(CS 참조), GOLF-REVERSAL(CS 뉴스필터 20점) | 상위 500종목 × 1년 | 전 종목 × 3년 | **P2** | 미확보 추정 | 백테스트 시 해당 점수 항목 비활성화(0점 처리) | DART API + 뉴스 API 수집 필요 |
| H-10 | 체결 강도 이력 | 미정 | ticker, datetime(분별), buy_volume, sell_volume, intensity(=buy/sell×100) | C1(체결강도 점수 20점), C3(체결강도 ≥150% 진입조건), ALPHA-GAP(CS 20점), CHARLIE-VI(CS 25점) | 상위 500종목 × 1년 | 상위 1,000종목 × 2년 | **P1** | 미확인 | 분봉 O/C 비교로 추정 가능 (정확도 70~80%) | 틱 데이터가 있으면 정확 산출 가능 |
| H-11 | 시장 지수 일봉 (KOSPI/KOSDAQ/VKOSPI) | 미정 | index_code, date, O/H/L/C, volume | 레짐 판단(MA5/MA20/ADX), C2(시장방향 점수 20점), C7(시장동반하락 점수 20점), Soft Kill(VKOSPI>25) | 2년 | 5년 | **P0** | 미확인 | 대체 불가 — 레짐 엔진 핵심 입력 | KRX 또는 KIS API에서 확보 용이 |
| H-12 | 상관계수 매트릭스 | 파생 (자동생성) | ticker_a, ticker_b, period(60일), correlation, sector_code | C6(대장주-후발주 상관 ≥0.7 필터), FOXTROT-SECTOR(CS 상관 항목 20점) | 동일업종 내 상위 10종목 쌍 | 전 업종 | **파생** | H-02 + H-07 확보 후 자동 산출 | — | 업종당 45쌍 × 30업종 = 1,350쌍 |
| H-13 | 기술 지표 사전계산 캐시 | 파생 (자동생성) | ticker, datetime, VWAP, RVOL, RSI(14), BB_upper/mid/lower, ATR(14), MA5/10/20, BBW | 전체 Condition · Strategy의 지표 참조 | H-01 수록 범위와 동일 | H-01과 동일 | **파생** | H-01 확보 후 자동 산출 | — | IndicatorEngine이 일괄 사전계산 |

---

## 2. 실시간 운영용 데이터

| # | 데이터명 | 데이터 소스 | 수신 항목 | 용도 (Condition/Strategy/System) | 갱신 주기 | 동시 구독 규모 | 우선순위 | 현재 상태 | 대체 가능 여부 | 비고 |
|---|---------|-----------|----------|--------------------------------|----------|--------------|---------|----------|--------------|------|
| R-01 | 실시간 체결(Tick) 스트림 | KIS OpenAPI WebSocket | ticker, price, volume, timestamp, side(매수/매도) | **전체** — Layer 0 TickCollector → BarBuilder → IndicatorEngine, 모든 Condition·Strategy 기반 | 체결 즉시 (이벤트 기반) | 500~1,000종목 | **P0** | 기존 모듈 존재 추정, 연동 확인 필요 | 대체 불가 | 종목당 초당 최대 100건, 지연 < 50ms |
| R-02 | 실시간 호가(Orderbook) 스트림 | KIS OpenAPI WebSocket | ticker, bid/ask_price_1~10, bid/ask_vol_1~10, timestamp | C1(스프레드), C3(호가 매수편향), CHARLIE-VI(CS 15점), TIER 4~5 슬리피지 | 500ms 간격 | 500~1,000종목 | **P1** | v4_orderbook_realtime 계획됨, 활성화 미확인 | 체결 스트림에서 스프레드 추정 가능 (정밀도 하락) | API 구독 종목 수 제한 확인 필요 |
| R-03 | 실시간 VI 발동·해제 알림 | KIS OpenAPI 또는 자체 감지 | ticker, vi_trigger_time, vi_release_time, vi_type, trigger_price | **C3**(VI 폭발) 트리거 · **CHARLIE-VI** 진입 시점 | 이벤트 기반 (발동/해제 즉시) | 전 종목 | **P1** | 미확인 | 체결 스트림에서 자체 감지 가능 (체결 중단 2분+ & 직전 ±3%) | KIS API에 VI 전용 통보 채널 유무 확인 |
| R-04 | 실시간 수급 (투자자별 매매) | KIS OpenAPI REST | ticker, datetime, foreign_net, institution_net, individual_net | C4(장중 순매수전환), C7(외·기관 전환), DELTA-VWAP(CS 20점), GOLF-REVERSAL(CS 20점) | 1분 또는 5분 폴링 | 상위 100~200종목 (DISCOVERED 이상 상태) | **P1** | 미확인 | 일별 수급 데이터로 대체 시 장중 전환 감지 불가 | API 호출 빈도 제한 확인 필요 (초당/분당) |
| R-05 | 실시간 업종 지수 | KIS OpenAPI REST 또는 WebSocket | sector_code, datetime, price, change_pct, volume | **C6**(업종 후발 대장주 감지), 레짐 판단 보조, FOXTROT-SECTOR 실시간 참조 | 1초~5초 | KRX 전 업종 (약 30개) | **P1** | 미확인 | 소속 종목 실시간 시세에서 자체 지수 계산 가능 (연산 부하 증가) | 업종 분류 코드 표준화 필요 |
| R-06 | 실시간 시장 지수 (KOSPI/KOSDAQ/VKOSPI) | KIS OpenAPI WebSocket | index_code, datetime, price, change_pct, volume | 레짐 판단(상승/하락/횡보/고변동), C2(시장방향 20점), C7(시장동반하락 20점), Soft Kill(VKOSPI>25), Hard Kill 참조 | 1초 | 3개 지수 | **P0** | 미확인 | 대체 불가 — Orchestrator 레짐엔진 핵심 | 구독 부하 극소, 확보 용이 예상 |
| R-07 | 실시간 뉴스·공시 피드 | DART Open API + 뉴스 API | ticker, datetime, headline, source, category | C1(뉴스존재 20점), C7(악재필터 20점), ALPHA-GAP(CS 참조), GOLF-REVERSAL(CS 뉴스필터 20점) | 이벤트 기반 (발표 후 30초 이내) | 전 종목 | **P2** | 미구현 추정 | 해당 점수 항목 비활성화 (0점 처리), 운영은 가능하나 정밀도 20% 하락 | DART API 키 필요, 뉴스 NLP 태깅 필요 |
| R-08 | 실시간 체결 강도 | R-01에서 파생 계산 | ticker, datetime, buy_volume, sell_volume, intensity | C1(체결강도 20점), C3(≥150% 진입조건), ALPHA-GAP(CS 20점), CHARLIE-VI(CS 25점) | R-01 수신 시 실시간 집계 | R-01 구독 종목과 동일 | **P0 (파생)** | R-01 확보 시 자동 생성 | — | 매수/매도 구분은 체결가-호가 비교로 판정 |
| R-09 | 실시간 기술 지표 캐시 | R-01에서 파생 계산 | ticker, VWAP, RVOL, RSI, BB, ATR, MA5/10/20, BBW | **전체** Condition · Strategy 실시간 판단 기반 | 봉 완성 시마다 (1분/3분/5분) + 500ms partial | R-01 구독 종목과 동일 | **P0 (파생)** | R-01 확보 시 자동 생성 | — | IndicatorEngine이 실시간 계산 |

---

## 3. 설정·참조 데이터 (정적/반정적)

| # | 데이터명 | 저장 위치 | 항목 | 용도 | 갱신 주기 | 우선순위 | 현재 상태 | 비고 |
|---|---------|----------|------|------|----------|---------|----------|------|
| S-01 | 종목 마스터 | DB 테이블 | ticker, name, market(KOSPI/KOSDAQ), sector_code, market_cap, shares_outstanding, listing_date, is_managed(관리종목), is_risk(투자위험) | TIER 시가총액 필터, Hard Kill(관리·위험종목 금지), 유니버스 구성 | 매일 장 전 갱신 | **P0** | 기존 존재 추정 | 관리·위험종목 플래그 필수 |
| S-02 | 업종 분류 체계 | DB 테이블 | sector_code, sector_name, parent_sector, sector_type(KRX/GICS) | C6 업종 매칭, 동일업종 진입금지 규칙, 상관계수 범위 | 분기별 갱신 | **P1** | 미확인 | KRX 업종 분류 기준으로 구축 |
| S-03 | 적합도 매트릭스 | YAML (fitness_matrix.yaml) | condition_id × strategy_id → fit_score (0~100) | Orchestrator 전략 라우팅, 크로스 매칭 판단 | 분기별 갱신 (백테스트 결과 반영) | **P0** | 설계 완료, 파일 미생성 | 초기값은 기술서 Part 5.1 기준 |
| S-04 | 레짐 보정값 | YAML (regime_adjustments.yaml) | regime_type × strategy_id → adjustment (±점수) | 적합도 동적 조정 | 분기별 갱신 | **P1** | 설계 완료, 파일 미생성 | 상승/하락/횡보/고변동 4종 레짐 |
| S-05 | TIER 파라미터 | YAML (tier_config.yaml) | tier_level(1~5) × 파라미터(건당배분, 최대포지션, 일일한도, 시총하한, CS하한 등) | CapitalAllocator, RiskManager | 변경 시 수동 갱신 | **P0** | 설계 완료, 파일 미생성 | 기술서 Part 6.2 기준 |
| S-06 | Condition 파라미터 | YAML (condition_config.yaml) | condition_id × 파라미터(임계값, 가중치, 점수표) | 7개 Condition의 발굴 기준 및 점수 산정 | 백테스트 결과에 따라 갱신 | **P0** | 설계 완료, 파일 미생성 | 기술서 Part 2.3.2 기준 |
| S-07 | Strategy 파라미터 | YAML (strategy_config.yaml) | strategy_id × 파라미터(진입조건, CS 가중치, 청산규칙, 트레일링 설정) | 7개 Strategy의 진입·청산·CS 계산 | 백테스트 결과에 따라 갱신 | **P0** | 설계 완료, 파일 미생성 | 기술서 Part 2.3.3 기준 |
| S-08 | 리스크 한도 | YAML (risk_limits.yaml) | tier_level × 한도(건당손실, 전략일일손실, DESK일일손실, 주간손실, CB Level 1~3 임계값) | RiskManager, CircuitBreaker | 변경 시 수동 갱신 | **P0** | 설계 완료, 파일 미생성 | 기술서 Part 7 기준 |
| S-09 | 실적 발표 일정 | DB 테이블 또는 외부 API | ticker, earnings_date, earnings_type(분기/반기/연간) | Hard Kill(실적 발표 전후 2일 진입 금지) | 분기별 사전 등록 | **P2** | 미확보 추정 | DART 또는 FnGuide에서 수집 |
| S-10 | 공휴일·반일거래일 캘린더 | 설정 파일 | date, market_status(정상/반일/휴장) | 시스템 부팅/종료 시각 조정, 백테스트 거래일 필터 | 연초 1회 등록 | **P1** | 미확인 | KRX 공휴일 일정 기준 |

---

## 4. 운영·로그 데이터 (시스템 생성)

| # | 데이터명 | 저장 위치 | 항목 | 용도 | 생성 주체 | 보존 기간 | 비고 |
|---|---------|----------|------|------|----------|----------|------|
| L-01 | 거래 로그 | PostgreSQL (trade_log) | position_id, ticker, strategy_id, condition_id, tier, entry_time, exit_time, entry_price, exit_price, quantity, pnl_pct, pnl_amount, hold_seconds, desk_score, cs, composite_score, relay_count, slippage, exit_reason | 성과 분석, 전략 평가, 파라미터 최적화, 일일 보고서 | TradeLogger | 영구 | 모든 거래 기록 — 핵심 자산 |
| L-02 | 발굴 로그 | PostgreSQL (discovery_log) | signal_id, ticker, condition_id, desk_score, timestamp, market_state, primary_strategy, expiry, result(entered/queued/expired/discarded) | Condition별 발굴 정확도 분석, 발굴 대비 진입 비율 | DiscoveryManager | 6개월 | 대량 발생 (일일 수백 건) |
| L-03 | 전략 신호 로그 | PostgreSQL (signal_log) | signal_id, ticker, strategy_id, cs, composite_score, timestamp, result(executed/rejected/expired) | Strategy별 CS 정밀도 분석, 신호 대비 체결 비율 | StrategyManager | 6개월 | 대량 발생 |
| L-04 | 릴레이 로그 | PostgreSQL (relay_log) | ticker, date, relay_seq(1/2/3), from_strategy, to_strategy, from_pnl, to_pnl, cooldown_start, cooldown_end | 릴레이 성공률 분석, 릴레이 전략 조합 최적화 | RelayManager | 영구 | 릴레이당 1건 |
| L-05 | 리스크 이벤트 로그 | PostgreSQL (risk_event_log) | event_type(hard_kill/soft_kill/cb_level1/2/3), timestamp, trigger_value, affected_positions, action_taken | 리스크 규칙 발동 빈도 분석, 규칙 효과 평가 | RiskManager | 영구 | 발동 시에만 생성 |
| L-06 | TIER 전환 로그 | PostgreSQL (tier_transition_log) | date, from_tier, to_tier, capital_amount, trigger_reason(up_shift/down_shift) | 자본 성장 추적, TIER 전환 빈도 분석 | TierCalculator | 영구 | 전환 시에만 생성 |
| L-07 | 일일 정산 보고서 | PostgreSQL (daily_report) | DailyReport 전체 필드 (기술서 Part 4.2 참조) | CEO 보고, 성과 추적, 시스템 건전성 확인 | DailyReporter | 영구 | 매일 15:30 1건 생성 |
| L-08 | 시스템 상태 로그 | Redis + PostgreSQL | system_state(booting/pre_scan/active/closing/settled), active_conditions, active_strategies, active_positions, queue_size, capital_utilization | 시스템 모니터링, 장애 추적 | SystemState | Redis 당일, DB 30일 | 1초 간격 갱신 |
| L-09 | 슬리피지 로그 | PostgreSQL (slippage_log) | position_id, ticker, strategy_id, signal_price, fill_price, slippage_pct, order_split_count | 전략별 슬리피지 분석, TIER별 주문 분할 효과 평가 | SlippageMonitor | 6개월 | 체결당 1건 |

---

## 5. 데이터 의존성 맵 (Condition/Strategy별)

| Condition / Strategy | H-01 분봉 | H-02 일봉 | H-03 VI | H-04 수급일별 | H-05 수급분별 | H-06 업종 | H-07 종목업종 | H-08 호가 | H-09 뉴스 | H-10 체결강도 | H-11 시장지수 | R-01 체결 | R-02 호가 | R-03 VI | R-04 수급 | R-05 업종 | R-06 시장지수 | R-07 뉴스 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **C1 갭 / ALPHA-GAP** | ● 필수 | ● 필수 | | | | | | ○ 권장 | ○ 권장 | ● 필수 | | ● 필수 | ○ 권장 | | | | | ○ 권장 |
| **C2 ORB / BRAVO-ORB** | ● 필수 | ● 필수 | | | | | | | | | ○ 권장 | ● 필수 | | | | | ● 필수 | |
| **C3 VI / CHARLIE-VI** | ● 필수 | | ● 필수 | | | | | ○ 권장 | | ● 필수 | | ● 필수 | ○ 권장 | ● 필수 | | | | |
| **C4 VWAP / DELTA-VWAP** | ● 필수 | ● 필수 | | ○ 권장 | ● 필수 | | | | | | | ● 필수 | | | ● 필수 | | | |
| **C5 눌림목 / ECHO-ABCD** | ● 필수 | | | | | | | | | | | ● 필수 | | | | | | |
| **C6 업종후발 / FOXTROT-SECTOR** | ● 필수 | ● 필수 | | | | ● 필수 | ● 필수 | | | | | ● 필수 | | | | ● 필수 | | |
| **C7 과매도 / GOLF-REVERSAL** | ● 필수 | | | ○ 권장 | ● 필수 | | | | ● 필수 | | ● 필수 | ● 필수 | | | ● 필수 | | ● 필수 | ● 필수 |
| **Orchestrator (레짐)** | | ● 필수 | | | | | | | | | ● 필수 | | | | | | ● 필수 | |
| **TIER Engine** | | ● 필수 | | | | | | | | | | | | | | | | |
| **RiskManager** | | | | | | | | | | | ● 필수 | | | | | | ● 필수 | |

● 필수 = 이 데이터 없이는 해당 모듈이 작동 불가
○ 권장 = 없으면 해당 점수 항목을 비활성화(0점)하여 운영 가능, 정밀도 하락

---

## 6. 데이터 확보 우선순위 종합 로드맵

| 단계 | 기간 | 확보 대상 | 확보 방법 | 이 단계에서 가능해지는 것 |
|------|------|----------|----------|------------------------|
| **Day 1~2** | 즉시 | H-01 범위 확인, H-02 존재·범위 확인, H-11 존재 확인, R-01 연동 확인, R-06 연동 확인, S-01 존재 확인 | DB 쿼리 실행, KIS API 기능 목록 확인 | 전체 데이터 현황 파악 완료, 부족 범위 확정 |
| **Day 3~5** | P0 확보 | H-01 보충(부족 시 KIS API 분봉 수집), H-02 보충(KIS API 또는 KRX), H-11 확보(KRX), S-01 갱신, S-03~S-08 YAML 파일 생성 | KIS API REST 호출, KRX 다운로드, YAML 작성 | **C2/BRAVO-ORB, C5/ECHO-ABCD 백테스트 시작 가능**, C1/ALPHA-GAP · C4/DELTA-VWAP 백테스트 시작 가능 |
| **Day 5~7** | P1 확보 | H-04 수급일별(KIS API 또는 KRX), H-06 업종지수(KRX 또는 자체구성), H-07 종목-업종매핑(KRX), H-10 체결강도(분봉에서 추정 또는 별도 수집) | KIS API, KRX 다운로드, 분봉 파생 계산 | **C6/FOXTROT-SECTOR, C7/GOLF-REVERSAL 백테스트 시작 가능**, H-12 상관계수 자동 산출 가능 |
| **Day 7~10** | P1 확보 (계속) | H-03 VI이력(KRX 또는 분봉 역추정), H-05 수급분별(KIS API 축적 시작), R-02 호가 실시간 연동, R-03 VI 실시간 감지, R-04 수급 실시간 폴링, R-05 업종 실시간 | KRX, KIS API WebSocket/REST, 자체 VI 감지 로직 | **C3/CHARLIE-VI 백테스트 시작 가능**, 7개 전체 Condition·Strategy 백테스트 완료 가능, 실시간 파이프라인 기초 구축 |
| **Day 10~15** | P2 확보 + 파생 | H-09 뉴스공시이력(DART API + 뉴스 수집), H-13 기술지표 사전계산, S-09 실적발표일정, S-10 공휴일 캘린더, R-07 뉴스 실시간 | DART API, 뉴스 API, 일괄 계산 | 뉴스 기반 점수 항목 활성화, 풀 스펙 백테스트 가능, Mock Trading 준비 완료 |
| **Day 15~20** | 통합 검증 | L-01~L-09 로그 테이블 생성, 전체 파이프라인 E2E 테스트 | DB 스키마 생성, 통합 테스트 | 전체 시스템 운영 준비 완료 |

---

## 7. 데이터 볼륨 추정

| 데이터 | 일일 생성량 | 연간 누적량 | 저장소 | 비고 |
|--------|-----------|-----------|--------|------|
| H-01 분봉 (1,000종목 × 380분 × 1분봉) | 38만 행/일 | ~9,500만 행/년 | PostgreSQL | 현재 433만 행 ≈ 약 11거래일분 (1,000종목 기준) 또는 더 적은 종목·더 긴 기간 |
| H-02 일봉 (2,500종목) | 2,500행/일 | 62.5만 행/년 | PostgreSQL | 가벼움 |
| H-04 수급 일별 (2,500종목) | 2,500행/일 | 62.5만 행/년 | PostgreSQL | 가벼움 |
| H-05 수급 분별 (500종목 × 380분) | 19만 행/일 | ~4,750만 행/년 | PostgreSQL | 볼륨 큼, 파티셔닝 필요 |
| R-01 Tick (1,000종목 × 평균 5,000틱) | 500만 건/일 | 실시간만, DB 미저장 | Redis (메모리) | 분봉 생성 후 원본 폐기 |
| R-02 호가 (1,000종목 × 500ms × 380분) | 4,560만 스냅샷/일 | 실시간만, DB 미저장 | Redis (메모리) | 최신 1건만 유지 |
| L-01 거래로그 | 2~5건/일 | ~750건/년 | PostgreSQL | 극소량, 영구 보존 |
| L-02 발굴로그 | 100~500건/일 | ~7.5만 건/년 | PostgreSQL | 중간량 |

---

## 8. 기술 인프라 요구사항

| 항목 | 요구 사양 | 용도 | 비고 |
|------|----------|------|------|
| PostgreSQL | 500GB+ SSD, 16GB+ RAM | H-01~H-13 히스토리컬 저장, L-01~L-09 로그 저장 | 분봉 테이블 날짜 파티셔닝 권장 |
| Redis | 8GB+ RAM | R-01~R-09 실시간 캐시, 상태 머신, Pub/Sub, Stream | 영속성 불필요, 당일 데이터만 |
| KIS OpenAPI | WebSocket 2~4 세션, REST 초당 20회 | R-01 체결, R-02 호가, R-04 수급, R-05~R-06 지수 | WebSocket 세션당 구독 종목 수 제한 확인 필요 |
| DART Open API | API 키 1개, 일일 호출 한도 확인 | H-09 과거 공시, R-07 실시간 공시, S-09 실적일정 | 무료 API, 호출 제한 존재 |
| 네트워크 | 전용선 또는 co-location 권장 | R-01~R-03 지연 최소화 | 지연 50ms 이내 목표 |

---

## 9. CEO 확인·결재 요청

**즉시 실행 (Day 1~2):**

DB에서 다음 쿼리를 실행하여 현재 데이터 현황을 파악해야 합니다.

```sql
-- 1) 전체 테이블 목록
SELECT table_name, pg_size_pretty(pg_total_relation_size(quote_ident(table_name)))
FROM information_schema.tables WHERE table_schema = 'public';

-- 2) 분봉 데이터 범위
SELECT MIN(datetime), MAX(datetime), COUNT(DISTINCT ticker), COUNT(*) FROM v4_minute_bar;

-- 3) 일봉 후보 테이블 탐색
SELECT table_name FROM information_schema.tables
WHERE table_name LIKE '%daily%' OR table_name LIKE '%price%' OR table_name LIKE '%ohlc%';

-- 4) 수급 후보 테이블 탐색
SELECT table_name FROM information_schema.tables
WHERE table_name LIKE '%investor%' OR table_name LIKE '%foreign%' OR table_name LIKE '%institution%';

-- 5) 업종 후보 테이블 탐색
SELECT table_name FROM information_schema.tables
WHERE table_name LIKE '%sector%' OR table_name LIKE '%industry%';

-- 6) 종목 마스터 탐색
SELECT table_name FROM information_schema.tables
WHERE table_name LIKE '%stock%' OR table_name LIKE '%master%' OR table_name LIKE '%ticker%';
```

KIS OpenAPI에서 다음 기능의 지원 여부를 확인해야 합니다. 실시간 체결 WebSocket(구독 종목 수 제한), 실시간 호가 WebSocket(구독 종목 수 제한), 과거 분봉 조회 REST(1회 응답 건수, 조회 가능 기간), VI 발동/해제 실시간 통보(전용 채널 유무), 투자자별 매매동향 실시간 조회(호출 빈도 제한), 업종 지수 실시간 조회, KOSPI/KOSDAQ/VKOSPI 실시간 조회 여부를 확인합니다.
