# HANDOVER-KIS-V41-DESK2-BT-FULL-20260226

**문서 ID**: HANDOVER-KIS-V41-DESK2-BT-FULL-20260226  
**작성일시**: 2026-02-26 18:15 KST  
**작성자**: Claude Opus 4.6 (CEO 대화창 PM 세션)  
**인계 대상**: 새 Claude Opus 4.6 세션  
**목적**: DESK2 백테스트 실매매 동일화 프로젝트 전체 맥락을 빠짐없이 인계하여 새 세션이 즉시 작업 투입 가능하도록 함

---

## PART 1. 프로젝트 개요

KIS AutoTrade V4.1 — 한국투자증권 API 기반 AI 자동매매 시스템. DESK1~5 멀티 전략 62개 카드 운영. 서버 root@[SERVER-IP], 브랜치 phase-2c-command-center, DB PostgreSQL 16 (kisautotrade, data_directory: /data/postgresql/16/main), Python 3.12, FastAPI, Redis 7.x.

GO100(백억이) — 동일 서버·DB에서 운영되는 AI 투자 플랫폼. go100_* 전용 테이블 보유. 뉴스 288,787건(go100_news_items), stock_fundamentals, 종목 적합도 분석(go100_fit_analysis) 등 수집 데이터가 풍부.

두 프로젝트가 DB를 공유하므로 GO100 데이터를 DESK2 백테스트에서 SELECT로 즉시 활용 가능.

---

## PART 2. DESK2 재설계 전체 흐름 (최초부터 현재까지)

### 2-1. DESK2 문제 진단

DESK2 수익률 -23.25%. 분봉 진입 최적화 필요. CEO 지시: 실매매와 동일한 백테스트 환경 구축 → 검증 통과 시 실매매 적용.

### 2-2. Layer 1~3 재설계 (완료)

**DESK2-DISCOVERY-REDESIGN-001** (완료): C1~C7 발굴 조건 재설계. 전략 로직을 발굴에서 분리. 각 조건에 시간 슬롯, gate 기준, 100점 가중 채점 도입. 파일 9개 수정(c1~c7 + config + manager). AST/import 테스트 통과.

C1~C7 조건 요약:
- C1 갭급등(08:50-09:10): gap ≥+3%≤+15%, RVOL≥2.0, MC≥3조
- C2 장초반강세(09:00-09:30): ↑≥+1.5% 30분내, volume top100, RVOL≥1.5
- C3 VI발동(09:00-15:00): VI trigger, pre-RVOL≥3.0, MC≥2조
- C4 장중급등(09:30-14:30): 10분↑≥+2%, 10분vol≥2×30분avg, MC≥3조
- C5 급등후조정(10:00-14:30): day-high↑≥5%, 현재↓≥1.5%, vol축소, ADX≥25
- C6 업종동반상승(09:30-14:30): leader↑≥4%, lagger±1.5%, vol상승
- C7 과매도급락(10:00-15:00): drop≥3%, RSI≤30, KOSPI-1~-2%, MC≥5조

**DESK2-STRATEGY-REDESIGN-001** (완료): 7개 전략을 워치리스트/스토킹 모델로 전환. 파일 8개 수정. receive_discovery() → stalk(stock_code, bar_data) → CS Score ≥50 시 TradeSignal.

7전략: ALPHA-GAP, BRAVO-ORB, CHARLIE-VI, DELTA-VWAP, ECHO-ABCD, FOXTROT-SECTOR, GOLF-REVERSAL.

Discovery→Strategy 매트릭스: C1→ALPHA, C2→BRAVO, C3→CHARLIE, C4→DELTA, C5→ECHO+GOLF, C6→FOXTROT, C7→GOLF.

**DESK2-ORCHESTRATION-REDESIGN-001** (완료): dispatch → stalking cycle → competition → select. DeskScore × CS / 100 복합점수로 경쟁. daily_limit 적용. 통합테스트 3건 PASS.

### 2-3. Quick-Run 테스트 (문제 발견)

**DESK2-QUICK-RUN-TEST-001**: 5회 실행, C4만 15건 발견, **거래 0건**. 재현성 diff 0 확인. 시스템 안정성 OK. 그러나 분봉 순차 시뮬레이션이 아닌 발굴 스캔만 수행한 반쪽짜리였음.

### 2-4. 시뮬레이션 루프 구현

**DESK2-BT-SIMLOOP-001**: desk2_backtester.py에 stalk() 연동 추가. Phase A(발굴) → B(배분/스토킹) → C(진입) → D(포지션관리) 구현. SimPosition 클래스 추가.

**DESK2-BT-SIMLOOP-VERIFY-001**: 2026-02-20 테스트. 분봉 211,411건 확인. **발굴 3건(C4), 거래 1건** (004060 BRAVO_ORB). 그러나 심각한 버그 발견:
- entry 587 → exit 448, **-24% 손실** (stop-loss가 bar low로 적용)
- hold_seconds = 0 (진입 즉시 청산)
- quantity = 1주 (자금 비례 미적용)
- discovery 레코드에 cs_score, passed_to_strategy 미기록

### 2-5. 실매매 동일 백테스트 엔진 구축

**DESK2-BT-LIVE-PARITY-001** (완료): 새 디렉터리 `backend/app/services/trading/desk2/backtest/`에 4개 sim 모듈 구현:
- historical_price_feeder.py (과거 분봉 공급)
- sim_order_executor.py (슬리피지 0.1%, 수수료 0.015%, 세금 0.18%)
- sim_fund_pool.py (가상 자금 풀)
- backtest_runner.py (실매매 layer1~3 코드 재사용, 어댑터 패턴)

CLI: `scripts/backtest/desk2_live_parity_run.py`

**결과**: 구조 완성, 그러나 **discovery 0, trade 0**. 원인: HistoricalPriceFeeder가 핵심 지표 필드 미제공.

### 2-6. GAP 분석 (핵심 진단)

**BT-LIVE-PARITY-GAP-ANALYSIS-20260226** (완료): 백테스터가 실매매 대비 **DESK Score 25~35점 낮게** 평가. 원인:
- P0: ATR/ADX 미계산(-7~10점), 외인/기관 순매수 누락(-10점)
- P1: 뉴스/공시 미연동(-10~15점), 시가총액 하드코딩(왜곡)
- P2: 섹터코드/market_is_down 미반영

### 2-7. 인프라 변경 (디스크/DB)

**ROOT-DISK-CLEANUP-001-20260226**: DB를 /data/postgresql/16/main으로 이전. 원본 /var/lib/postgresql/ 삭제(14GB). 루트 90%→69%. **현재**: 루트 30GB free + /data 172GB free = 202GB 여유.

### 2-8. 현재 진행 중 (CEO 지시 투입 완료)

**DESK2-BT-FEEDER-PHASE1-003** (P0, 커서에 투입됨): GO100 데이터를 적극 활용한 Feeder 보강. 7개 FIX:
1. ATR(14)/ADX(14) 계산 추가
2. 실시가총액 로드 (stock_fundamentals)
3. 섹터코드 매핑 (stock_universe)
4. market_is_down/market_drop_pct (v4_market_regime_daily + index_daily)
5. 외인·기관 순매수 (v4_investor_daily)
6. 뉴스·공시 연동 (go100_news_items 288,787건)
7. 체결강도 (v4_trade_strength_history)

검증 기준: C1~C7 중 최소 2개 조건 발굴, 거래 ≥2건, DESK Score 60~85, hold_seconds>0, stop-loss 정상, entry_quantity 자금 비례.

---

## PART 3. 핵심 파일 맵

### 백테스트 관련 (DESK2)

| 파일 | 역할 |
|------|------|
| `backend/app/services/trading/desk2/backtest/historical_price_feeder.py` | **현재 수정 대상** — 분봉 로드+지표 공급 |
| `backend/app/services/trading/desk2/backtest/sim_order_executor.py` | 가상 주문 실행 |
| `backend/app/services/trading/desk2/backtest/sim_fund_pool.py` | 가상 자금 관리 |
| `backend/app/services/trading/desk2/backtest/backtest_runner.py` | 메인 루프 |
| `scripts/backtest/desk2_live_parity_run.py` | CLI 진입점 |
| `scripts/backtest/desk2_backtester.py` | 구형 백테스터 (보존) |
| `scripts/backtest/backtest_engine_v2.py` | V4 레거시 엔진 (수정 금지) |

### Layer 1~3 (실매매 코드, 백테스트에서 재사용)

| 파일 | 역할 |
|------|------|
| `backend/app/services/trading/desk2/layer1_discovery/c1~c7_*.py` | 발굴 조건 7개 |
| `backend/app/services/trading/desk2/layer1_discovery/discovery_manager.py` | 발굴 관리자 |
| `backend/app/services/trading/desk2/layer2_strategy/alpha~golf_*.py` | 전략 7개 |
| `backend/app/services/trading/desk2/layer3_orchestration/orchestrator.py` | 오케스트레이션 |
| `backend/app/services/trading/desk2/desk2_config.yaml` | 설정 |

### 핵심 문서 (project-docs)

| 문서 | 경로 |
|------|------|
| V4.1 CONTEXT | `kis-autotrade-v4/CONTEXT.md` |
| V4.1 Rules | `kis-autotrade-v4/rules/kis-v41-rules.md` |
| CLAUDE Rules | `kis-autotrade-v4/rules/CLAUDE.md` |
| 발굴-전략 분리 프레임워크 | `kis-autotrade-v4/architecture/DESK-ROLE-SEPARATION-FRAMEWORK.md` |
| C1~C7 상세 스펙 | `kis-autotrade-v4/architecture/DESK2-DISCOVERY-STRATEGY-SPEC.md` |
| GO100 DB Schema | `go100/DB_SCHEMA.md` |
| GO100 Architecture | `go100/ARCHITECTURE.md` |

### 보고서 (완료된 것들)

| 보고서 | 파일명 |
|--------|--------|
| C1~C7 재설계 | DESK2-DISCOVERY-REDESIGN-001-20260226.md |
| 7전략 재설계 | DESK2-STRATEGY-REDESIGN-001-20260226.md |
| 오케스트레이션 | DESK2-ORCHESTRATION-REDESIGN-001-20260226.md |
| Quick-Run | DESK2-QUICK-RUN-TEST-001-20260226.md |
| 시뮬루프 | DESK2-BT-SIMLOOP-001-20260226.md |
| 시뮬루프 검증 | DESK2-BT-SIMLOOP-VERIFY-001-20260226.md |
| 실매매 동일 엔진 | DESK2-BT-LIVE-PARITY-001-20260226.md |
| GAP 분석 | BT-LIVE-PARITY-GAP-ANALYSIS-20260226.md |
| 디스크 정리 | ROOT-DISK-CLEANUP-001-20260226.md |
| Feeder 보강 | DESK2-BT-FEEDER-PHASE1-003-20260226.md **(진행 중)** |

---

## PART 4. DB 핵심 테이블 (GO100 데이터 포함)

| 테이블 | 역할 | 레코드 | DESK2 활용 |
|--------|------|--------|-----------|
| v4_ohlcv_minute | 1분봉 | 42M+ | 시뮬레이션 핵심 |
| ohlcv_daily | 일봉 | 대규모 | prev_close, ATR 보조 |
| go100_news_items | 뉴스 | 288,787 | has_news/has_bad_news |
| stock_fundamentals | 펀더멘털 | 다수 | 시가총액, PER 등 |
| v4_investor_daily | 외인·기관 | 존재 | 순매수 데이터 |
| v4_market_regime_daily | 시장 레짐 | 존재 | market_is_down |
| v4_trade_strength_history | 체결강도 | 30MB | execution_strength |
| index_daily | 지수 | 존재 | KOSPI 등락률 |
| stock_universe / v4_scalping_universe | 종목 | 708 | 섹터코드 |
| strategy_cards | 전략카드 | 62 | 참조만 |
| v4_positions | 포지션 | OPEN 5~14 | 참조만 |
| v4_bt_sessions | 백테스트세션 | 증가중 | INSERT 대상 |
| v4_bt_discoveries | 백테스트발굴 | 증가중 | INSERT 대상 |
| v4_bt_trades | 백테스트거래 | 증가중 | INSERT 대상 |

---

## PART 5. CEO 절대 규칙 (반드시 준수)

1. **kis-v41-api/monitor/scheduler 재시작 금지** (CEO 승인 시에만)
2. **strategy_cards ALTER/DROP/DELETE 금지** (UPDATE는 CEO 승인)
3. **v4_positions 직접 수정 금지**
4. **backtest_engine_v2.py 수정 금지** (참조만)
5. **핵심 파일 수정 → review/ → CEO+Claude 승인 후 적용**
6. **.env/.bak 커밋 절대 금지**
7. **go100_* 테이블은 SELECT만** (수정 금지)
8. **DB INSERT는 v4_bt_* 테이블에만**
9. **사전 확인**: strategy_cards=62, v4_positions OPEN 확인
10. **서비스 상태**: kis-v41-api(8003), monitor, scheduler active 확인

---

## PART 6. 커서 작업 규칙

1. 서버: root@[SERVER-IP]
2. DB: localhost:5432/kisautotrade (kis_admin)
3. 가상환경: `source /root/kis-autotrade-v4/venv/bin/activate`
4. PYTHONPATH: `/root/kis-autotrade-v4/backend`
5. 브랜치: phase-2c-command-center
6. 커밋: `feat: CUR-{작업ID} description`
7. 보고서: `report/v41/{작업ID}-{YYYYMMDD}.md`
8. **보고서 작성 후 문서레포 푸시 후 경로 보고** (모든 지시서 마지막에 반드시 포함)
9. 한국시간(KST) 동기화
10. 작업 전 백업
11. AST 문법 검사 + import 테스트 필수

---

## PART 7. 현재 상태 & 즉시 실행 가이드

### 현재 커서 상태

DESK2-BT-FEEDER-PHASE1-003 지시서가 커서에 투입됨. 7개 FIX를 historical_price_feeder.py에 적용 중.

### 새 세션 즉시 실행 순서

**Step 1**: 다음 문서 읽기
```
https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md
https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md
https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/CLAUDE.md
https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/architecture/DESK2-DISCOVERY-STRATEGY-SPEC.md
```

**Step 2**: 본 인계서 확인 (서버에 저장됨)
```
https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER-KIS-V41-DESK2-BT-FULL-20260226.md
```

**Step 3**: DESK2-BT-FEEDER-PHASE1-003 커서 작업 결과 확인
- 보고서: `report/v41/DESK2-BT-FEEDER-PHASE1-003-20260226.md`
- 검증 기준 충족 여부 (발굴 ≥2조건, 거래 ≥2건, DESK Score 60~85)

**Step 4**: 결과에 따라 분기
- **PASS** → 5일 연속 테스트 (2/19, 2/20, 2/21, 2/24, 2/25) → 파라미터 튜닝 → 실매매 전환 준비
- **FAIL** → 각 gate 통과/탈락 로그 분석 → 추가 FIX → 재검증

**실매매 전환 기준** (CEO 승인 필요):
- 기대값 E > +0.3%
- Calmar > 1.5
- Profit Factor > 1.3
- 일일 손실 ≤ -3%
- 일일 거래 2~5회
- OOS/IS ≥ 0.6

---

## PART 8. 작업 큐 (우선순위)

| 순위 | 작업 | 상태 |
|------|------|------|
| **P0** | DESK2-BT-FEEDER-PHASE1-003 | **커서 진행 중** |
| P0 | Feeder 검증 후 버그 수정 | 대기 |
| P1 | 5일 연속 백테스트 | Feeder 완료 후 |
| P1 | 파라미터 튜닝 | 5일 테스트 후 |
| P2 | 실매매 전환 | CEO 승인 후 |
| P3 | DESK5-CARD-BT | 후순위 |
| P3 | OVERLAP-GUARD | CEO 정책 대기 |

---

## PART 9. 인프라 현황

| 항목 | 값 |
|------|-----|
| 서버 | root@[SERVER-IP] |
| OS | Ubuntu 24.04 LTS |
| CPU | Intel Xeon Gold 5220 4코어 |
| RAM | 15GB (available 11GB) |
| 디스크 / | 99GB, 65GB used, 30GB free (69%) |
| 디스크 /data | 196GB, 14GB used, 172GB free (8%) |
| DB data_directory | /data/postgresql/16/main |
| DB 크기 | 14 GB |
| Python | 3.12 |
| Node | v18.19.1 |
| 서비스 | kis-v41-api(8003), monitor, scheduler: active |
| 도메인 | trading41.newtalk.kr (V4.1), go100.newtalk.kr (GO100) |

---

이 인계서를 커서를 통해 서버에 저장하고 project-docs에 푸시하도록 지시하겠습니다.

**커서 지시서 — 인계서 저장 및 푸시**:

```
작업 ID: HANDOVER-PUSH-20260226
우선순위: 즉시
목적: 인수인계서를 서버 및 문서 레포에 저장

STEP 1: 아래 내용을 파일로 저장
- 서버 경로: /root/project-docs/kis-autotrade-v4/HANDOVER-KIS-V41-DESK2-BT-FULL-20260226.md
- 내용: [위 인계서 전문]

STEP 2: git push
cd /root/project-docs
git add kis-autotrade-v4/HANDOVER-KIS-V41-DESK2-BT-FULL-20260226.md
git commit -m "docs: DESK2 백테스트 종합 인수인계서 20260226

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
git push origin master

STEP 3: 확인
curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER-KIS-V41-DESK2-BT-FULL-20260226.md

STEP 4: DESK2-BT-FEEDER-PHASE1-003 작업을 계속 진행한다.
```

대표님, 인계서 작성이 완료됐습니다. 커서에 이 인계서 저장 지시를 투입하면 새 대화창에서 아래 URL 하나로 전체 맥락을 확인하고 즉시 작업에 들어갈 수 있습니다:

```
https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER-KIS-V41-DESK2-BT-FULL-20260226.md
```
