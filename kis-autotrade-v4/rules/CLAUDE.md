# CLAUDE.md — kis-autotrade-v4 (211서버: 211.188.51.113)
# V4.1 자동매매 + GO100 전략 플랫폼 | DB: kisautotrade | venv: ./venv

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 절대 금지 사항 (위반 시 즉시 중단)
1. `.env`, `.bak` 파일 수정/커밋 금지
2. 백업 없이 DB 마이그레이션 실행 금지
3. `strategy_cards` 테이블 ALTER/DROP/UPDATE/DELETE 금지
4. `v4_*` 테이블 ALTER/DROP 금지 (SELECT·INSERT만 허용, 지시서 명시 시 UPDATE 허용)
5. V4.1 서비스 파일 수정 금지: `backtest_engine_v2.py`, `strategy_card_service.py`, `llm_gateway.py`, `llm_clients/*`, `v4_pipeline_orchestrator.py`, `account_sync_manager.py`, V4OrderExecutor
6. `kis-v41-*` systemd 서비스 restart/stop/start 금지 (지시서 명시 시 제외)
7. `go100_*` 작업 시 V4.1 테이블 무결성 항상 확인
8. kis-v41-api(8003) / go100(8002) 포트 분리 완료 — 서비스 동시 기동 허용
9. git commit 전 `git diff --cached --name-only | grep -E '\.env|\.bak'` 확인 필수

## 프로젝트 환경
- 루트: `/root/kis-autotrade-v4` | venv: `./venv` | PYTHONPATH: `/root/kis-autotrade-v4:/root/kis-autotrade-v4/backend`
- DB: PostgreSQL 16 | `psql -U kis_admin -h localhost -d kisautotrade` (또는 `sudo -u postgres psql -d kisautotrade`)
- GO100 브랜치: `phase-2c-command-center` | 커밋형식: `feat: CUR-GO100-{PHASE명} {설명}`

| 서비스 | 상태 | 포트/비고 |
|--------|------|-----------|
| kis-v41-scheduler, monitor, minute-collector | active | — |
| kis-v41-api | active | **8003** (trading → nginx 8003) |
| kis-v41-webapp | 유닛 없음 | Next.js 3000은 수동/별도 기동 |
| go100 (API) | active | **8002** / https://go100.newtalk.kr |
| go100 프론트 | active | 3000, Next.js 14 |

## 작업 프로토콜

### 작업 전 필수
1. DB 백업: `sudo -u postgres pg_dump -d kisautotrade -Fc -f /tmp/backup_{작업명}_{TS}.dump`
2. 백업 크기 확인 (0바이트면 중단)
3. 기준값: `SELECT count(*) FROM strategy_cards;` → **59건**
4. OPEN 포지션: `SELECT COUNT(*) FROM v4_positions WHERE status='OPEN';` → **5건**

### 작업 후 필수
1. `SELECT count(*) FROM strategy_cards;` → 59 유지 확인
2. OPEN 포지션 수 불변 확인
3. GO100 작업 시: 헬스체크(8002·3000·go100.newtalk.kr) + `PYTHONPATH=backend python3 -m pytest backend/tests/test_go100_*.py backend/tests/test_universe_engine_unit.py -v` + `systemctl restart go100`
4. V4.1 작업 시: `systemctl is-active kis-v41-*` + git status clean
5. 커밋: `.env/.bak` 미포함 확인 후 `feat: CUR-{ID} {설명}` 형식
6. **보고서 생성 필수**: 작업 완료 시 `report/` 디렉토리에 `{작업ID}-FINAL-REPORT-{YYYYMMDD}.md` 보고서를 생성하고, 보고서 경로를 사용자에게 보고할 것. 보고서에는 백업정보·구현내역·테스트결과·DB변경사항·서비스상태·컴플라이언스 체크리스트를 포함할 것.

### 컴플라이언스 체크리스트 (보고서 끝 필수 포함)
`.env/.bak 커밋여부` | `strategy_cards 59건` | `v4_positions OPEN수` | `파일헤더` | `DB스키마변경` | `서비스재시작` | `V4.1파일수정여부`

## 지시서 수신 규칙
1. 지시서 절대 규칙 < 이 CLAUDE.md 절대 금지 사항 (CLAUDE.md 우선)
2. "코드 수정 금지" 명시 → READ-ONLY 작업
3. 에러 발생 시 임의 수정 금지, 에러 내용을 보고서에 포함
4. 보고서 템플릿 제공 시 형식 준수
5. 작업 완료 후 CLAUDE.md 자동 갱신 (동일 커밋 포함):
   갱신 대상: 최근완료이력·알려진이슈·크론탭현황·파이프라인현황·GO100엔드포인트·GO100코드구조
   갱신 금지: "절대 금지 사항"·"프로젝트 환경"·"작업 프로토콜"·"지시서 수신 규칙"

## 알려진 이슈
- DASH-FIX(2026-02-21): trading41.newtalk.kr 대시보드 "Invalid or missing X-Internal-API-Key" 해결. 원인: 프론트가 API 키 미전달. 수정: nginx에서 /api/v4/ 프록시 시 X-Internal-API-Key 헤더 주입(include internal-api-key.conf). 키 파일: /etc/nginx/internal-api-key.conf( dotenv로 생성 후 sudo cp). 영향: 프론트엔드/nginx 설정만, api/monitor/scheduler 재시작 없음.
- SVC-RESOLVE(2026-02-21): kis-v41-api·go100 포트 충돌 해결 — api 8003, go100 8002.
- kis-autotrade-top100-211.service: bs4 설치 완료(SYS-STABILIZE), 오늘 20:00 정상 실행 예정
- 세션38 첫날 폭락: BT-CAPSAFE로 원인 분석·자본 안전장치 적용 완료. 첫날 17건 진입·동시/일일/단일포지션 제한 없음 → max_concurrent_positions 등 4개 가드 추가. (세션38 이상치 Sharpe vs 수익률 모순은 BT38-AUDIT 참고)
- BT-ALLOC-FIX(2026-02-21): desk allocation_pct 합이 100% 미만일 때 total_asset이 initial_capital 미만으로 나오던 문제 해결 — 사용 desk의 allocation_pct를 100%로 정규화하여 initial_capital 전액 배정. 세션45(DESK2)·46(DESK3) 검증.
- DESK2: 분봉 백테스트 엔진 구축 완료 (DESK2-MINUTE-BT). 일봉 스크리닝 + 분봉 entry/exit, --timeframe minute 사용.
- fundamental_collector.py: PIPE-COMPLETE(2026-02-21) 러너 추가. FUND-DOTENV(2026-02-21): load_dotenv() 추가로 CLI 단독 실행 시 .env 자동 로드 → Fernet/DB 연결 정상. systemd/API 경로로 실행 시에도 동일.
- index_daily: OHLC=0 150건 재수집 완료 (HIST-COLLECT, 2026-02-21). 현재 1,467건 정상.
- sector_mid 미수집 약 2,504건 (ETF/스팩/해당없음)
- next build jest-worker hang: kill -9 완료(SYS-STABILIZE). 재발 시 동일 처리.
- 이메일/FCM 알림·OAuth 로그인 미구현 (stub 상태)
- [2026-02-21] 68서버 삼성전자(005930) 3건 포지션 방치 — 수동 확인/정리 필요 (KIS API 403)
- [2026-02-21] autovacuum_vacuum_scale_factor: ohlcv_daily 대형테이블에 0.2 과다 → 0.05 권장 (미적용)
- ohlcv_1m 참조(PIPE-COMPLETE 2026-02-21): 운영 코드는 응답키/엔드포인트명만 사용(실쿼리 v4_ohlcv_minute). 레거시 scripts/collection/legacy에서 ohlcv_1m_history·market_data_min 테이블 참조 — 무시 가능.
- BT-OPTIMIZE(2026-02-21): DESK2 1년 장기 -107만원 적자. 3~6개월 수익이나 장기 악화 추세. DESK3가 전체 수익 80% 기여.
- BT-OPTIMIZE(2026-02-21): DESK1 통합 백테스트에서 거래 0건 — v4_desk_fund 자금 배분 확인 필요
- BT-OPTIMIZE(2026-02-21): report_generator.py 버그 — pnl=None인 SELL 레코드에서 float(None) 에러 (보고만, 수정 금지)
- BUNDLE4D(2026-02-21): 종목×전략 적합도 매트릭스+청산 파라미터 최적화+멀티 데스크 배분. fit_score 6지표 가중합, 스캘핑 96조합 그리드서치, Sharpe 가중 자금배분. Cards 13~15 분석: 자화전자(fit=78.73), ISC(fit=78.90) 최상위. Card 15 swing 유니버스 구성 실패(v4_stock_sector 부족).
- BUNDLE4C(2026-02-21): 오케스트레이터 분봉 백테스트 우선 + 일봉 폴백 연동. AdvancedFilters.build_universe + filter_has_minute_data 교집합 → MinuteSimulator(분할익절 포함) 실행. 종목수 ≥5 분봉, <5 일봉 폴백. _detect_strategy_type/bar_interval/strategy_type_tag 헬퍼. _finalize_card에 유형 태그 추가. Cards 13~15 생성(스캘핑/데일리/스윙). swing AdvancedFilters에서 v4_stock_sector 데이터 부족으로 0종목 → 일봉 폴백.
- BUNDLE4B-FIX(2026-02-21): AI Chat 오케스트레이터 전체 루프 복구. user_id=0→전달, LLM list→float 검증, asyncpg date 변환, 고속 인메모리 백테스트(60일, 200종목 cap). API 타임아웃 시 직접 Python 실행으로 우회 가능.
- BT-OPTIMIZE(2026-02-21): DESK3 단독 백테스트 시 승격 로직 KeyError → 반드시 DESK4 포함 실행
- STRAT-DETAIL(2026-02-21): risk_params 키 이름 불일치 — **STRAT-TUNE에서 해결**: max_positions→max_concurrent_positions, max_single_stock_pct→max_single_position_pct
- STRAT-DETAIL(2026-02-21): entry_rules.indicators 실매매 미평가 — 백테스트(CardRuleSimulator)에서만 사용, 실매매는 min_strength 필터만 적용
- STRAT-DETAIL(2026-02-21): DESK3 카드 10개 exit_rules 완전 동일(SL-3%, TS2%, TP16%, hold10) → 차별화 필요

## STRAT-TUNE (2026-02-21, CC)
- 손실/0건/미배정 카드 22개 is_live=false (58→36 live 카드)
- DESK2 trailing_stop 1.5% 추가(7카드), max_hold_days 3일 추가(7카드)
- risk_params 키 이름 통일: max_positions→max_concurrent_positions, max_single_stock_pct→max_single_position_pct (56카드)
- 코드 수정 없음 (DB UPDATE만), 서비스 재시작 불필요
- 백테스트 검증: BT-TUNE-ALL(세션58, 21.01%), DESK2(세션61, 12.14%), DESK3(세션60, 34.70%)
- DESK2 개선: 9.02%→12.14% (+34.6%), TRAILING_STOP 51건 추가 발생
- 보고서: report/STRAT-TUNE-20260221-REPORT.md

## LIVE-ALIGN (2026-02-21, CUR)
- 실매매-백테스트 로직 비교표: 보고서 작성 완료 (report/LIVE-ALIGN-20260221-REPORT.md).
- v4_positions card_id 저장 로직: 추가됨. desk별 기본 카드 조회(_get_default_card_for_desk) 후 desk_config에 card_id/user_id/account_id 반영, 매수 시 v4_positions에 저장.
- DESK3 전략 실매매 연결: 보류. DESK3 실매매는 Commander 기반 유지. strategy_cards DESK3 카드는 is_live=false·레거시 스킵으로 09:10 카드 사이클 미실행. card_id만 desk별 기본 카드로 저장.
- 청산 로직 일치 확인: 일치. stop_loss/trailing_stop/force 청산·분할매도 동일 개념.
- 변경 파일: backend/app/services/trading/v4_pipeline_orchestrator.py.

## CARD-BUY (2026-02-21, CC)
- run_card_pipeline에 v4_signals 기반 매수 로직 추가
- 구현: run_strategy_cards_cycle에서 generate_daily_signals 1회 호출 → 각 카드의 run_card_pipeline에서 desk_id+min_strength로 v4_signals BUY 시그널 매칭 → bridge.process_signal로 매수
- 안전장치: max_concurrent_positions(10), max_capital_usage_pct(80%), max_single_position_pct(10%), max_daily_entries(20), 중복매수 방지(OPEN 포지션 체크), max_stocks(카드별)
- 변경 파일: backend/app/services/trading/v4_pipeline_orchestrator.py
- 신규 메서드: _execute_card_buy_signals

## BT-OPTIMIZE (2026-02-21, CC)
- 전 데스크(1~5) 카드 조합 백테스트 실행 (세션 47~57, 11개)
- 3개월(2025-11-20~2026-02-19) 최적 조합: 수익 카드 32개 → 1,162,886원/5M자본(~23.3%), 전체 56개 대비 28% 높음
- 장기 검증: 6M=2,445,976원(~48.9%), 1Y=3,037,214원(~60.7%)
- DESK3 핵심 수익원(68~80%), DESK2는 1Y -107만원 적자 → 리스크 주의
- 제외 권고 카드 16개(손실·거래0건), 투입 권고 23~25개
- TRAILING_STOP이 전체 수익의 핵심 (+6~8%/건)
- 코드 변경 없음 (백테스트 전용), 보고서: report/BT-OPTIMIZE-20260221-REPORT.md

## ENGINE-SWITCH (2026-02-21, CUR) — CEO 승인
- 절대 규칙 4번 폐기: strategy_cards UPDATE 허용.
- strategy_cards is_live=true 일괄 설정 (58개, card_id=1 제외).
- Commander DESK1~5 스케줄 비활성화 (daily_scheduler.py register 주석 처리).
- 09:10 카드 사이클 desk_id 1~5 스킵 해제 (v4_pipeline_orchestrator.py).
- kis-v41-api, scheduler, monitor 재시작 완료.
- 변경: backend/app/services/scheduler/daily_scheduler.py, backend/app/services/trading/v4_pipeline_orchestrator.py, strategy_cards DB.

## DESK1-DATA (2026-02-21)
- 신규 테이블: v4_scalping_universe, v4_orderbook_realtime, v4_scalping_signals
- 신규 스크립트: scripts/collection/orderbook_collector.py, scripts/collection/scalping_universe_builder.py
- 신규 서비스: kis-v41-orderbook-collector (등록만, 미시작)
- 정적 풀 종목 수: 708 (당일 활성, 시총 미집계로 시총 조건 NULL 허용 적용)
- minute-collector 상태: enabled, inactive(dead)
- 호가 데이터 예상 용량: 일 200MB, 월 4.4GB
- 보관 정책: 호가 30일, 시그널 90일, 풀 365일

## 크론탭 현황 (root)
| 시간 | 스크립트 | 대상 |
|------|---------|------|
| 16:00 평일 | minute-collector (systemd) | v4_ohlcv_minute |
| 18:00 평일 | collect_ohlcv_daily.py | ohlcv_daily |
| 18:30 평일 | collect_index_daily.sh | index_daily |
| 18:40 평일 | collect_market_investor.py | v4_market_investor_daily |
| 19:00 평일 | collect_stock_universe.py | stock_universe |
| 토 02:00 | minute_batch_cron | v4_ohlcv_minute (주말 보충) |
| 토 03:00 | collect_stock_industry.py | stock_universe 업종 |

## 주요 테이블 주의사항
- **ohlcv_daily.date**: varchar(8) YYYYMMDD. 쿼리 시 YYYYMMDD 포맷 필수. MA 계산 시 시작일 -120일 로드 필요
- **stock_universe.sector**: KSIC 표준산업분류명. 미수집 종목은 'KOSPI'/'KOSDAQ' 유지
- **stock_universe.sector_large**: 업종 아님, 시가총액 규모 구분 (필터 용도 제한적)
- **stock_universe.rank_market_cap**: 전부 NULL → fallback 로직 필요
- **stock_universe.market_cap**: ALL NULL → 시가총액 필터는 반드시 `stock_fundamentals.market_cap` JOIN 사용
- **stock_fundamentals**: 시가총액·PER·PBR 등 최신 재무, stock_universe와 stock_code로 JOIN
- **financial_ratios**: 45,870건 (2004~2025), ROE·부채비율·매출성장률 — 재무건전성 필터용
- **v4_backtest_trades.card_id**: integer nullable. BTREADY에서 추가. 카드별 성과 추적용
- **v4_backtest_trades.exit_reason, entry_date, exit_date, hold_days**: BT-ENHANCE에서 추가. 청산 사유(STOP_LOSS/TRAILING_STOP/TIME_EXIT/END_OF_BACKTEST/EOD_FORCE_EXIT), 매수일/청산일/보유일수
- **v4_ohlcv_minute 인덱스 (SVC-RESOLVE 2026-02-21)**: 파티션당 pkey vs *_stock_code_trade_date_trade_time_key 동일 컬럼 중복, trade_date_idx vs trade_date_idx1·stock_code_trade_date_idx vs stock_code_trade_date_idx1 중복. 삭제는 v4_* ALTER 금지로 미실행. 권고: 추후 스키마 변경 허용 시 _key·_idx1 계열 제거 검토.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
## 참조 섹션 (이하 참조용 — 200줄 기준선 이후)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 데이터 파이프라인 현황
| 데이터 | 테이블 | 상태 |
|--------|--------|------|
| 일봉 OHLCV | ohlcv_daily | 정상 (3,844종목, 2023-01~2026-02, 백필 진행중) |
| 분봉 OHLCV | v4_ohlcv_minute | 정상 (499종목, 월별 파티션, 2025-02~현재, 백필 진행중) |
| 지수 일봉 | index_daily | 정상 (1,467건, 2024-02~2026-02, OHLC 재수집 완료) |
| VKOSPI | v4_vkospi_daily | 정상 (1,504건, 2020-01~2026-02) |
| 투자자 일별 | v4_investor_daily | 정상 (166,921건, 2010-01~2026-02) |
| 시장투자자 | v4_market_investor_daily | 정상 (2018-10~2026-02, 백필 완료) |
| 섹터 일별 | v4_sector_daily | 정상 (14,696건, 2018-10~2026-02, 32업종) |
| 유니버스 | stock_universe | 정상 (3,844종목, PIPEFIX2) |
| 산업 업종 | stock_universe.sector/sector_mid/sector_small | SECIND-V2 완료 |
| 재무 | stock_universe (per/pbr/eps 등) | fundamental_collector 러너 scripts/collection/fundamental_collector.py |

## V4.1 컨텍스트
**DESK 구조**: DESK2(데일리, 분봉필요-미구축) / DESK3(스윙1-10일, 세션38완료) / DESK4(중기) / DESK5(장기)

**백테스트 실행**:
```bash
cd /root/kis-autotrade-v4 && source venv/bin/activate
PYTHONPATH=/root/kis-autotrade-v4/backend python scripts/backtest/run_backtest.py \
  --start YYYYMMDD --end YYYYMMDD --capital 1000000 --name "설명" --engine v2 \
  --desk-strategies '[{"desk_id":3,"card_id":8}]'
```
주의: `--desk-id` 파라미터 없음. `--desk-strategies` JSON 사용. v2 엔진 저장 시 SELL 행에 exit_reason/entry_date/exit_date/hold_days 자동 기록(신규 세션만, 기존 36~38 세션은 NULL).

**V2 allocation 정규화 (BT-ALLOC-FIX)**: 사용 desk들의 allocation_pct 합이 100%가 아니면 100%로 정규화하여 initial_capital 전액을 desk_funds에 배정. 로그 `[ALLOC-NORMALIZE]`로 확인.

**V2 자본 안전장치 (CC-BT-CAPSAFE)**: desk_configs/risk_params에서 설정. 미설정 시 기본값 사용.
- `max_concurrent_positions`: DESK별 동시 보유 포지션 상한 (기본 10)
- `max_capital_usage_pct`: DESK 자본 사용률 상한 % (기본 80)
- `max_single_position_pct`: 단일 포지션 최대 비중 % (초기자본 기준, 기본 10)
- `max_daily_entries`: 일일 최대 신규 진입 수 (기본 20). 초과 시 "SKIP BUY" 로그.

## GO100 컨텍스트
전략 카드 생애주기: `IDEA → DRAFT → BACKTESTED → PAPER_LIVE → LIVE → PAUSED → RETIRED`
source_type: `SYSTEM / CUSTOM / LLM / SHARED`

코드 구조:
- `backend/app/services/go100/`: universe/ strategy/ portfolio/ backtest/ ai/ **paper_trading/** **risk/** **live_trading/** **scheduler/** **optimizer/**
- `backend/app/routers/go100/`: strategy_router, portfolio_router, backtest_router, ai_router, **paper_trading_router**, **risk_router**, **live_trading_router**, **scheduler_router**, **optimizer_router**
- `frontend/src/go100/`: types/ api/ hooks/
- `backend/tests/`: test_go100_*.py + test_universe_engine_unit.py (총 141건 mock)

API 엔드포인트 (`/api/go100/`):
- `strategy-cards`: POST/GET CRUD, POST `/{id}/transition`
- `store`: GET/POST, POST `/subscribe`
- `portfolios`: POST/GET, GET `/{id}/positions`, GET `/{id}/summary`
- `backtest`: POST `/run`, GET `/{run_id}`, GET 목록
- `ai`: POST `/chat`, `/evaluate`, `/optimize`, `/understand`, `/design`
- `paper-trading`: POST `/start`, GET `/`, GET `/{id}`, POST `/{id}/pause|resume|stop|run-now`, GET `/{id}/positions|trades|snapshots`
- `risk`: GET `/defaults/{level}`, GET `/effective`, POST `/disclaimer`, GET `/disclaimers`
- `live-trading`: POST `/start`, GET `/`, GET `/{id}`, POST `/{id}/pause|resume|stop|run-now|reconcile`
- `scheduler`: POST `/run-live|run-paper|reconcile`, GET `/status`
- `optimizer`: POST `/fit-analysis`, GET `/fit-analysis/{card_id}`, POST `/exit-optimize`, POST `/desk-allocation`, GET `/desk-allocation/{id}`

V4.1 인프라 재사용(읽기전용): LLMGateway(싱글톤), V4OrderExecutor(Phase8), BrokerFactory, AccountSyncManager
인증: `get_current_user` (JWT Bearer, `backend.app.core.security_middleware`)
DB세션: `get_db` (AsyncSessionLocal, `backend.app.core.database`)

## 서버 구성
| 서버 | IP | 역할 | 상태 |
|------|----|------|------|
| **211서버** (현행) | 211.188.51.113 | V4.1 자동매매 + GO100 | 운영 중 |
| **68서버** (정리 예정) | 68.183.183.11 | 구 트레이딩 (CentOS 7) | KIS API 403, 통폐합 보류 |

68서버 통폐합 시 필요: ① .env 키 동기화 → ② trading.newtalk.kr SSL 발급 → ③ DNS 변경 → ④ 68서버 서비스 중단
DO Spaces: newtalk1(SGP1, 17.5GB) + newtalk(NYC3, 1.4TB) — 이미지 CDN, 유지 필요

## 최근 완료 작업 이력
| ID | 내용 | 커밋 |
|----|------|------|
| BT-TRADE-DETAIL | BT-TUNE 세션(58/60/61) 개별 거래 상세 분석. TOP/WORST 거래, 카드별·종목별·DESK별·요일별·보유일수별 분석, 멀티카드 진입 리스크 분석 | (본 커밋) |
| GO100-BUNDLE4D | 종목×전략 적합도 매트릭스+청산 최적화+멀티 데스크 배분 (fit_engine+optimizer_service+5 API, 141 tests) | (본 커밋) |
| STRAT-TUNE | 손실/0건 카드 22개 비활성화, DESK2 trailing_stop+hold 추가, risk_params 키 통일, BT 검증(21.01%) | (본 커밋) |
| STRAT-DETAIL | 전략 카드 58개 진입/청산 조건 전수 조사. entry_rules/exit_rules/risk_params 전문 분석, 수익vs손실 카드 비교, 엔진 평가 방식 분석, 5개 최적화 권고 | (본 커밋) |
| GO100-BUNDLE4C | 오케스트레이터 분봉 백테스트 우선+일봉 폴백. AdvancedFilters+MinuteSimulator+분할익절 통합. Cards 13~15(스캘핑/데일리/스윙) 생성 (129 tests) | (본 커밋) |
| GO100-BUNDLE4B-FIX | 오케스트레이터 전체 루프 수정: user_id 전달, LLM 응답 타입 검증, asyncpg 날짜 변환, 고속 인메모리 백테스트. Cards 10-12 생성·검증 (129 tests) | 05a0f773 |
| BT-OPTIMIZE | 전 데스크 카드 조합 백테스트(세션47~57), 최적 32카드 선별, 3M/6M/1Y 검증, DESK별·카드별·exit_reason별 성과 분석 | (본 커밋) |
| CARD-BUY | run_card_pipeline에 v4_signals 기반 매수 로직 추가. generate_daily_signals 1회 호출 + 카드별 시그널 매칭 + 안전장치 6종 | 3a71052a |
| STRAT-AUDIT | 전략 카드 59개 전수 분석, 백테스트 세션/카드/exit_reason/종목별 성과, 실매매 현황·엔진 구조·분봉 연동 평가. 읽기 전용, 변경 없음 | (본 커밋) |
| FUND-DOTENV | fundamental_collector.py에 load_dotenv() 추가, CLI 단독 실행 시 .env 자동 로드, 실행 테스트 성공 | (본 커밋) |
| GO100-BUNDLE4B | Advanced 12필터 + 분봉백테스트엔진 + 분할익절 시뮬레이터 + 3 CEO전략(스캘핑/데일리/스윙) + Paper Trading 시작 (129 tests) | ab44d85a |
| GO100-BUNDLE4A | V4.1 DB 전수조사 (156테이블, 컬럼품질, 데이터범위, stock_universe.market_cap=ALL NULL 발견) | (보고서만) |
| HIST-VERIFY | HIST-COLLECT 데이터 검증: ohlcv_daily 2023-01~2026-02 2,596,548행, v4_ohlcv_minute 9,997,087행, index_daily OHLC=0 150건, DB 3,779MB | 없음 |
| FUND-CHECK | fundamental_collector KIS API 설정 상태 확인. 결과: kis_configs 기반 동작, CLI 실행 시 .env 미로드로 Fernet/DB 실패 → 보고만 | 없음 |
| BT-ALLOC-FIX | desk allocation_pct 100% 정규화, total_asset 정확도 확보 (세션45·46 검증) | (본 커밋) |
| IDX-DROP | 레거시 ohlcv_1m·ohlcv_1m_history·ohlcv_1m_old·market_data_min DROP(636MB 절감). 분봉 파티션 중복 인덱스는 부모 인덱스 종속으로 DROP 미실행 | (본 커밋) |
| HIST-COLLECT | 분봉/일봉/업종/VKOSPI/시장투자자 과거 데이터 최대 수집, collect_minute_historical 버그 2건 수정, 신규 스크립트 2개 추가 | (본 커밋) |
| SYS-STABILIZE | /tmp 정리(32GB→1.3MB), _legacy_ 3테이블 DROP(3.2GB), Swap 8GB 구성, bs4 설치 | fb9e3593 |
| SVR68-CLEANUP | 68서버 백업+기능비교, next build hang kill, top100 bs4 에러 식별 | (본 커밋) |
| DB-CAPACITY | DB 용량 분석, 레거시 DROP 계획, 3년 예측 보고서 | (본 커밋) |
| DESK2-MINUTE-BT | 백테스트 엔진 분봉 모드: --timeframe minute, MinuteDataLoader/IndicatorCalculator/ConditionEvaluator, DESK2·3 minute_entry/exit | (본 커밋) |
| SVC-RESOLVE | kis-v41-api 8003 이동·go100 8002 유지, nginx 수정, webapp 유닛 없음, 분봉 인덱스 중복 조사 | (본 커밋) |
| GO100-BUNDLE3-FIX | systemd 4-timer 등록(live/reconcile/paper/report), AI Chat E2E 3건, KIS 모의계좌 E2E(paper+live dry_run+reconcile+pause), fetch_balance→get_balance 수정, get_status pos.id 수정 (98 tests) | (본 커밋) |
| GO100-BUNDLE3 | 포지션사이징 체계+면책동의 + Phase8 실거래엔진 + 스케줄러 (98 tests) | 097c82d0 |
| GO100-PHASE7 | Paper Trading 엔진/스케줄러/서비스/라우터 (10 endpoints, 74 tests) | (본 커밋) |
| GO100-PHASE6 | EVALUATE+OPTIMIZE 에이전트 + 전체 오케스트레이션 루프 (61 tests) | 5cbf21f0 |
| BT-CAPSAFE | 세션38 첫날 폭락 원인 분석 + 자본 안전장치 4종(max_concurrent/capital_usage/single_position/daily_entries) | (본 커밋) |
| BT-ENHANCE | v4_backtest_trades에 exit_reason/entry_date/exit_date/hold_days 추가 + engine v2 저장 로직 | (본 커밋) |
| GO100-PHASE5 | 백억이 AI UNDERSTAND+DESIGN 에이전트 + 12 unit tests | d7206f1b |
| SECIND-V2 | 업종 대/중/소분류 병행 수집 | c7f77110 |
| DESK3BT | DESK3 세션38 실행 (351건, -54.80%) | — |
| SECIND | 산업 업종 수집 CTPF1002R | 1cdb99ad |
| MKTINV | market_investor 스크립트+크론 | 8a187bf2 |
| BTREADY | card_id 컬럼 + DESK3 준비 | — |
| IDXFIX | index OHLC 파싱 수정 | — |
| PIPEFIX2 | universe 토큰 403 해결 | — |
| PIPEFIX1 | 일봉 DB 비밀번호 + index 크론 | ceabc344 |
| LOGFIX | 백테스트 엔진 로깅 16포인트 추가 | 42432c32 |
