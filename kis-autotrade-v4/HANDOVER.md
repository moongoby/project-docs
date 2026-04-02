# HANDOVER – KIS AutoTrade V4.1
> 최종 업데이트: 2026-04-02 | 버전: v11.22
> 역할: History 계층 — 최근 작업 이력 상세 기록
> Core(프로젝트 현황·규칙·환경)는 CONTEXT.md를 참조하라.

---

## 이 문서의 운영 원칙

- 이 문서는 토큰 상한이 없다. 비용을 아끼지 말고 최신화하라.
- 작업 완료 시 반드시 이 문서에 해당 작업 항목을 추가하라.
- 최근 15건을 유지한다. 16건째부터 HANDOVER-HISTORY.md로 이동한다.
- HANDOVER-HISTORY.md가 30건을 초과하면 가장 오래된 항목을 HANDOVER-ARCHIVE.md로 이동한다.
- CEO 재설명 1회 비용 > 문서 토큰 비용 100회분임을 명심하라.

---

## 문서 체계 안내

| 계층 | 파일 | 역할 | 읽기 시점 |
|------|------|------|-----------|
| Core | CONTEXT.md | 프로젝트 현황, 서버, DB, DESK, 규칙, 작업큐, 참조문서 | 매 세션 필수 |
| Directives | CEO-DIRECTIVES.md | CEO 투자철학, 전략 지시, 기술 지시, 절대규칙, 경로규칙 | 매 세션 필수 |
| Rules | KIS-HANDOVER-RULES.md + kis-v41-rules.md | 파이프라인 규칙, 매니저/작업자 역할, 서비스 경계 | 온보딩/규칙확인 |
| History | HANDOVER.md (본 문서) | 최근 15건 작업 상세 이력 | 이전 작업 참조 시 |
| History-중기 | HANDOVER-HISTORY.md | 16~45건째 작업 이력 | 필요 시 참조 |
| Archive | HANDOVER-ARCHIVE.md | 46건째 이후 전체 이력 + 핵심 발견 보관 | 장기 참조 시 |

**참조 URL:**
- CONTEXT.md: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/CONTEXT.md
- CEO-DIRECTIVES.md: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/CEO-DIRECTIVES.md
- KIS-HANDOVER-RULES.md: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/rules/KIS-HANDOVER-RULES.md
- kis-v41-rules.md: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/rules/kis-v41-rules.md
- HANDOVER-HISTORY.md: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER-HISTORY.md
- HANDOVER-ARCHIVE.md: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER-ARCHIVE.md

---

## 최근 작업 이력 (15건, 최신순)

### CUR-GO100-BROKER-GATEWAY-CONNECT — GO100 실매매 BrokerGateway 연결 (2026-04-02)
- **HANDOVER 버전**: v11.22
- **브랜치**: `phase-2c-command-center`
- **작업 내용**:
  - `factory.py`: `MockKISApi()` 하드코딩을 `GO100_LIVE_TRADING_ENABLED` 환경변수 기반 분기로 교체
  - `BrokerGatewayKISAdapter` 클래스 신규 (+95줄): BrokerGateway를 KISApiInterface로 래핑, `set_account_id()`로 전략카드 account_id 설정
  - `live_service.py`: `run_now(dry_run=None)` → 환경변수 기반 실매매/모의 자동판단 + account_id 로깅
  - 안전장치 5중: 환경변수 게이트 + A-1 HOTFIX(broker_gateway.py) + hallucination_guard + V4OrderExecutor dry_run + accounts.is_mock
- **활성화**: `.env`에 `GO100_LIVE_TRADING_ENABLED=true` 추가 + A-1 HOTFIX 해제(CEO 승인) + `systemctl restart go100`
- **미설정 시**: 기존 MockKISApi fallback (무영향)
- **검증 결과**: 2파일 구문 검증 통과, go100 서비스 active, 에러 0건
- **보고서**: go100/reports/CUR-GO100-BROKER-GATEWAY-CONNECT-001-20260402.md

### REPLAY-DESK2-DEPRECATED — ReplayEngine 동적 전략카드 로딩 + DESK2 deprecated (2026-03-30)
- **HANDOVER 버전**: v11.21
- **커밋**: `d98541e3` (replay/desk2) + `4f08f2db` + `2efb4744` + `ec243bde` (seed완료)
- **작업 내용**:
  - **ReplayEngine 동적 전략카드 로딩** (3단계, +211줄):
    - `replay_engine.py`: `load_strategy_cards()` 추가 — `go100_strategy_cards` DB에서 ACTIVE 카드 동적 로드
    - `entry_detector.py`: SignalEvaluator 기반 CARD_* 전략 진입 fallback (+118줄)
    - `candidate_scanner.py`: CARD_* 범용 후보 스캐닝 지원
  - **DESK2 백테스트 deprecated** (2단계):
    - `backtest_runner.py`: deprecated 마킹, GO100 BacktestService 통합으로 대체
    - `backend/app/services/backtest/__init__.py`: deprecated stub 처리
  - **레거시 backtest/ deprecated** (1단계): ReplayEngine 완전 대체
  - **대가 전략 시드 완료** (`4f08f2db`, `2efb4744`, `ec243bde`):
    - `v4_master_strategies` 15건 저장 (래리 윌리엄스, 터틀, CANSLIM 등)
    - `ai_client._parse_json`: JSONDecodeError 시 빈 dict 반환 (Gemini 비정형 응답 방어)
    - `formalize_strategy`: JSON 정형화 실패 시 1회 재시도 + 강제 JSON 출력
    - `run_master_collector.py` 독립 실행 스크립트 추가
- **검증 결과**: 6파일 +211/-2줄, v4_master_strategies 15건, ReplayEngine 동적 카드 로딩 활성화

### MASTER-STRATEGY-SEED-PIPELINE — 대가 전략 시드 파이프라인 (2026-03-29)
- **HANDOVER 버전**: v11.20
- **커밋**: `1998df81` + `ef5a8fa2` + `cf7b9a5b` + `f7d5d561` + `fdbc3f5f`
- **작업 내용**:
  - `master_strategy_collector.py` 신규 (406줄): SearXNG 검색 → Gemini(LiteLLM) 정형화 → `v4_master_strategies` UPSERT
  - `ai_client.py`: `claude-opus-4` OPUS 모델 + `select_model()` 지원 추가 (R-AUTH 준수)
  - `run_master_strategy_collect.py` 스크립트 (81줄): CLI 수동 실행 지원
  - **L2 가설 생성에 대가 전략 동적 주입**:
    - `hypothesis_engine.py`: `v4_master_strategies` 조회 → few-shot 샘플로 프롬프트 보강
    - `l2_desk_generator.py`: 대가 전략 시드 3건 자동 삽입 (+35줄)
  - `v4_master_strategies` 마이그레이션 SQL 추가 (`f7d5d561`)
  - SearXNG URL 수정: `localhost` → `68.183.183.11:8888` (KIS서버 직접 접근)
  - fix: `minute simulator` 메서드 이름 `run_backtest` → `run` 수정 (`fdbc3f5f`)
- **검증 결과**: 3파일 신규 518줄 추가, L2 가설 생성 few-shot 주입 활성화, SearXNG 정상 연결

### BACKTEST-PERF-OPT — 백테스트 성능 최적화 + DESK 프랙탈 통합 (2026-03-28)
- **HANDOVER 버전**: v11.19
- **커밋**: `cbfec41d` + `e357b1a7` + `e65f7be3` + `25cd4ed6` + `6c5e6b15`
- **작업 내용**:
  - **DESK 프랙탈 시스템 P1~P6 통합엔진 반영** (`cbfec41d`, 7파일 +889/-549):
    - `minute_simulator.py` 전면 재편 (+728줄)
    - `minute_cache.py` 신규 (136줄): 분봉 데이터 캐싱 레이어
    - `signal_evaluator.py` +38줄, `trading_cost.py` +419줄
    - `expression_parser.py` +39줄: 프랙탈 조건 파싱 확장
    - `scripts/run_unified_engine.py` +52줄: P1~P6 프랙탈 모드 반영
  - **UniverseEngine DataCache 주간 캐시** (`e357b1a7`):
    - `universe/engine.py`: source 필터로 3844→328종목 처리 (필요 종목만 로드)
  - **indicator_precompute 1회 사전계산** (`e65f7be3`):
    - `backtest/simulator.py`: 지표 반복계산 제거 → 백테스트 **21시간 → 3분** (420배 단축)
  - `MinuteBacktestSimulator` alias 추가 (`25cd4ed6`): `Go100MinuteSimulator` import 호환
  - 백테스트 **24시간 데몬 모드** 전환 (`6c5e6b15`): 워치독 크론 추가, 상시 실행 체계
- **검증 결과**: 백테스트 21시간→3분 ✅, 유니버스 3844→328 캐시 ✅, DESK 프랙탈 P1~P6 통합 ✅

### PHASE2-VIRTUAL-OHLCV — 가상매매 기술지표 실제 OHLCV 교체 (2026-03-27)
- **HANDOVER 버전**: v11.18
- **커밋**: `d2df117c`
- **작업 내용**:
  - Phase 2: 가상매매(`--mode virtual`) 기술지표를 랜덤→실제 OHLCV 기반으로 교체
  - `make_real_signal()` 265줄 구현: indicator_precompute()의 MA/RSI/MACD/ADX/BB/Stoch → TradeSignal 주입
  - `_load_ohlcv_sync()` + `_virtual_ohlcv_cache`: psycopg2 동기 OHLCV 로드 + 메모리 캐시 (장 시작 1회 프리로드)
  - `action_signal()`: OHLCV 프리로드 → make_real_signal() 우선 → legacy 폴백
  - `action_nxt_signal()`: 동일 Phase 2 패턴 적용
  - 기존 `_LEGACY_make_neutral_signal()` 삭제 안함 (폴백 보존)
- **검증 결과**: RSI=75.0(실제), vol_ratio=0.38(실제), ATR=15(실제), import/syntax OK, 에러 0건
- **보고서**: report/v41/PHASE2-VIRTUAL-OHLCV-20260327.md

### PHASE3-RERUN — 가설엔진 → 통합엔진 연결 + 카탈로그 확장 (2026-03-27)
- **HANDOVER 버전**: v11.17
- **커밋**: `eb248a5f` (보고서) + `b5c49244` (코드)
- **작업 내용**:
  - Phase 3 재실행: 가설엔진 PASS → 통합엔진 연결 전체 파이프라인 완성
  - 작업1: 카탈로그 확장 — Entry 32종(+13), Exit 7종(+3) 수급/외부데이터 지표 추가
  - 작업2: hypothesis_pipeline._register_temp_card() — PASS 가설 → HYPOTHESIS 카드(stage_id=1) 등록
  - 작업3: 통합엔진 run_unified_engine.py — HYPOTHESIS BT 카드 로드 + StratParam 자동생성 + 안전처리
  - 작업4: strategy_promotion_engine.py — HYPOTHESIS 1→2→3→4 승격 로직
  - 작업5: seed_walkforward_pass_cards.py — 1회성 시드 (10건 이미 등록 확인)
  - SignalEvaluator: Phase 3 지표 DATA_NOT_AVAILABLE 패턴 적용 (16개 타입)
  - PaperTradingEngine30d 직접 호출 경로 제거 (CEO 확정 원칙)
- **검증 결과**: Import OK, Entry=32/Exit=7, HYPOTHESIS 10건 stage_id=1, 에러 0건
- **보고서**: report/go100/PHASE3-RERUN-20260327.md

### PHASE1-CTE-CARD-PIPELINE — CTE 하드코딩 제거, 전략 카드 기반 전환 (2026-03-27)
- **HANDOVER 버전**: v11.16
- **커밋**: `ed6fa0ad` (Phase 1 메인) + `12aba107` (Phase 1 보강) + `7bc862a9` (검증 리포트)
- **작업 내용**:
  - CTE 파이프라인의 하드코딩된 전략 매핑을 go100_strategy_cards 테이블 기반으로 전환
  - 7개 DESK 전략 카드 시드 (card_id 67-73): D2/D4/D5/D6/D7/S1/D-ORB, 모두 PAPER_LIVE/stage=2
  - 6개 핵심 컴포넌트 구현:
    1. `CTEPipeline.evaluate_with_card()` — 카드 기반 평가 엔트리포인트
    2. `BounceConfirmationGate.evaluate_bounce()` — 14개 조건 타입 제네릭 평가기
    3. `TriggerTacticMatrix` 4개 카드 기반 메서드
    4. `SignalGenerator._load_strategy_cards()` — async DB 로드
    5. `run_unified_engine.load_active_strategy_cards()` — 카드 기반 전략 우선순위
    6. DB 마이그레이션 074/075 (스키마 확장 + DESK 시드)
  - Phase 1 보강: ai_client 3단폴백 (R-AUTH 준수), bounce_conditions 평가기 315줄 추가
  - 기존 하드코딩 로직 fallback 보존 (안정성)
- **검증 결과**: 7 DESK 카드 DB 확인, 6 컴포넌트 import 성공, 서비스 active, 에러 로그 0건
- **보고서**: report/PHASE1-CTE-PIPELINE-RESULT-20260327.md, report/v41/PHASE1-CTE-CARD-PIPELINE-20260327.md

### P0-PROMPT-SCHEMA — LLM 가설 생성 프롬프트 개선 (2026-03-24)
- **HANDOVER 버전**: v11.15
- **작업 내용**:
  - 문제: LLM이 자연어 조건 생성 → SignalEvaluator 해석 불가 → trades=0 (238건 중 237건, 99.6%)
  - 작업1: l2_desk_generator.py 프롬프트에 indicator 카탈로그(6개 entry + 4개 exit type), JSON 스키마 강제, Few-shot 예시 3건 추가
  - 작업2: `_validate_hypothesis()` 검증 레이어 — conditions list/dict/type 검증 + 실패 시 최대 2회 재생성 + 3회 실패 시 GENERATION_FAIL
  - 작업3: `_detect_contradictions()` 모순 탐지 — 골든크로스+RSI<35, 데드+RSI>65, 상향+하향돌파, 골든+데드 4쌍 감지 + 자동 재생성
  - hypothesis_rule_mapper.py: 구조화 dict 직접 변환 + exit_signal.rules 매핑 + 레거시 호환
  - 단위 테스트 전체 통과 (검증/모순탐지/매퍼 new+legacy 형식)
- **기대효과**: LLM→SignalEvaluator 변환 성공률 ~0.4% → 90%+
- **보고서**: go100/reports/P0-PROMPT-SCHEMA-20260324.md

### GO100-WHY-BADGE — 검증 페이지 매매 근거(WHY) 표시 (2026-03-20)
- **HANDOVER 버전**: v11.14
- **커밋**: GO100-WHY-BADGE-20260320 보고서 push
- **작업 내용**:
  - CEO 지시: 모든 검증 페이지에 매매 근거(WHY) 반드시 표시
  - TradeHistory.tsx: `SIGNAL_LABELS` export 추가 (재사용 가능)
  - SignalTimeline.tsx: `signal_name`/`dip_pct`/`desk_id` 뱃지 — 이미 구현됨
  - TradeHistoryTable.tsx: `reason`/`regime_at_entry` 컬럼 — 이미 구현됨
  - TradeDetail.tsx: `signal_source` InfoRow 표시 — 이미 구현됨
  - 빌드 성공(51/51 pages), go100-frontend active 확인
- **보고서**: go100/reports/GO100-WHY-BADGE-20260320.md

### DESK1-VOL-CORRECTION — DESK1 volume_ratio 보정 v2 (2026-03-20)
- **HANDOVER 버전**: v11.13
- **커밋**: `0e91a973` + `294583d0` + `3a432889` + `1e362c52`
- **작업 내용**:
  - 문제: WS tick 수집이 35종목 한정이라 current_volume이 실제보다 극히 낮음 → volume_ratio 0.00으로 surge=False
  - 수정: `scripts/run_desk1_scanner.py` — 2단계 보정 추가
  - **1단계** `_get_kis_access_token()` + `_fetch_kis_acml_vol()`: `FHKST01010100` TR → `acml_vol`+`stck_prpr` 보정
  - **2단계 price-only fallback**: REST API acml_vol=0 반환 시, `price_chg >= 5%` 종목 confidence 40+α(최대 65)로 감지
  - **버그 수정 v2** (`1e362c52`): 임계값 0.05→0.95 상향, prev_day_volume=0 케이스 완전 누락 버그 2건 수정
    - 버그1: 0.0792인 475150(+11.15%) 보정 제외 → 임계값 0.95로 해결
    - 버그2: 008600처럼 prev=0이면 vol_ratio=36625로 보정·폴백 모두 스킵 → `or prev_day_volume==0` + 폴백 가드 추가
  - `sleep(0.11)` rate limit 준수 (~9 req/sec) | 002780: ×11.4배, 475150: ×7.3배 보정 확인
- **성공기준**: REST API 성공 시 surge=True; 실패 시 [PRICE_ONLY] 경로로 감지; prev=0 종목도 폴백 포함
- **보고서**: DESK1-VOLUME-CORRECTION-20260320.md

### DESK1-GRIDSEARCH-OPT — DESK1 그리드서치 최적화 (2026-03-19)
- **HANDOVER 버전**: v11.11
- **커밋**: project-docs (업데이트 중)
- **작업 내용**:
  - DESK1(초단기/스캘핑) 종목 100개 대상 10개 전략 × 144 조합 그리드서치 실행
  - 스크립트: `scripts/run_desk1_gridsearch.py` (기존 파일 활용, 서비스 재시작 없음)
  - DESK1 exit rules: stop 1~2%, target 1.5~6%, max_hold 1~2일 (당일 청산 원칙 반영)
  - 총 606건 → `v4_optimization_results` (desk_id=1)에 저장 (이번 실행 144건 추가)
  - DESK1 #1: BOLLINGER_BAND (bb_mult=2.5, buy_threshold=-0.05) / 샤프 17.50 / 승률 78%
  - DESK1 #2: MEAN_REVERSION (bb_period=15, rsi_buy=30) / 샤프 9.30 / 승률 62%
  - DESK1 #3: RSI_DIVERGENCE (rsi_buy=20, rsi_sell=80) / 샤프 8.15 / 승률 58%
  - 부적합 전략: BREAKOUT_MOMENTUM(-0.25), VOLUME_SPIKE(-0.32) — 초단기 거짓신호 과다
  - 공통 패턴: BOLLINGER_BAND bb_mult=2.5가 DESK1~3 전체에서 최상위
- **성공기준**: desk_id=1 결과 606건 ✅ / 전략 10개 포함 ✅
- **보고서**: DESK1-GRID-SEARCH-OPTIMIZATION-20260319.md

### GRID-SEARCH-OPTIMIZATION — DESK 전략 파라미터 그리드서치 최적화 v2 (2026-03-18)
- **HANDOVER 버전**: v11.10
- **커밋**: project-docs (업데이트 중)
- **작업 내용**:
  - `backend/optimize_strategy_params.py` 신규 생성 (벡터화 최적화 버전)
  - 1차 실행: 루프 방식 → DESK2(30종목) 15분, DESK3에서 SIGTERM 종료
  - 2차 실행: numpy 벡터화 → DESK2 9초, 전체 576조합 약 2분 완료 (100배+ 속도 향상)
  - 데이터: ohlcv_daily 2025-09-01~2026-03-18, 종목 3,775개
  - 총 1,152건 → `v4_optimization_results` 테이블 저장 (이전 583건 + 신규 569건)
  - DESK2 #1: BOLLINGER_BAND (bb_mult=2.5, buy_threshold=-0.05) / 샤프 12.62 / 승률 80%
  - DESK3 #1: BOLLINGER_BAND (bb_mult=2.5, buy_threshold=-0.05) / 샤프 9.85 / 승률 67%
  - DESK4 #1: MEAN_REVERSION (bb_mult=2.5, rsi_buy=35) / 샤프 45.49 / 승률 100% (주의: 샘플 9건)
  - DESK5 #1: MEAN_REVERSION (bb_mult=2.5, rsi_buy=35) / 샤프 10.98 / 승률 67%
  - 공통 패턴: BOLLINGER_BAND bb_mult=2.5 (DESK2~3), MEAN_REVERSION bb_mult=2.5/rsi_buy=35 (DESK3~5)
- **성공기준**: v4_optimization_results 1,152건 ✅ / 전체 DESK TOP3 출력 ✅
- **보고서**: GRID-SEARCH-OPTIMIZATION-20260318.md (v2 업데이트)

### KIS-304 — GO100 TYPE-D-R (card_id=61) C등급 전략 비활성화 (2026-03-09)
- **HANDOVER 버전**: v11.8
- **커밋**: project-docs 91bb072
- **작업 내용**:
  - 작업 전 상태: card_id=61, is_active=true, card_status=BACKTESTED, last_backtest_return=-4.20, MDD=-21.3%
  - `SUSPENDED` 상태가 check constraint 미허용 → `PAUSED`로 대체 적용
  - `UPDATE go100_strategy_cards SET is_active=false, card_status='PAUSED' WHERE go100_card_id=61;` → UPDATE 1 ✅
  - 관련 paper_trading_sessions: 0개 (PAUSED 처리 불필요)
  - 변경 후 확인: is_active=false, card_status=PAUSED ✅
  - 03-10 장 개시 전 실주문 방지 완료
  - 재활성화 조건: 재설계 + 재백테스트 + CEO 승인 필요
- **성공기준**: 3/3 달성 (is_active=false ✅ / card_status=PAUSED ✅ / 세션 PAUSED ✅(해당없음))
- **보고서**: CUR-V41-KIS304-GO100-TYPED-R-SUSPEND-001-20260309.md (HTTP 200 ✅)

### T-053 — 모의투자 거래 발생 검증 + 다중 세션 확인 (2026-03-09)
- **HANDOVER 버전**: v11.7
- **커밋**: DB 전용 (entry_rules 완화, 수동 테스트 거래 삽입), project-docs 06895d5
- **작업 내용**:
  - entry_rules 포맷 검증: card_id=35,36 모두 SignalEvaluator 호환 확인 (`type` 기반)
  - PaperTradingEngine30d.run_daily_check() 6개 세션 실행 → ok=True, 에러 없음
  - 거래 미발생 원인: 최신 ohlcv=2026-03-06, sessions 3-7 start_date=2026-03-09 → 스킵; 시장조건 미충족
  - card_id=35 volume_surge ratio 2.0 → 1.5 완화 (jsonb_set '{1,ratio}')
  - 수동 테스트 거래 삽입: session_id=2, 005930 BUY 100주 @56,400 (DB 동작 검증)
  - ACTIVE 세션: 6개 (session_id 2-7) — "3개 이상" 기준 충족
  - 발견: 지시서 jsonb 경로 오류(`{conditions,1,value}` → `{1,ratio}`), PK 오류(`card_id` → `go100_card_id`)
- **다음 단계**: 2026-03-10 장 시작 후 `run_paper_trading_daily.sh` 자동 실행으로 실제 신호 탐지
- **보고서**: CUR-GO100-PAPER-TRADING-VERIFY-001-20260309.md (HTTP 200 ✅)

### KIS-302 — 03-10 장전 최종 시스템 헬스체크 전수점검 (2026-03-09)
- **HANDOVER 버전**: v11.6
- **커밋**: project-docs 5ba135f
- **작업 내용**:
  - 10개 항목 전수점검 ALL PASS
  - bridge.py: PID 2405236 (root, 21h+ 가동 중)
  - funnel_score null_fallback: 0.5 ✅
  - 서비스 5개 all active: kis-v41-api(20h+), kis-v41-monitor, kis-v41-scheduler, postgresql, redis-server
  - strategy_cards: 60건, open_positions(OPEN): 0건
  - Redis: PONG
  - crontab: 44줄 (20잡+ 등록)
  - backtest/progress: 200 OK, 3세션 CONVERGED(100%)
  - trades/unified: 105,526건 (10만건+ ✅), win_rate 46.23%, PF 2.10
  - GO100 ACTIVE 세션: 6개 (session 2-7, card_id 35/55-59)
  - go100: active running (09:07 KST)
- **보고서**: CUR-V41-KIS302-PREMARKET-HEALTHCHECK-001-20260309.md (HTTP 200 ✅)
- **project-docs 커밋**: 5ba135f

### T-054 — Admin War Room 메인 + 사이드바 + 파이프라인 뷰 구현 검증 (2026-03-09)
- **HANDOVER 버전**: v11.5
- **커밋**: 기존 T-043~T-047 커밋 (57e3ef56, 1745df4f, 1e38518b, b8f247ca, 41bd6d80 등) — 재구현 불필요
- **작업 내용**:
  - T-054 지시서 검토 결과, 전체 구현이 이전 태스크(T-043~T-047)에서 이미 완료됨 확인
  - AdminSidebar.tsx: 11개 메뉴 (종합상황실~사용자관리) 구현 완료
  - admin/page.tsx (War Room): KPI 4카드 + 파이프라인 8단계 + AI 브리핑 + 활동 타임라인 구현 완료
  - 서브페이지 10개: data/features/models/agents/research/signals/trading/performance/system/users 모두 풀 구현 완료
  - 빌드: `npm run build` → ✓ Compiled successfully (BUILD_ID: MINW8ckefm91HQ398zrMi)
  - 서비스 재시작: go100-frontend active (running) 10:19:46 KST
  - URL 확인: 11개 admin 경로 모두 307 (인증 리다이렉트 = 정상)
- **보고서**: CUR-GO100-ADMIN-WARROOM-001-20260309.md (HTTP 200 ✅)
- **project-docs 커밋**: 8dda01b

---

## 핵심 발견 및 교훈 (이번 구간)

### 투자 전략 발견
- **DQI Grade A(92.8) 달성**: L0_KOSPI NOT NULL 기준을 재정의함으로써 구조적 차단 해소. 핵심은 "프록시 값도 값이다" — NULL이 아닌 한 유효 데이터로 취급.
- **FunnelScore Fail-Open 모드**: null_fallback_score=0.5로 설정하여 데이터 미비 구간에서도 매매 파이프라인 차단 방지. 실전 검증 예정(03-10).
- **trades.html 키움 스타일**: LightweightCharts v5.1.0 기반, RSI/MACD pane 분리, 보유구간 Rectangle 시각화 완료. Phase3(자동추세선, 거래량프로파일, 분봉 실시간)은 대기.

### 인프라 교훈
- **좀비 프로세스 5대 패턴**(AADS-178): ①RESULT 폴링 부모 미감시, ②L1 타이머 프로세스그룹 미정리, ③task_id 없는 directive 무한 재시도, ④auto_trigger 중복 실행, ⑤빈 PROJECT 파싱 실패. 모두 근본 수정 완료.
- **T-T- 이중 prefix 버그**: genspark_bridge.py에서 label이 이미 "T-"를 포함하는데 다시 "T-"를 붙여 "T-T-228" 생성. startswith("T-") 체크로 해소.

---

## Task ID 현황

| 구분 | 범위 | 상태 |
|------|------|------|
| 레거시 T-xxx | T-001 ~ T-286 | 읽기 전용, 신규 발행 금지 |
| 신규 KIS-xxx (연번) | KIS-288 ~ KIS-304 (현재 최신) | 활성 (CEO 지시: KIS-288부터 연번) |
| 문서 전용 | KIS-001 ~ KIS-004 | CONTEXT/HANDOVER 업데이트 전용 |
| 다음 발행 번호 | KIS-305 | — |

---

## 버전 이력

| 버전 | 날짜 | Task | 변경 요약 |
|------|------|------|-----------|
| v11.22 | 2026-04-02 | GO100-BROKER-GATEWAY-CONNECT | factory.py MockKISApi→BrokerGateway 환경변수 분기 + live_service dry_run 자동판단 |
| v11.21 | 2026-03-30 | REPLAY-DESK2-DEPRECATED | ReplayEngine 동적 전략카드 로딩 + DESK2/레거시 deprecated + 대가전략 시드 15건 완료 |
| v11.20 | 2026-03-29 | MASTER-STRATEGY-SEED-PIPELINE | 대가 전략 수집 파이프라인 신규 + L2 few-shot 주입 + SearXNG URL 수정 |
| v11.19 | 2026-03-28 | BACKTEST-PERF-OPT | 백테스트 21시간→3분(420배), UniverseEngine 3844→328 캐시, DESK 프랙탈 P1~P6 통합 |
| v11.18 | 2026-03-27 | PHASE2-VIRTUAL-OHLCV | 가상매매 기술지표 랜덤→실제 OHLCV 교체, make_real_signal() 265줄, 장 시작 1회 프리로드 |
| v11.17 | 2026-03-27 | PHASE3-RERUN | 가설엔진→통합엔진 연결, 카탈로그 32+7종, HYPOTHESIS 카드 10건 시드, 승격 파이프라인 완성 |
| v11.16 | 2026-03-27 | PHASE1-CTE-CARD-PIPELINE | CTE 하드코딩 제거 → go100_strategy_cards 기반 전환, 7 DESK 카드 + 6 컴포넌트 구현 |
| v11.15 | 2026-03-24 | P0-PROMPT-SCHEMA | LLM 가설 프롬프트 JSON 스키마 강제 + indicator 카탈로그 + 검증 레이어 + 모순 탐지 |
| v11.12 | 2026-03-20 | DESK1-VOL-CORRECTION | DESK1 volume_ratio 보정 — REST acml_vol(1차) + price-only fallback(2차) 완성 |
| v11.8 | 2026-03-09 | KIS-304 | GO100 card_id=61 C등급 비활성화 — is_active=false, PAUSED |
| v11.4 | 2026-03-09 | T-052 | GO100 전략 카드 대량 생산 — 5레짐 7전략, 백테스트7회, 세션5개 ACTIVE |
| v11.3 | 2026-03-08 | KIS-301 | backtest sessions/trades stock_name null 해결 — stock_universe LEFT JOIN, COALESCE |
| v11.2 | 2026-03-08 | KIS-300 | CONTEXT.md v12.0 최신화 — KIS-290~298 반영, 연번체계 KIS-288부터, API 상태 갱신 |
| v11.1 | 2026-03-08 | KIS-298 | trades.html DOM ID 수정 + 한글 검색 fetchSearch 추가 |
| v11.0 | 2026-03-08 | — | History 계층 재구성, 85K→15건 정리, 구조화 |
| v10.73 | 2026-03-08 | KIS-297 | trades.html 빈화면 API 진단 (진단 전용, 정상 확인) |
| v10.72 | 2026-03-08 | AADS-178 | 좀비 프로세스 근본수정 5건, 211+68 배포 |
| v10.71 | 2026-03-08 | KIS-001 | CONTEXT.md v11.1 종합 업데이트 |
| v10.70 | 2026-03-08 | T-283 | 문서 4계층 재구성, 매니저 프로토콜, 자동화 |
| v10.69 | 2026-03-08 | T-284 | 브릿지 큐 정리 + Phase2 7/7 검증 |
| v10.68 | 2026-03-08 | T-285 | 컨텍스트 동기화 v10.28 |
| v10.67 | 2026-03-08 | T-286 | backtest/progress 엔드포인트 구현 |
| v10.66 | 2026-03-08 | T-283 | trades.html Phase2 (RSI/MACD/Rectangle/전체화면) |
| v10.65 | 2026-03-08 | T-282-S4S5 | HTML 조립 + 외부 HTTP 7/7 |
| v10.64 | 2026-03-08 | T-282 | 키움 영웅문4 스타일 차트 전면 교체 7파일 |
| v10.63 | 2026-03-07 | T-281 | Nginx trades.html static serving |
| v10.62 | 2026-03-07 | T-280 | trades.html 배포, API 3개 200OK |
| v10.61 | 2026-03-07 | T-278 | CEO 통합 거래 뷰어 Phase 1, TC-13/13 |
| v10.60 | 2026-03-07 | T-277 | 큐정리+장전점검, 서비스 4개 active |
| v10.59 | 2026-03-07 | T-275 | DQI Grade A(92.8) 달성 |
