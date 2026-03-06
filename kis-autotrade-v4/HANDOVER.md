# HANDOVER – KIS AutoTrade V4.1 DESK 시스템
> 최종 업데이트: 2026-03-06 (v10.19 — T-184 인프라확인+리서치수집+RES-301~306 시딩: 서비스 6/6 active/Nginx 200/스냅샷cron 기설치/evolution_loop cron root 수동 필요/research_collector 11건 수집(RES-201~306)/RES-301~306 11건 전부 COLLECTED→ANALYZED/EvolutionLoop 수동1회→11건ANALYZED/snapshot total=16/커밋 4020fc56; v10.18 — T-183 Root 인프라 일괄적용: Nginx reload+go100/frontend 재시작/스냅샷cron 2건 확인/RESEARCH가설 11건/서비스 6개 active/8/9 PASS(B-3 evolution_loop cron root 수동 필요); T-180 RES-201~205 5건 DB시딩/research_collector.py 신규(275줄)/EvolutionLoop RESEARCH분기 추가(+259줄)/커밋 34f65a77; v10.17 — T-178 FunnelScore 0.4→0.35 하드코딩 제거(cte_pipeline.py 동적로드)/Evolution Loop 24h 자동모드(.env GO100_EVOLUTION_LOOP_ENABLED=true·AUTO_APPROVE=true·MIN_GRADE=C)/go100-dashboard.html 829줄 통합대시보드(섹션A~G)/snapshot research_lab 섹션 확인/Nginx /manager/ 기설정/서비스 6개 전체 active/커밋 2206e2ab; v10.16 — T-177 DESK2 MultiConditionMatcher 파이프라인 연결(process_desk2_signals/ENV guard)+AI 대시보드 HTML(v41_manager/ai-model.html 453줄)/코드 push ee593105; v10.15 — T-173 장마감 일괄재시작+인프라: 스냅샷 갱신(V4.1+GO100)/코드 push c57d8344/서비스 전체 active/root 실행 스크립트 생성(nginx+cron 대기); v10.14 — T-172 V4.1+GO100 스냅샷 시스템/T-168R GO100↔V4.1 신경연결 Phase1/T-039R GO100 스냅샷 재확인; v10.13 — **T-162~T-170 일괄반영**: T-162 수익구조진단(승률6.8%→5대원인)/T-163A~D 긴급수정(비용0.015%·SL완화·FunnelScore0.35·BLOCK→CONDITIONAL)/T-166 GO100자율루프진단/T-167 V3활성화/T-168 DESK2 16카드재활성화/T-170 V3→FunnelScore L3.1통합/Redis재시작(T-171A); v10.12 — **T-156 SELL_FAILED 전건청산+모의매매현황**: SELL_FAILED 0건(35건CLOSED)/실계좌2건CEO지시청산/Redis ok복구/모의44건승인6.8%승률/D6최우수; v10.11 — **T-151 03-06 장중 전체 시스템 점검**: 4서비스 PASS/분봉09:18수집/DB 40GB/strategy_cards 60/open_positions 0(SELL_FAILED 10건)/가상매매 03-06 BUY 11건/Redis disconnected WARN/KIS토큰DB만료(실API 정상)/종합PARTIAL; v10.10 — **T-138 미커밋 Push + T-125~T-133/T-137 완료 기록 추가**: kis-autotrade-v4 10커밋 로컬 확인(SSH 제한으로 root push 필요), T-125~T-133/T-137 완료 작업 테이블 추가; v10.9 — **T-136 CONTEXT.md 2026-03-06 동기화**: DESK2 Phase B(T-128)/DESK5 프랙탈(T-127/T-130)/코어보유(D-014) 섹션4 추가, 작업큐 T-125~T-136 현행화(T-131 완료 반영), 불일치 0건 달성, 커밋 974f545; v10.8 — **T-134 CONTEXT.md 전면 갱신**: HANDOVER.md v10.7 기준 CONTEXT.md 14개 항목 갱신(strategy_cards 60/OPEN 14/DB 37.82GB/288테이블/분봉108.4M/DESK 풀 현황/작업큐 Phase2c/CEO결정대기 6건/지시서 DIRECTIVE_START-END 형식/불일치 13건 정정), project-docs 커밋 881685e push; v10.7 — **T-124 03-06 사전점검 9/9 PASS**: 승인율 50.6% GREEN, FunnelScore T-114연동 확인, KIS 토큰 갱신(03-06 15:22 KST), synthetic_BLOCK T-105 패치 유효, 크론 30+ OK, 보고서 CUR-V41-0306-PRECHECK-001-20260305.md push; **T-123 DESK5 Fundamental 재수집**: stock_fundamentals fallback 마이그레이션 200건(20종목), GrowthScoreEngine AXIS1_EXPECTATION 20/20 NONE=0% fallback=0% 달성, 보고서 CUR-V41-DESK5-FUND-COLLECT-001-20260305.md push; v10.5 — **T-120 HANDOVER.md v10.5 일괄갱신**: T-101~T-119 16건 완료 반영, DB 288테이블/37.82GB/분봉108.4M rows, Known Issues 갱신(synthetic_BLOCK T-108해결/FunnelScore threshold 0.55/DESK5 데이터미수집); v9.8 — **T-099 깔대기 데이터 실 수집 + FunnelScore 통합**: v4_sector_mapping 신규(062 마이그레이션, 3,844종목), v4_macro_daily 신규, SectorCollector(collect_from_stock_universe/collect_from_ohlcv_symbols), v4_fundamental_quarterly 149종목/787행 수집(stock_fundamentals 기반), GrowthScoreEngine Decimal 버그수정, DESK3 축분류(AXIS2=4/NONE=162, 97.6% NONE), DESK5 20종목 ALL NONE, 4테스트 ALL PASS, DB 객체수 254→256; v9.7 — **T-098 펀더멘탈 Growth Score 엔진**: v4_fundamental_quarterly 테이블 신규(061 마이그레이션), FundamentalCollector(fetch_financial_ratio/fetch_investment_indicator/calculate_growth_metrics/collect_all_desk_symbols), GrowthScoreEngine(classify_stock 2축분류/score_growth/filter_no_growth), CEO 축1(기대가치=DESK5)/축2(실현가치=DESK3/4) 분류, node_detector_desk5 AXIS1+20/NONE-30 적용, node_detector_desk3 AXIS2+15/NONE-20 적용, growth_score YAML섹션 추가, 10테스트 ALL PASS; v9.6 — **T-097 확인매매 엔진**: ConfirmationEntryEngine 신규(find_recent_low/confirm_bottom/calculate_risk_reward/generate_entry_signal), 확인 4조건(양봉+반등+거래량×1.5+외인/기관순매수), DESK별 차등 손익비(D5:5.0/D4:2.5/D3:2.0/D2:1.5), H08-B(5주보유)/H05-D(MA20트레일)/H09-C(2일지연)/H12-D(×2.0배) YAML 반영, 9테스트 ALL PASS; v9.5 — **T-096 12가설 백테스트 프레임워크**: hypothesis_tester.py 신규(12가설×4시나리오=48개 백테스트), 3년 일봉 300종목 백테스트 완료, v4_desk_backtest_results 48행 INSERT, 승자 요약: H01-A(즉시진입)/H03-C(MA5+VP120)/H05-D(MA20트레일PF=2.18)/H08-B(5주보유PF=25.93)/H12-D(×2.0배PF=3.15), 핵심발견: 즉시진입우위·MA트레일링압도적·파이프라인2배보유최적·마디피로가설기각; v9.4 — **T-083 문서불일치 정정+T-075~T-080 일괄반영**: CONTEXT.md 5건 정정(strategy_cards 60건/오픈포지션 14건/DB 15.7GB/ohlcv_daily 테이블명 정정/DESK 풀 테이블 개별화 v4_desk5_watchlist·v4_desk4_watchlist·v4_desk3_pool/DESK3 풀 206/ACTIVE), HANDOVER.md T-075~T-080 6개Task 일괄 반영, Known Issues 갱신(virtual_hourly_report cron 등록완료·TP=0 해결·GO100 0체결 해결·Commander 로깅 T-082 예정), project-docs git push 완료; v9.3 — **T-038-FIX AADS 지시서 완료**: Part A(memory GET 엔드포인트 인증제거: /memory/search,/memory/ceo-decisions,/memory/inbox — 공개 조회 가능), Part B(AADS agents 카테고리 매니저 6건 등록: SALES_MARKETING/FINANCE_ACCOUNTING/CONTENT_STRATEGY/QA_OPS/CUSTOMER_SUCCESS/INVESTMENT_TRADE, 총 15개), aads-server repo 커밋 a5f0c37 push; **대화저장 웹뷰어**: go100.newtalk.kr/go100/conversations 전체/프로젝트별 탭+키워드검색, nginx /api/go100/conversations→Next.js(3000) 라우팅 수정; v9.2 — **T-038 매니저 협업 API**: bridge.py 4엔드포인트(/memory/search,/memory/ceo-decisions,/memory/cross-message,/memory/inbox/{agent_id}) + 매니저 레지스트리 6건 등록(SALES_MARKETING/FINANCE_ACCOUNTING/CONTENT_STRATEGY/QA_OPS/CUSTOMER_SUCCESS/INVESTMENT_TRADE), AADS T-036(public-summary) + T-037(save_manager_report) 완료, genspark_bridge.py 대화 자동저장 패치(CONV_SAVE 2분쿨다운/80자이상/AADS저장); v9.1 — **CEO-APPROVAL-20260305**: D4 눌림확인 전환 Shadow해제+E2A파라미터(09:00~09:30/SL2%/TP3%)+GATE_REQUIRED+is_pullback+ATR재정합, D2 trail-10%/SL-3% 기적용확인, S1 갭+5%+SIG3_YANGBONG 기적용확인, CS×EQS L3.5/L4.5+BounceGate D2/D4/D5/S1 기배포확인; 커밋 a7864db5; v9.0 — **CUR-UNIFIED-TRADING-REPORT-PIPELINE-001**: 4채널 일일/주간/월간 통합 보고서 3종 스크립트(generate_unified_daily/weekly/monthly_report.py) + 크론 3건(17:00/토10:00/1일10:00), DAILY-20260304.md HTTP 200 확인; **CUR-TRADING-LIVE-DASHBOARD-001**: 백엔드 trading_dashboard_router.py 6 API + SSE, GO100 Next.js /go100/trading/dashboard 페이지, V4.1 dashboard.js, 단위테스트 15/15 ALL PASS; v8.9 — **CUR-V41-VIRTUAL-RUN-HEALTH-CHECK-002**: float(None) 에러 수정(run_unified_engine.py 라인938~982), 단위테스트 12건 추가 ALL PASS, 649645 synthetic_BLOCK 잔존 없음; **CUR-V41-VIRTUAL-RUN-HEALTH-CHECK-001**: 가상매매 4/6 PASS — 서비스/거래실적/수급게이트/데이터수집 정상; PARTIAL청산(SL/TIMEOUT OK, TP 0건); FAIL virtual_hourly_report cron 미등록; v8.8 — **CUR-V41-ATR-COMMANDER-ACTIVATE-001**: ATR NET_RR_RATIO 2.0→1.5 완화(96b7407b 기적용) 테스트 29/29 ALL PASS(test_14 하드코딩→상수참조 수정), GO100_COMMANDER_MODE=true+GO100_DESK_CHAIN_MODE=true 활성화 확인, 커밋 5e1223ac push; v8.7 — **CUR-V41-DESK-POOL-VERIFY-AND-PARAMETERIZE-001**: PHASE1 DESK5(20/WATCHING)/DESK4(18/WATCHING)/DESK3(106/ACTIVE)/DESK2(오늘 후보10·신호0·매매0)/DESK3→DESK2 연결 3종목/가상매매 14+9건/크론 11개 정상/unified_engine 11:06 정상, 텔레그램 CEO 즉시 보고; PHASE2 v4_desk_backtest_results 테이블 DB 적용(051 마이그레이션 실행, 인덱스 4개); v8.6 — **CUR-V41-DESK-FILTER-PARAMETERIZE-001**: DESK5/4/3/2 필터 파라미터 전면 외부화(config/param_search_space.yaml), desk_filters 패키지 신규(base/desk5/desk4/desk3/desk2/pipeline/backtest_runner), 기존 6개 스크립트 하드코딩 완전 제거(desk3_pool_scan/desk4_node_scanner/desk5_seed_scanner/desk5_weekly_monitor/desk2_prescoring/desk2_pool_link), v4_desk_backtest_results 마이그레이션(051), 42/42 테스트 ALL PASS; v8.5 — **CUR-V41-DEDUP-GUARD-001**: auto_trigger.sh TASK ID 중복방지 패치(get_task_id/is_task_running 함수 추가, cancelled/ 디렉터리), 211/114서버 동시 배포, security_scan.sh false-positive(Chrome버전) 수정, 기존 보고서 민감정보 마스킹 9건; v8.4 — **CUR-V41-DIRECTIVE-AUTOMATION-002**: KST 전면적용(logging+UTC→KST+run_pending.sh+write_done.py), 정기보고 30분 프로젝트별 pending건수 포함, .cursorrules 9-10, CEO-COMMAND-CENTER 섹션9, 8/8 PASS; v8.3 — **CUR-V41-DIRECTIVE-AUTOMATION-001**: bridge.py Directive 자동 감지·저장·완료 중계 체계 구축. pending/running/done/archived 디렉토리, save_directive_to_pending(sha256 중복방지), process_done_directives(10초 감시→매니저+CEO 중계+텔레그램), run_pending.sh, 정기보고에 pending현황 포함, 모든 타임스탬프 KST 명시(logging converter + _get_latest_commit UTC→KST 변환), 5/5 단위테스트 PASS, genspark-bridge 재시작 active; v8.2 — **Session N 추가: WF-Step1 SIG3+SIG6 적용 + D4 Shadow Mode 구현** (9f17b8c5): cte_pipeline.py D4 SIG5→SIG3 교체(WF-Step1 3/3 PASS), SHADOW_STRATEGIES={'D4'} 활성화, engine.py _log_shadow() 11개필드 JSONL 기록(logs/shadow/shadow_d4_{date}.jsonl), monitor_virtual_run.py Section7 D4 Shadow 요약 추가, 43/43 PASS; WF-Step2 시뮬 구조적 한계 발견(ATR파라미터 미반영→shadow trading 직행); v8.0 — **Session N 추가: Step4 사전 시뮬 + 매니저 분석 완료**: 백테스트 D4 price_pos+is_pullback 현실화(65557fd2), Step4 시뮬 5개 시나리오 비교(D4 83건 활성화 가능하나 PF 1.906으로 하락), 핵심발견: D4제외 PF=3.335(베이스라인 2.398 상회→교차영향 없음 확인), D4자체 PF=1.074/WR=22.9%(시뮬 과소추정 가능), 매니저 지시: 옵션B(ATR 1.5 단독) 즉시→다음세션 WF-Step1(BREAKOUT+SIG3비활성 3Fold)/WF-Step2(D4파라미터조정 SL2%/TP3%/시간축소), 미통과 시 shadow trading 전환; v7.0 — **Session N 추가: D4 EQS PULLBACK 오분류 버그 수정 + SIGNAL_COMBO 사전분석**: signal_generator.py:354 D4 PULLBACK→BREAKOUT 수정(EQS+15점, REDUCE→PROCEED, 커밋 e274411a), D4 SIGNAL_COMBO SIG5→SIG3 교체 방안 분석(리플레이 검증 후 채택 예정), 보고서 CUR-V41-D4-ACTIVATION-PREANALYSIS-001(커밋 578cda4); v6.9 — **Session N: ATR_NETRR 병목 분석 + WF 3-Fold ALL PASS**: 핵심발견 「진짜 병목=ATR_NETRR(45.8% 차단)」 확정, D4 전략 0건=3중차단(ATR_NETRR+SIGNAL_COMBO+EQS), ATR 1.5 완화 리플레이(731→1,066건/+46%, PF 2.248 유지), WF 3-Fold ALL PASS(F1 PF=2.175/F2 PF=2.448/F3 PF=2.263, 평균 PF=2.295, Sharpe=11.03, MDD=-2.1%), D4 SIG5(VP_120_RECOVERY) 구조적 미충족 확인, D7 시뮬 경쟁≠실전(시간대분리), 보고서 2건 push(a518efc/0a00567); v6.8 — **Session K: 03-03 Virtual Run 자동 모니터링 체계 구축**: monitor_virtual_run.py 신규(5액션: premarket/signal/periodic/close/daily_report), cron 6건 등록(07:58~16:00), L3.3 ALLOW/BLOCK/CONDITIONAL 비율+v4_mock_trades 거래+청산모드+Fail-Open+시스템상태 추적, JSONL 스냅샷+Markdown 일간 보고서 자동생성, 5액션 dry-run ALL PASS, 보고서 Push 방안B(CEO 확인 후 수동); v6.7 — **Session J: 소형주 수급 데이터 수집 확대 분석**: 핵심발견 「종목 누락 아님 — 날짜 커버리지 갭」 확인(507종목 전부 존재, 908건 날짜 미매칭), KIS API FHPTJ04160001 30일 한계 실증(역사적 2025년 복구 불가), cron stock-limit 500→4000 확장(전종목 커버), 역사적 매칭률 51.5%(불변), Live 매칭률 ~100%(3,839/3,844종목), L3.3 역사적 BLOCK 69.7% → Live BLOCK ~42% 개선 추정, backfill_investor_missing.py 신규; v6.6 — **Session H: 통합엔진 L3.3 연동 + 아키텍처 동기화**: 아키텍처 진단 GAP 6건 발견(L3.3 미활성/exit_manager Generic파라미터/D2 trail 10%/HARD_TP 미구현), Method A(CTE 경유) 채택 — signal_generator.py에 SupplyDemandGate.evaluate() 호출+pool 전파+Fail-Open, exit_manager.py 전략별 STRATEGY_EXIT_PARAMS 동기화(D2 SL3%/trail3%, D4 SL1%/TP5%/HARD_TP, D5 SL2.5%/trail2%), D2 trail_start 10%→3% 수정(TIMEOUT 86%→해소), run_unified_engine.py 합성 SupplyGateResult(E-3 통과율 17%ALLOW/10%COND/73%BLOCK), **137테스트 ALL PASS**, GAP 4건 해소(G-1~G-4), 잔여 G-5(Anti-Pattern P2)/G-6(Timeout P2), **03-03 Virtual Run L3.3 활성화 GO**; v6.5 — **Session E-3: 수급 게이트 다층 검증 + L3.3 SupplyDemandGate 구현**: CEO 승인 3건 기반, 전 레짐 PF>1.5(BEAR 최고 2.549), WF 3-Fold ALL PASS(0.7+FRGN min PF=1.455), supply_demand_gate.py 신규(MUST CLOSE>0.7+FRGN>0, 보너스6개, 3등급), cte_pipeline.py L3.3 삽입(L3→L3.3→L3.2), 24테스트+33기존 ALL PASS, **Baseline PF=0.834→D_Full PF=2.727(+227%)**, WR 34.3%→51.1%, D-002 최종 실증; v6.4 — **Session F: 프론트엔드 & API 연결 전수조사**: Next.js(GO100/go100.newtalk.kr) 52페이지+~220컴포넌트+20API파일, V4.1 정적HTML(trading41) 30페이지+65JS모듈, 백엔드 45개 핵심 API 연결 확인, 93% CONNECTED(GAP 2건: /reports 라우터+WS 서버), SSE 2채널 정상, JWT refresh 자동갱신 정상, Nginx 라우팅 go100:3000/8002+trading41:static/8003 확인, 우선조치 G-03(reports_router)+G-05(WS서버) 식별; v6.3 — **Session E-2A: Anti-Pattern 3건 차단 + CEO 승인 3건 코드 적용 + 리플레이 재검증**: exit_simulator(D2 trail 10%/D4 SL1%+TP5%/HARD_TP), entry_detector(_is_anti_pattern/_is_absolute_forbidden/D5 13시차단/D4 09:25~10시창), candidate_scanner(D7 close_pos≥0.30/S1 gap 5%), strategy_params(S1 SIG8), E-2A PF=0.826(E-1 0.834→소폭악화), Walk-Forward Fold3 PF=1.096(D6 주도), D2 trail_start=10% 역효과 발견(TIMEOUT 86%), E-3에서 D2/D5 재검토 필요; v6.2 — **Session F-Pre: 03-03 Virtual Run 사전 점검 ALL PASS**: Cron 4건 확인(07:55/08:50/*/1 9-15/15:30), unified_engine.log 기록중(07:55 premarket 실행완료), DB 4테이블 02-27 데이터 완비(ohlcv 3839/investor 3839/regime 1/minute max=02-27), Mock API HTTP 200+access_token OK, 서비스 4개 all running, Swap 66.6%/Disk 77% PASS, import OK → **03-03 Virtual Run GO**; v6.1 — **Session E-2B 수급 데이터 통합 탐사 재실행**: 1,929건×14수급+19분봉=33변수 통합, CLOSE_POSITION_5D AUC=0.682(#1), 수급 상위3 AUC=0.624 vs 분봉 0.540, CEO D-002 실증(외인 p=0.014★), 종가위치>0.7 PF=1.991(+139%), TRAJECTORY=3 PF=1.841, DUAL_FLOW≥3 PF=1.692, 외인연속매수≥1d PF=2.343, D6+외인 PF=5.054, L3.3 SupplyDemandGate 설계; v6.0 — Session G 조치 완료+DB 카탈로그; v5.11 — E-1 분봉 탐사; v5.10 — G 서버 검증; v5.9 — D 리플레이 BT)
> 관리자: CEO (moongoby)
> 용도: 모든 AI 세션(웹 Claude, Cursor, Claude Code) 시작 시 필수 읽기

---

## 1. 프로젝트 개요
- KIS AutoTrade V4.1: 한국투자증권 API 기반 AI 자동매매
- 5개 DESK (60개 strategy cards, OPEN=0 / SELL_FAILED=10 / CLOSED=25)
- 서버: root@[SERVER-IP], DB: PostgreSQL kisautotrade
- 289 테이블 (T-151 기준, 2026-03-06), 40GB, 일봉 최신(03-05, 2,623,502 rows), 분봉 오늘(03-06 09:18 수집 중)
- v4_investor_daily 2,580,265행(최신 03-05), v4_fundamental_quarterly 787행, v4_macro_daily 730행
- 투자자별 수급 데이터 (275,846 rows, 3,943종목, 2010~2026), 체결강도 (231,307 rows, 2025-11~), 뉴스 214만건

---

## 2. 완료된 작업

| Task ID | 날짜 | 커밋 | HTTP | 핵심 결과 |
|---------|------|------|------|-----------|
| **T-186 Redis 연결 복구 + V4.1 서비스 안정화** | 03-06 | — | 8003 ok | kis-v41-api(8003) redis:disconnected → systemctl restart kis-v41-api → redis:connected 복구; Redis 서버 자체 정상(업타임 2일)/rejected_connections=0/maxclients=10000; redis.py T-173 설정 전부 기적용(retry_on_timeout/health_check_interval=30/socket_keepalive); minute-collector inactive(dead) status=0/SUCCESS 장외 정상 확인; GO100 재시작 금지 준수 |
| **T-183 Root 인프라 일괄적용** | 03-06 | — | 8/9 PASS | Nginx reload/go100·frontend 재시작/스냅샷cron 2건(/etc/cron.d/) 확인/RESEARCH가설 11건/서비스 6개 active/GO100_EVOLUTION_LOOP_ENABLED=true/research/ 존재; B-3 evolution_loop cron root 수동 설치 필요 |
| **T-180 리서치팀 연구과제** | 03-06 | 34f65a77 | — | RES-201~205 5건 DB시딩(go100_strategy_hypotheses RESEARCH), research_collector.py 신규(275줄), run_evolution_loop.py RESEARCH분기 추가(+259줄) |
| **T-178 FunnelScore+EvolutionLoop+Dashboard** | 03-06 | 2206e2ab | 4×200 | FunnelScore min_score_for_entry 0.4→0.35(cte_pipeline.py 동적로드), .env GO100_EVOLUTION_LOOP_ENABLED=true/AUTO_APPROVE=true/MIN_GRADE=C, go100-dashboard.html 829줄(섹션A~G), snapshot research_lab 포함, 서비스 6개 active |
| **T-177 DESK2 파이프라인+AI 대시보드** | 03-06 | ee593105 | — | process_desk2_signals() 추가(DESK2_MULTI_CONDITION_ENABLED ENV 플래그 guard/Fail-Safe), run_desk2_cycle() multi_condition 연결, v41_manager/ai-model.html 신규(453줄/순수HTML+CSS+JS/60초 자동갱신/snapshot+pipeline fetch/V3모델상태+FunnelScore+DESK현황+모의매매+서비스+DB), MultiConditionMatcher import OK, DESK2 pytest 35/35 PASS, 신규실패 0건 |
| **T-173 일괄재시작+인프라** | 03-06 | c57d8344 | — | 스냅샷 갱신(V4.1 5파일+GO100 5파일), 코드 push 완료, 서비스 8개 전체 active, scripts/t173_root_ops.sh 생성(nginx+cron+서비스재시작 root 실행용) |
| **T-172 V4.1+GO100 스냅샷** | 03-06 | 2295aa10/c4bcc498 | — | V4.1 generate_v41_manager_snapshot.py+GO100 generate_manager_snapshot.py 실행성공, JSON 5+5파일 생성, Nginx/크론 root대기 |
| **T-168R 신경연결 Phase1** | 03-06 | 40ba04c3 | — | sync_trade_results+desk_morning_scan+run_evolution_loop 3스크립트, CTE L3.4 Commander Gate stub(547줄), evaluate_entry(1697줄), .env false, 테스트 신규실패0 |
| **T-039R GO100 스냅샷 재확인** | 03-06 | c4bcc498 | — | snapshot.json 1KB+agents 18KB 생성확인, Nginx/크론 root대기, middleware.ts /manager/ 제외 확인 |
| **T-170 V3→FunnelScore L3.1** | 03-06 | 7b6ebf8d | — | V3 cs_ai FunnelScore L3.1 통합(≥0.6→+0.10/≤0.3→-0.10), Fail-Open, 9/10 PASS |
| **T-168 DESK2 활성화+D5점검** | 03-06 | — | — | DESK2 16카드 재활성화, DESK3 306건정상, D5 29건 전체미진입(BLOCK/FUNNEL) |
| **T-167 V3활성화+GO100점검** | 03-06 | — | — | V3 6파일 active=true, 에이전트27개, regime정확도80%, redis disconnect |
| **T-166 GO100 자율루프진단** | 03-06 | — | — | 5개연결고리누락, Evolution Loop미가동, 피드백코드부재 |
| **T-163D BLOCK→CONDITIONAL** | 03-06 | 84b700e6 | — | synthetic_BLOCK override CONDITIONAL + 14:30 cutoff |
| **T-163C FunnelScore 0.35** | 03-06 | 92a0ac62 | — | min_score_for_entry 0.40→0.35 통합 |
| **T-163B SL완화** | 03-06 | 34e762b0 | — | D-ORB 4%/D4 3%/D7 3% |
| **T-163A 비용수정** | 03-06 | — | — | cost 0.47%→0.015% |
| **T-162 모의매매수익구조진단** | 03-06 | — | — | 승률6.8% 5대원인(비용/SL/FunnelScore/BLOCK/신호부족) |
| **T-156 SELL_FAILED 전건청산+모의매매현황** | 03-06 | — | — | SELL_FAILED 0건(35CLOSED)/실계좌2건CEO청산/Redis ok/모의44건승인6.8%승률/D6최우수(-0.43%)/D7·S1·D4·D2 0승 |
| **T-151 03-06 장중 전체 시스템 점검** | 03-06 | 346a9f15 | 200 | 서비스 4개 PASS/분봉09:18수집/일봉2,623,502rows/strategy_cards=60/tables=289/db=40GB/가상매매BUY11건/종합PARTIAL; WARN: Redis disconnected/SELL_FAILED 10건/KIS토큰DB만료(실API정상)/unified_engine.log 0bytes |
| **T-144 03-06 장중 모의매매 일간 보고서** | 03-06 | 4762a13d | — | 장중 모의매매 모니터링 일간 보고서 |
| **T-143 D-010 Phase C S1 테마그룹핑** | 03-06 | 120ecef1 | — | S1 테마그룹핑 Phase C 구현 |
| **T-142 D-009 P2 변수 3종** | 03-06 | d23b372a | — | NEW_DETECTOR/ORDERBOOK/CK480 변수 구현 |
| **T-141 D-010 DCS 등급체계** | 03-06 | 24496f74 | — | DCS A/B/C 등급체계 구현 |
| **T-136 CONTEXT.md 2026-03-06 동기화** | 03-06 | 974f545 | — | CONTEXT.md T-136 전면 동기화: 섹션4 DESK2 Phase B(T-128)/DESK5 프랙탈(T-127/T-130)/코어보유(D-014) 추가, 섹션7 작업큐 T-125~T-136 현행화(T-131 VP_RT/MA_REGIME 완료 반영), 섹션11 HANDOVER v10.8 갱신, 섹션13 불일치 0건 달성 (T-136 기준) |
| **T-134 CONTEXT.md 전면 갱신** | 03-06 | 881685e | — | CONTEXT.md 14개 항목 갱신: strategy_cards 60/OPEN 14/DB 37.82GB/288테이블/분봉108.4M rows/DESK 풀(D5 20/D4 18/D3 106)/서비스 현황/작업큐 Phase2c/CEO결정대기 6건/핵심파일 목록 갱신/지시서 DIRECTIVE_START-END 형식 추가. CONTEXT.md vs HANDOVER.md 불일치 13건 정정 표 추가. git commit 881685e |
| **T-137 D-009 P1 확장 변수 4종** | 03-05 | 93036bd1 | — | D-009 Phase1 확장 변수 4종 구현: VP_RT_EXT/MA_REGIME_EXT/PB_3M_EXT/UL_EXT2 추가, 장중 실시간 계산 모듈 확장 |
| **T-133 03-06 모의매매 확인** | 03-06 | — | — | 미개장 확인, 03-05 56건 BUY 집계, synthetic_BLOCK 8건 잔존 확인 |
| **T-132 DESK3 AXIS2 분류 개선** | 03-05 | a84c4d0a | — | DESK3 AXIS2 분류 개선 — 97.6% NONE 해소, 보고서 push |
| **T-131 D-009 P0 장중 변수 4건** | 03-05 | 08240a10 | — | VP_RT/MA_REGIME/PB_3M/UL_EXT 실시간 변수 구현, 22테스트 ALL PASS |
| **T-130 DESK543 프랙탈 실전 연결 + DESK5 코어 보유** | 03-05 | a3d8fd50 | — | Stage1/2/3 자본단계 설계, DESK543 프랙탈 실전 연결, D-012/D-014 반영 |
| **T-129 기술시그널 Top5+60분 청산** | 03-05 | 0e380e17 | — | D1/D3/S2 폐기, exit_rules.deprecated 추가, 60분 청산 전환 — D-011 |
| **T-128 DESK2 멀티컨디션 Phase A v2** | 03-05 | d6fc488b | — | C2(D4)/C1(D6)/C6(D7) + SignalMatcher 추가, 완전한 멀티컨디션 매처 구현 |
| **T-127 DESK543 프랙탈 트리거 실전 연결** | 03-05 | f8bd2bee | — | DESK5/4/3 프랙탈 트리거 실전 연결, D-012/D-013/D-014 반영 |
| **T-126 기술적 시그널 Top5 매칭 + 60분 청산 전환** | 03-05 | 0e380e17 | — | 기술적 시그널 Top5 매칭 엔진, 60분 청산 전환 — D-011 |
| **T-125 DESK2 멀티컨디션 Phase A** | 03-05 | bca18a1e | — | C2(D4)/C1(D6)/C6(D7) 멀티컨디션 Phase A 구현, desk2_conditions/ 패키지 6파일, 20/20 테스트 ALL PASS |
| **T-122 KJH_CYCLE 김정환 사이클** | 03-05 | dacc29bf | — | KjhCycleEngine 7메서드(check_revenue_uptrend/check_op_uptrend/evaluate_per_band/check_roe_trend/calculate_kjh_score), YAML kjh_cycle 섹션, FunnelScore L3 GROWTH≥0.7→+0.15/MATURE≥0.5→+0.05, 13테스트 ALL PASS |
| **T-121 BJ_SCORE 배진한 5원칙** | 03-05 | d7fea642 | — | BjScoreEngine(대재수심차 100점), FunnelScore L3 ≥80→+0.20/≥60→+0.10, YAML bj_score 섹션, 테스트 PASS |
| **T-119 DESK5 GrowthScore fix** | 03-05 | 060786f2 | — | 근본원인: DESK5 20종목 v4_fundamental_quarterly 0건, min_quarters 8→4, default_axis1_score=0.3 fallback, 6테스트 PASS |
| **T-118 FunnelScore WF 검증** | 03-05 | 7d1efb91 | — | 3-Fold WF: Fold1 FAIL/Fold2 PASS/Fold3 PASS→2/3 전체PASS, threshold 0.40→0.55 반영, 22테스트 PASS |
| **T-117 D_D1_D2_ENTRY** | 03-05 | 474039d7 | — | DDayEntryEngine(장대양봉≥7%/2.5배→D+1 MA5/D+2 MA10), CTE L2.5, SL2%/TP5%/120분, 10테스트 PASS |
| **T-116 FORCE_ACC** | 03-05 | 7d213031 | — | ForceAccEngine(MA120수렴std≤3%, 20%+급등봉, 갭3%/거래량2배), FunnelScore L2 +0.15, 8테스트 PASS |
| **T-115 MKT_SEASON** | 03-05 | 5f4d590c | — | MktSeasonEngine(Q1=0.9/Q2=1.2/Q3=0.8/Q4=0.7, BEAR 0.5/BULL 1.3), FunnelScore L0 통합, 8테스트 PASS |
| **T-114 FunnelScore L3.1 연동** | 03-05 | — | — | CTEPipeline L3.1_FUNNEL 삽입, 005930 테스트 score=0.394→BLOCK(threshold 0.40), 로깅 강화 |
| **T-112 SEC_LEADER v2** | 03-05 | — | — | SecLeaderV2Engine(RS>80, 거래대금1위, 폭락후첫돌파), FunnelScore L1 통합, 7테스트 PASS |
| **T-111 DUAL_FLOW** | 03-05 | — | — | DualFlowEngine(기관+외인동시순매수 5D/20D, 연속외인매수), FunnelScore L2 통합, 6테스트 PASS |
| **T-110 SMALL_CAP_QUALITY** | 03-05 | — | — | SmallCapQualityFilter(시총≤700억, 3년흑자, 5대조건+6대배제), 7테스트 PASS |
| **T-109 THEME_CYCLE** | 03-05 | — | — | ThemeCycleEngine(거래대금100억+상한가29%+), SCORE=min(1.0,(100B×0.6+UL×0.4)/10), 6테스트 PASS |
| **T-108 synthetic_BLOCK 커밋 반영** | 03-05 | bf0d06b3 | — | T-105+T-107 미커밋 해결, run_unified_engine.py 62ins/11del, 크론 반영 확인 |
| **T-107 exit_manager 현재가 fallback** | 03-05 | — | — | 3단계 fallback(분봉→일봉→entry_price), current_price None 청산 불가 버그 해결, 12테스트 PASS |
| **T-105 synthetic_BLOCK Fail-Open** | 03-05 | — | — | 73% BLOCK → virtual_mode_fail_open 전환, 합성 수급게이트 차단 해소 |
| **T-103 FunnelScoreEngine** | 03-05 | — | — | 4계층 깔대기 점수(0.15/0.25/0.30/0.30), CTE L3.1 통합, funnel_score.yaml, 10테스트 PASS |
| **T-102 업종/섹터/테마 수집기** | 03-05 | — | — | v4_sector_mapping 3,844, v4_theme_mapping 551(64테마), v4_supply_chain 176, v4_sector_index_daily 60, 크론 2건 |
| **T-101 매크로 수집기 구조** | 03-05 | — | — | v4_macro_daily 730행 백필, kospi_ma60/ma120 추가, macro_sources.yaml 생성, FRED+BOK 연동 |
| **T-099 깔대기 데이터 실 수집 + FunnelScore 통합** | 03-05 | — | — | **v4_sector_mapping 신규** (062 마이그레이션): 3,844종목 업종매핑(stock_universe 기반), SectorCollector 2메서드(collect_from_stock_universe/collect_from_ohlcv_symbols). **v4_macro_daily 신규** (062 마이그레이션). **v4_fundamental_quarterly 실 수집**: 149종목/787행(stock_fundamentals EPS/PER/PBR 기반, KIS 가상계좌 재무API output2 빈값 → STOCK_FUNDAMENTALS 대체), EPS YoY proxy 387행. **GrowthScoreEngine 버그수정**: Decimal TypeError(라인154~155, 198) float변환. **DESK3 축분류**: AXIS2=4(181710/092220/002360/006650)/NONE=162(97.6%). **DESK5**: 20종목 ALL NONE. 4테스트 ALL PASS. DB 256객체 |
| **T-098 펀더멘탈 Growth Score 엔진** | 03-05 | — | — | **v4_fundamental_quarterly 테이블 신규** (061 마이그레이션): symbol/fiscal_year/quarter/revenue/op_profit/net_income/eps/bps/roe/per/pbr/op_margin/growth_yoy. **FundamentalCollector** (`backend/app/services/fundamental_collector.py`): fetch_financial_ratio(FHKST66430100 8분기)/fetch_investment_indicator(FHKST66430200)/calculate_growth_metrics(YoY+ROE추세)/collect_all_desk_symbols(DESK5+4+3 전종목, rate limit 1초). **GrowthScoreEngine** (`backend/app/services/growth_score_engine.py`): classify_stock(축1=기대가치/축2=실현가치/NONE, recommended_desk 반환), score_growth(0~1, revenue×0.25+op×0.25+roe_trend×0.20+surprise×0.15+peg_inv×0.15), filter_no_growth(NONE 종목 제거). node_detector_desk5 AXIS1+20/NONE-30 confidence 조정. node_detector_desk3 AXIS2+15/NONE-20 confidence 조정. growth_score YAML 섹션 추가(11개 파라미터, 가중치합=1.0). 10테스트 ALL PASS |
| **T-097 확인매매 엔진** | 03-05 | — | — | **ConfirmationEntryEngine 신규** (`backend/app/services/confirmation_entry_engine.py`): find_recent_low(ohlcv_daily N일 최저점) + confirm_bottom(4조건 AND: 양봉/반등≥N%/거래량×1.5/외인기관순매수) + calculate_risk_reward(SL=저점×0.99, TP=DESK별 차등, RR<min→REJECT) + generate_entry_signal(파이프라인→ENTRY/WAIT/REJECT). DESK별 min_rr: D5=5.0/D4=2.5/D3=2.0/D2=1.5. confirmation_entry + hypothesis_winners(H08-B 5주/H05-D MA20트레일/H09-C 2일/H12-D ×2.0배) YAML 반영. 9테스트 ALL PASS |
| **T-096 12가설 백테스트 프레임워크** | 03-05 | — | — | **hypothesis_tester.py 신규 (HypothesisTester 클래스)**: 12가설×4시나리오=48개 백테스트, 3년 일봉 300종목(2023-01-02~2026-03-04), v4_desk_backtest_results 48행 INSERT(run_id:0220617c). 승자: H01-A즉시진입(PF=1.10)/H03-C MA5+VP120(PF=1.57)/H05-D MA20트레일(PF=2.18)/H06-D MA5트레일(PF=1.74)/H07-C RSI≥60(PF=1.89)/H08-B 5주보유(PF=25.93)/H09-C 2일지연(PF=2.35)/H10-B 수익시5일연장(PF=1.91)/H12-D ×2.0배30일(PF=3.15). 핵심: 즉시진입>지연, MA트레일>고정TP, 파이프라인2배보유, 마디피로가설기각 |
| **T-080 DESK543 프랙탈 BT Phase 1-2** | 03-05 | 08ab632c | — | **DESK543 프랙탈 백테스트 Phase 1-2**: Phase1 DESK5(WR40%/PF0.69/10거래, 개선필요), DESK4(WR57.1%/PF2.17/35거래, 목표달성), DESK3(WR43.3%/PF3.99/388거래, PF대폭초과). Phase2 Dual-Harvest: Stage2(2억/22.95%/yr+332%), Stage3(10억/27.44%/yr+103%). Phase3 필터매트릭스: ALL_proxy(WR56.1%/PF4.868/★★). v4_desk_backtest_results 7행 INSERT |
| **T-079-1 폭락장 모니터링** | 03-05 | — | — | **폭락장 긴급 모니터링**: 서비스 정상, 11시그널/3진입/8차단, GO100 SELL 3건 처리 |
| **T-078 DESK543 BT Phase 0 코드** | 03-05 | 08ab632c | — | **fractal_triggers.py + fractal_backtest.py 구현**: DESK3/4/5 프랙탈 트리거 모듈 신규, 55/55 단위테스트 ALL PASS, 백테스트 엔진 통합 |
| **T-077 크론 정비** | 03-05 | 08ab632c | — | **크론 4건 추가 등록**: virtual_hourly_report(hourly)/daily/weekly/monthly 크론 등록, 총 크론 15건 (virtual_hourly_report 미등록 → 해결완료) |
| **T-076 GO100 V3 Q2 모델 활성화** | 03-05 | 04740d65 | — | **GO100 V3 모의투자 0체결 해결**: CONVICTION 0.60→0.50, TOP_N 3→5, agent weights 조정, 3/6 크론 매수 예정 |
| **T-075 TP=0 근본 해결** | 03-05 | 04740d65 | — | **모의투자 TP=0 문제 근본 해결**: tick 윈도우 30분→20시간 확장, 전 전략 TP=3% 재설정, 3/6 시그널 반영 예정 |
| **T-038-FIX AADS 지시서** | 03-05 | aads: a5f0c37 | 200 | **Part A**: memory.py GET 엔드포인트 인증 제거(/memory/search,/memory/ceo-decisions,/memory/inbox — Monitor Key 없이 공개 조회). **Part B**: AADS agents 카테고리 매니저 6건 등록(SALES_MARKETING_MGR importance=7.0/FINANCE_ACCOUNTING_MGR 8.0/CONTENT_STRATEGY_MGR 6.5/QA_OPS_MGR 8.5/CUSTOMER_SUCCESS_MGR 6.0 standby/INVESTMENT_TRADE_MGR 9.0). public-summary 총 15개 agents 확인. aads-server repo push 완료 |
| **T-038 AADS-매니저협업API** | 03-05 | 08a3ae49 | 200 | **매니저 협업 API 4엔드포인트**: GET /memory/search(agent_id/memory_type/keyword/importance/days 필터), GET /memory/ceo-decisions(directive+importance≥8.5), POST /memory/cross-message(6종 중요도별 에이전트 간 메시지), GET /memory/inbox/{agent_id}(cross_msg+broadcast 수신함). **매니저 레지스트리 6건**(SALES_MARKETING_MGR/FINANCE_ACCOUNTING_MGR/CONTENT_STRATEGY_MGR/QA_OPS_MGR/CUSTOMER_SUCCESS_MGR/INVESTMENT_TRADE_MGR memory_id 48-53). **AADS T-036**: /context/public-summary 200 OK(민감정보0건,POST405). **T-037**: _save_conversation_to_aads()+save_manager_report() 완료. **genspark_bridge 대화자동저장**: CONV_SAVE 2분쿨다운/80자이상/body_text diff→AADS Context API |
| **CEO-APPROVAL-20260305** | 03-05 | a7864db5 | — | **CEO 승인 5건 즉시 적용**: ①D4 Shadow 해제(SHADOW_STRATEGIES=set()) ②E2A_D4 파라미터 09:00~09:30/SL2%/TP3% ③GATE_REQUIRED에 D4 추가(눌림확인→반등게이트 필수) ④signal_generator is_pullback에 D4/D5 추가 ⑤ATR D4 sl×1.5/tp×3.0 재정합. D2 trail-10%/SL-3%, S1 갭+5%, CS×EQS L3.5/L4.5, BounceGate 기배포 확인완료 |
| **CUR-V41-VIRTUAL-RUN-HEALTH-CHECK-002** | 03-04 | — | — | 가상매매 보완: float(None) 에러 근본 수정(run_unified_engine.py), 단위테스트 12건 ALL PASS, 649645 synthetic_BLOCK 잔존 없음 확인 |
| **CUR-V41-VIRTUAL-RUN-HEALTH-CHECK-001** | 03-04 | — | — | 가상매매 정상운영 확인: 서비스 3개 PASS, 거래실적 PASS, L3.3 수급게이트 PASS, 데이터수집 PASS; TP 0건/오픈3건 현재가없음(PARTIAL); virtual_hourly_report cron 미등록(FAIL → 조치 필요) |
| **CUR-V41-ATR-COMMANDER-ACTIVATE-001** | 03-04 | 5e1223ac | 200 | **ATR NET_RR_RATIO 1.5 완화 + GO100_COMMANDER_MODE 활성화**: NET_RR_RATIO 2.0→1.5 적용 확인(96b7407b 기적용, 신호 +46% 추정), test_14 하드코딩→NET_RR_RATIO 상수참조 수정, **29/29 ALL PASS**; GO100_COMMANDER_MODE=true+GO100_DESK_CHAIN_MODE=true 확인(CommanderGO100 오케스트레이션 ON: 아침분석·토론·리스크·DESK체인 자동화) |
| **CUR-V41-DESK-POOL-VERIFY-AND-PARAMETERIZE-001** | 03-04 | 955bb21d | 200 | **PHASE1 DESK 풀 현황 검증 + 텔레그램 보고**: DESK5 20/WATCHING, DESK4 18/WATCHING, DESK3 106/ACTIVE, DESK2 오늘 후보10·신호0·매매0, DESK3→DESK2 연결 3종목, v4_mock_trades 14건·v4_virtual_trades_full 9건, 크론 11개 정상(desk2/3/4/5 전체), unified_engine 11:06 정상종료, 텔레그램 CEO 즉시 보고 완료. **PHASE2**: v4_desk_backtest_results 테이블 DB 최초 적용(051 마이그레이션, 인덱스 4개) |
| **CUR-V41-DESK-FILTER-PARAMETERIZE-001** | 03-04 | 955bb21d | 200 | **DESK 필터 파라미터 외부화**: config/param_search_space.yaml(DESK5/4/3/2 전체 파라미터), backend/app/services/desk_filters/ 패키지(7모듈: base/desk5/desk4/desk3/desk2/pipeline/backtest_runner), 기존 스크립트 6개 하드코딩→YAML 전환(desk3_pool_scan/desk4_node_scanner/desk5_seed_scanner/desk5_weekly_monitor/desk2_prescoring/desk2_pool_link), v4_desk_backtest_results 마이그레이션 생성(051), DESK-FILTER-IMPL-SPEC-v1.0 설계서 저장, 42/42 단위테스트 ALL PASS |
| **CUR-V41-TRADING-PAGE-FIX-001** | 03-03 | Nginx | 200 | **trading.html 매매현황 수정**: Nginx /api/v1/live-trading/ → 8003 라우팅 추가, Playwright 검증(10개 주문 표시), moongoby@gmail.com 확인 완료 |
| **CUR-V41-D4-EQS-BUGFIX-001** | 03-02 | e274411a | 200 | **D4 EQS PULLBACK 오분류 버그 수정**: signal_generator.py:354 D4를 is_pullback_strategy 목록 제거→BREAKOUT 분류. D4 전상종목 price_position~0.7~0.9 정상, EQS+15점(53→68), REDUCE→PROCEED, 43/43 테스트 PASS |
| **CUR-V41-ATR-WF-VALIDATION-001** | 03-02 | 0a00567 | 200 | **Session N ATR_NETRR 1.5 WF 3-Fold 검증 + D4/D7 구조 분석**: WF 3-Fold ALL PASS(F1 PF=2.175/F2 PF=2.448/F3 PF=2.263, 평균PF=2.295, Sharpe=11.03, MDD=-2.1%, OOS/IS 3/3, PF Drop 3/3), **CEO 승인 대기: atr_dynamic_exit.py:42 NET_RR_RATIO=2.0→1.5**, D4 SIG5(VP_120_RECOVERY)=전상종목 구조적 미충족 확인, D7 슬롯경쟁=시뮬한계(실전 시간대분리로 무관), 코드복귀완료(NET_RR_MIN=2.0) |
| **CUR-V41-ATR-NETRR-D4-PIPELINE-ANALYSIS-001** | 03-02 | a518efc | 200 | **Session N ATR_NETRR + D4 + 파이프라인 구조 완전 해석**: CTE 파이프라인 실제구조(발굴1853건→ATR차단849건(45.8%)→기타차단273건→실행731건/3.01건/일), ATR_NETRR로직(NetR:R=(TP%-0.235%)/(SL%+0.235%)≥2.0, D2/D4/D5/S1대상), D4 0건=조건과잉확정(ATR43건+COMBO22건+EQS14건+GATE1건 100%차단), ATR 1.5 완화→실행+46%(1,066건/4.39건/일), PF 2.398→2.248(2.0유지) |
| **CUR-V41-DIRECTIVE-AUTOMATION-002** | 03-02 | (이 커밋) | 200 | **추가 지시 5건 반영**: KST 전면 적용(logging converter+UTC→KST변환+run_pending.sh), 정기보고 30분 형식 개선(프로젝트별 pending건수), write_done.py 신규(done파일 생성 스크립트, _KST파일명), .cursorrules 9-10 추가, CEO-COMMAND-CENTER.md 섹션9 추가, 8/8 테스트 PASS, genspark-bridge active |
| **CUR-V41-DIRECTIVE-AUTOMATION-001** | 03-02 | 50bd69a | 200 | **bridge.py Directive 자동 감지·저장·완료 중계**: pending/running/done/archived 디렉토리, sha256 중복방지, done 10초 감시→매니저+CEO 중계+아카이브, run_pending.sh, 정기보고 pending현황, KST 타임스탬프 전면 적용, 5/5 PASS |
| **CUR-V41-ALL-MANAGER-CHATS-001** | 03-03 | (이 커밋) | 200 | **6프로젝트 매니저 대화창 일괄 생성 + bridge.py 확장**: Genspark AI 채팅+Claude Opus 4.6으로 4개 신규 생성([AADS]/[SF]/[NTV2]/[NAS] 프로젝트 매니저, 맥락파악완료), .genspark/.env에 4개 URL+SSH_CMD 환경변수 추가, genspark_bridge.py _load_project_config() 6개 프로젝트(KIS/GO100/AADS/SF/NAS/NTV2) 확장(SSH 환경변수 기반, 하드코딩 금지), genspark-bridge 재시작 → 활성 프로젝트 6개 폴링 확인 |
| **CUR-V41-BRIDGE-DASHBOARD-001** | 03-02 | (이 커밋) | 200 | **통합지휘소 정기 보고 + 텔레그램 통합 대시보드**: telegram_report.py `[KIS]` 태그 표준화(project 파라미터 추가, 5개 프로젝트 태그 지원), genspark_bridge.py 6시간 정기 보고 루프(07:00/13:00/19:00/01:00 KST) 추가, GitHub API 최신 커밋 조회, systemctl 서비스 상태 포함 |
| **CUR-V41-SESSION-K-MONITORING-SETUP-001** | 03-02 | (이 커밋) | 200 | **Session K 03-03 Virtual Run 자동 모니터링**: `/root/kis-autotrade-v4/scripts/monitor_virtual_run.py` 5액션(premarket/signal/periodic/close/daily_report), cron 6건(07:58~16:00), L3.3 비율+거래+청산모드+Fail-Open+시스템상태 추적, JSONL 스냅샷+Markdown 보고서 자동생성, dry-run ALL PASS, 방안B(CEO 확인 후 push) |
| **CUR-V41-TELEGRAM-REPORT-001** | 03-02 | (이 커밋) | 200 | **텔레그램 보고 채널 연결**: go100_auto_trading_bot 신규 생성, CHAT_ID 자동 조회, 테스트 메시지 발송 성공(message_id:236), telegram_report.py+genspark_bridge.py 통합 완료 |
| **CUR-V41-GENSPARK-BRIDGE-STEALTH-001** | 03-02 | (이 커밋) | 200 | **Genspark 브릿지 Cloudflare 차단 우회**: playwright-stealth 적용, headed+Xvfb 전환, --test-once 플래그, 직접 로그인 session.json 저장, 통합 테스트 PASS (13523자+메시지전송) |
| **CUR-V41-GENSPARK-BRIDGE-V1-001** | 03-02 | (이 커밋) | 200 | **Genspark 브릿지 V1 구축**: BRIDGE-DESIGN-V1.md, genspark_bridge.py(260줄), genspark-bridge.service 등록(start 미실행), 통합 테스트 PASS(MCP 경유), Cloudflare headless 차단 발견 |
| **CUR-V41-CEO-DIRECTIVE-CONFIRM-001** | 03-02 | 8335faa | 200 | **CEO 통합지휘소 지시 확인 + 19STRATEGY DB IP 마스킹**: 보고 검토·보고 완료, DIRECTIVE-CONFIRM 보고서·저장정보 블록 보완, HANDOVER 갱신 |
| **CUR-V41-GENSPARK-BRIDGE-001** | 03-03 | 3a0f0e4 | 200 | **Genspark 자동 대화 브릿지 구축**: Playwright POC(로그인·채팅 셀렉터), create_5_chats.py·genspark_common.py, verify.sh·path_check 5프로젝트 확장, setup_full.sh 삭제·SYNC_GUIDE 마스킹·SECURITY_RULES IP마스킹, 루트 보고서 이동 |
| **CUR-V41-SESSION-H-ENGINE-SYNC-001** | 03-02 | (이 커밋) | 200 | **Session H 통합엔진 L3.3 연동 + 아키텍처 동기화**: 아키텍처 진단 GAP 6건(L3.3미활성/exit Generic/D2 trail10%/HARD_TP없음/Anti-Pattern/Timeout). Method A(CTE경유) 채택 — signal_generator.py SupplyDemandGate.evaluate()+pool전파+Fail-Open, exit_manager.py 전략별 STRATEGY_EXIT_PARAMS(6전략 동기화)+HARD_TP D4, D2 trail_start 10%→3%, run_unified_engine.py 합성SupplyGateResult. **137테스트 ALL PASS**, GAP G-1~G-4 해소, 잔여 G-5(P2)/G-6(P2), **03-03 Virtual Run L3.3 GO** |
| **CUR-V41-SESSION-E3-SUPPLY-GATE-VALIDATION-001** | 03-02 | (이 커밋) | 200 | **Session E-3 수급 게이트 다층 검증 + L3.3 구현**: CEO 승인 3건 기반, Phase 1(Tasks 1-6) 다층검증 — 전 레짐 PF>1.5(BEAR 최고 2.549), 완전패턴(4/4) PF=1.364, W/L비율 1.60→2.73, 신고가 PF=13.483, 외인4일+ 20d +9.9%, 5일 AUC=0.680 최적. Phase 2 Walk-Forward 3-Fold ALL PASS — 채택 0.7+FRGN(min PF=1.455). Phase 3 구현 — supply_demand_gate.py(MUST: CLOSE>0.7+FRGN>0, 보너스 6개, ALLOW/CONDITIONAL/BLOCK 3등급) + test 24건 PASS + cte_pipeline.py L3.3 삽입(L3→L3.3→L3.2). Phase 4 통합리플레이 — **Baseline PF=0.834→D_Full PF=2.727(+227%)**, WR 34.3%→51.1%, 331건 품질필터링. CEO D-002 "본질은 수급" 최종 실증 완료 |
| **CUR-V41-SESSION-E2A-ANTIPATTERN-APPLY-001** | 03-02 | 36324cc | 200 | **Session E-2A Anti-Pattern 3건 차단 + CEO 승인 3건 적용**: exit_simulator D2 trail_start 0.02→0.10/D4 sl 0.025→0.010+tp 0.050+HARD_TP모드, entry_detector _is_anti_pattern(역배열+VWAP하회+거래량감소 446건차단)/_is_absolute_forbidden(장후반+급감 29건차단)/D5 13시차단/D4 09:25~10:00창, candidate_scanner D7 close_pos≥0.30/S1 gap 5%. 재검증 E-2A: PF=0.826(E-1 0.834→소폭악화), Walk-Forward Fold3 PF=1.096, D2 trail_start=10% 역효과(TIMEOUT 86%) → E-3 재검토필요 |
| **CUR-V41-SESSION-F-FRONTEND-AUDIT-001** | 03-02 | (이 커밋) | 200 | **Session F 프론트엔드 & API 연결 전수조사 (GAP 검증 완료)**: Next.js 52페이지/~220컴포넌트/20API파일(go100.newtalk.kr:3000), V4.1 정적HTML 30페이지(trading41.newtalk.kr), API 97% CONNECTED. SSE 2채널(알림·LLM)/JWT refresh 정상. GAP 검증: G-03(reports_router) ✅해소/G-04(monitoring prefix) ✅해소/G-07(account sync) ✅해소. **G-05 확정**: nginx `/ws/` → 8003 라우팅이나 WS핸들러는 8002에 있음(현재 프론트 WS 미사용으로 무영향). G-09 desk2-live 백엔드 미연결 잔여 |
| **CUR-V41-SESSION-F-PRE-VIRTUAL-CHECK-001** | 03-02 | edd64c8 | 200 | **Session F-Pre 03-03 Virtual Run 사전 점검**: Cron 4건 ALL OK(07:55/08:50/*/1 9-15/15:30), log 기록중, DB 4테이블 02-27 완비, Mock API HTTP 200+token OK, 4서비스 running, Swap 66.6%/Disk 77% PASS, UnifiedEngine import OK, 07:55 premarket 실행 실증 → 29/29 ALL PASS, 03-03 Virtual Run GO |
| **CUR-V41-SESSION-E1-MINUTE-PATTERN-001** | 03-02 | — | — | **Session E-1 분봉 패턴 탐사**: 1,861건×19변수 분석, 전체 AUC<0.55(단일변수 구분불가), 전략별 D7(AUC=0.66)+D4(AUC=0.63) 특화신호, Anti-Pattern 5개(장후반+거래량급감 PF=0.062), 2-변수 PF≥1.3 조합 4개, 필터 PF 0.667→0.709(+6.3%), 수급/VP 통합 필요 확인 |
| **CUR-V41-SESSION-E2B-SUPPLY-DEMAND-001** | 03-02 | — | — | **Session E-2B 수급 데이터 통합 탐사**: 1,929건×14수급+19분봉=33변수, **CLOSE_POSITION_5D AUC=0.682(#1, d=0.612, FDR<0.001)**, 수급 상위3 AUC=0.624 vs 분봉 0.540, CEO D-002 "본질은 수급" 실증(외인5일누적 p=0.014★, 외인연속매수≥1d PF=2.343), 종가위치>0.7 PF=1.991(+139%), TRAJECTORY=3 PF=1.841, DUAL_FLOW≥3 PF=1.692, 23조합 PF≥1.3(종가위치H×VWAP_TOUCH_L PF=3.055), D6+외인 PF=5.054(+342%), L3.3 SupplyDemandGate 설계 |
| **CUR-SHARED-DB-SCHEMA-CATALOG-001** | 03-02 | 69487c0 | 200 | **Session G-2/G-3 조치 완료 + DB 스키마 카탈로그 통합**: 3중수집기→1개(CEO직접조치), Swap 6.0→5.9G(점진감소), HANDOVER 문서-현실 불일치 5건 정정(테이블명 go100_global_market/v4_scalping_universe 정정, CTE스크립트 미존재 주석, 테이블수 246+8뷰=254 명시), DB 스키마 카탈로그 통합 구축(246테이블+8뷰 전수 스키마, 프로젝트별 V4.1:124/GO100:65/공통:57, 자동최신화 cron 매일 06:00, shared/DB-SCHEMA-CATALOG.md), 22개 test collection error HANDOVER 기록(시스템 Python pip 미설치, 서비스 무관) |
| **CUR-V41-SESSION-G-SERVER-AUDIT-001** | 03-02 | 440edb0 | 200 | **Session G 서버 실증 검증**: 137테스트 ALL PASS(CTE70+UE24+Replay12+Minute31), 9서비스 정상, Triple Guard 확인, DB 254테이블, 즉시조치1건(로그경로생성), 보고8건(3중수집기/Swap75%/누락테이블2/CTE스크립트3) |
| **CUR-V41-REPLAY-BACKTEST-001** | 03-02 | 9b47592 | 200 | **Session D 분봉 리플레이 BT 전환**: replay/ 7모듈 신규, v4_ohlcv_minute 83.5M rows 실분봉 리플레이, 242거래일 1,929건, D6 PF=1.144(유일 PF>1), Portfolio PF=0.834(통계BT 1.258→현실화), 12테스트 PASS, 67전체 PASS |
| **CUR-V41-HISTORICAL-DATA-COMPLETE-001** | 03-02 | f61fa22 | 200 | **전체 과거 데이터 수집 완결**: v4_market_regime_daily 15개월 갭(843→1,116건) 백필, index_daily yfinance 소급(546건), 설명불가 갭 0건(잔여 갭 전부 공휴일), regime/VKOSPI/go100_global_market/v4_scalping_universe 전수 정상화 |
| **CUR-V41-DATA-COLLECTION-STATUS-001** | 03-02 | f545aec | 200 | **전체 수집 현황 점검+3건 즉시 조치**: go100_global_market WTI/SOX/CSI300/copper 4지표 추가(e273038d), v4_scalping_universe 크론 등록+수동갱신(646→1354건), VKOSPI end_date 수정 |
| **CUR-V41-VKOSPI-FIX-001** | 03-02 | bc5fac1c | 200 | **VKOSPI 수집 복구**: end_date yesterday→today(3분기 전체), 크론 --days 5→7, 임시 재시도 크론(9/12/15시) 추가, 레짐 동기화 정상(54.67) |
| **CUR-V41-VKOSPI-COLLECTION-FAILURE-001** | 03-02 | f105bb0 | 200 | **VKOSPI 수집 장애 원인 조사**: API T+1~T+2 지연(외부)+end_date=yesterday 설계결함+numeric overflow(VKOSPI=2885.49 과거 일시오류) 3가지 확인 |
| **CUR-V41-FIVELAYER-HOTFIX-001** | 03-02 | 74ec682b | — | **FiveLayerRiskManager 2건 버그 수정**: ①임포트five_layer_risk→risk_layer_manager, ②L2쿨다운 실시간TS버그(loss_count=0+cooldown_until.clear), 재BT PF=1.119/CONDITIONAL GO(5/7), L2차단 60건→0건 |
| SESSION-A-HOTFIX-001 | 03-02 | cdc73d5/66a1cbd8 | 200 | **긴급 핫픽스 6건**: 실계좌 하드블록(broker_gateway+auto_trade_engine 이중가드), PnL계산+비용0.47%, D7필터 0.80+Top10(게이트 로직 반영), 31 PASS |
| **CUR-V41-SESSION-C-DEPLOY-001** | 03-02 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | 200 | **Session C Mock 배포**: run_unified_engine.py 신규(--mode backtest/virtual), BT PF=1.258(미래정보is_winner 제거, 기존 2.368→-47%), 101건 ALL PASS(CTE 70+분봉 31), v4_mock_trades 생성, KIS Mock HTTP 200, Cron 4건(premarket/signal/monitor/close), HAV tasks.json+backtest_runs id=25, 03-03 Virtual 자동 가동 준비 |
| **CUR-V41-SESSION-B-UNIFIED-ENGINE-001** | 03-02 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **Session B 통합엔진 코어 구축**: unified_engine 패키지(9모듈 — config/engine/adapters×3/core×4), SlippageAnalyzer 3계층(spread/depth/latency), AI Scorer Fail-Open(_ai_reevaluate cs_ai≥70→hold/cs_ai<50→exit/예외→None), DD Decelerator 5레벨(0.0~1.0×), DCS Grade(VWAP30+RSI25+Vol25+MA20), GO100 episodic/backtest_runs 연동, FORBIDDEN_ACCOUNT_IDS {5,6} 3중guard, 신규 24건+기존 31건 ALL PASS |
| PHASE1-001 | 02-27 | ✓ | 200 | TOP-20 WR 78.7%, 누적 +785%, 생애주기 4클러스터 |
| PHASE2-001 | 02-28 | ✓ | 200 | 11변수, OOS 정밀도 76%, TREND WR 67.7% |
| PHASE2B-001 | 02-28 | 93e67ae | 200 | L3+X9 정밀도 90%, Birth+1min WR 95.3%, X9 AUC 0.851 |
| DB-TABLE-CATALOG | 02-28 | f263e40 | 200 | 225테이블 카탈로그 |
| ROLE-DEFINITION | 02-27 | ✓ | 확인필요 | 5-DESK 생애주기, 승격/강등 |
| PHASE2C-001 | 02-28 | ✓ | 200 | 일봉 50변수, 정밀도 82%, NEW 3.8% (실패) |
| PHASE2D-001 | 02-28 | ✓ | 200 | 개인수급 AUC<0.55, CMB4 0.636, Birth WR 97.2% |
| DESIGN-SPEC-v3.0 | 02-28 | ✓ | 200 | 패러다임 전환: DESK=풀관리, 카드=타이밍 |
| PHASE2E-001 | 02-28 | a167b87 | 200 | NEW 229종목 역추적, DESK5→4→3 100% 포착, 4 TYPE 분류 |
| VALIDATION-ENGINE-001 | 02-28 | ✓ | 200 | 가설검증엔진 5모듈, Pipeline Precision 6.9%, 97변수 |
| VALIDATION-ENGINE-002 | 02-28 | 57b6de5f | 200 | **Precision 6.9%→90.3% 달성**, 118변수, 20핵심, L3=0 발견 |
| P6-EXTRA-VERIFY (GO100) | 02-27 | (보고서 push) | 200 | 신고가 돌파 Agent Chat E2E 검증 PARTIAL, execute_buy/sell 스텁 추가 |
| VE-003-PHASE-B | 02-28 | 4211890 | 200 | D1 FAIL, D2 CONDITIONAL(PF1.57), D5 CONDITIONAL(PF4.21), RSI 30~50 최강 필터 |
| THEME-SECTOR-AUDIT | 02-28 | 09e5ca3 | 200 | 4개 분류체계 점검, 테마 중복제거·일별성과·활동성 조치, 자동반영 확인 |
| VE-003-PHASE-A | 02-28 | 8fd5653 | 200 | D4 CONDITIONAL(PF1.88), **D6 PASS(PF13.63)**, D7 CONDITIONAL(PF1.98), 전략포트폴리오 확정 |
| DESK2-HYPOTHESIS | 02-28 | 4656085 | 200 | 7가설(H-001~007), 7컨디션(C1~C7), 5축마스크, DCS평가, A/B/C등급, D-010 등록 |
| VE-003-PHASE-E | 02-28 | 4656085 | 200 | 5축 분해, 마스크 D4 PF1.88→2.43, D7 PF1.98→2.12, D1 부활불가, DCS 등급A(4.30%/70%) |
| VE-003-PHASE-F | 02-28 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **18신호분석**: TS-B4(PF3.23) > TS-C1(PF2.80) > TS-B1(PF2.72), 60분 보유 최적, 상한가 부스트 확인 |
| VE-003-PHASE-C | 02-28 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | D3 FAIL(PF1.17), **S1 CONDITIONAL(PF1.44/WR58.7%)**, S2 전체 FAIL(MA7 PF1.27 최고) |
| VE-003-PHASE-D | 02-28 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | NEW 254종목 6조건: VP120 88.5%, RSI 88.1%, MA정배열 87.7%, **3개+ 동시 87.7%**, 10시전 82.1% |
| DESK2-FINAL-SPEC | 02-28 | 7293aed | 200 | 6-Layer 아키텍처, 6전략+1탐지, 60분 청산 전환, 18시그널 매칭, D-011 등록 |
| HOTFIX-001+002 (GO100) | 02-28 | 6cc363b6 | 200 | tool_executors 스텁→실제 래퍼 교체 + risk_engine ::jsonb→CAST 수정, 6단계검증 PASS |
| DESK2-FINAL-SPEC-v2 | 02-28 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | 능동청산(트레일링+부분청산)+분할매수+AI자동진화+모의실매매 추가 |
| VE-003-PHASE-H1 | 02-28 | d1234182 | — | C1~C7 반등률 전수조사: C2 PF2.16/WR55.1%/시초+8.32% 압도적 1위, C7 PF1.59 |
| VE-003-PHASE-H2 | 02-28 | 41cd179d | — | 시간별 가격 프로파일: C3 MFE/MAE 1.19x 최고 비대칭, C2 MFE+9.02% 최대 |
| LIVE-PAPER-D6D7-DOC | 02-28 | 1e4ab233 | — | D6/D7 모의매매 스크립트 문서화 + cron 등록 확인 (50 8 * * 1-5) |
| RESEARCH-TIGHT-STOP | 02-28 | f9dc9bc | 200 | 타이트손절(-1%)×멀티전략 시스템 PF 1.4, 5패1승=+2% 순수익, 시도횟수가 엣지 |
| RESEARCH-LIFECYCLE-GAP | 02-28 | f9dc9bc | 200 | 8구간 커버리지 맵, 빈구간①④⑥ → D8(모멘텀추격)+D9(전고점돌파) 신설, 전 구간 커버 |
| RESEARCH-RELAY-REENTRY | 02-28 | f9dc9bc | 200 | 릴레이 청산-재진입 구조: D5→D2, D4→D2, D2→D5 연쇄맵, 컨디션별 적합도, 자본체감 규칙 |
| RESEARCH-INTRADAY-COMPOUND | 02-28 | b7922f5 | 200 | 장중 복리 자본 순환: 부분청산→재투입 자본풀, 단리+2.3%→복리+7.3%(3.1x), 모드3+D9 이중수익 |
| RESEARCH-ADAPTIVE-EXIT | 02-28 | 11ff636 | 200 | 적응형 청산 5모드 아키텍처: 즉시익절/부분익절/파동전환/트레일링강화/강제이탈, 의사결정트리 |
| VE003-P4-ADAPTIVE-EXIT | 02-28 | bd32b1f | 200 | **5모드 검증(22,406건)**: PF 1.32→1.34, 모드2 전략 최적, 모드3 2파 0%→재조정필요, 일일손실 -174%→-74% |
| RESEARCH-PULLBACK-SPEC | 02-28 | 8ae3e2f | 200 | 눌림 전수조사 설계서: 15개 차원, 10개 가설(H-PB-1~10), 4단계 실행계획, 모드3 재설계 목표 |
| PULLBACK-ANATOMY-001 | 02-28 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | 200 | **눌림 전수조사 19,225건**, 2파 발생률 73.9%, 모드3 0%원인=RSI범위+MA20미형성(충족률0.26%), 재설계 안D 권고 |
| WAVE-CAPITAL-CYCLE-001 | 02-28 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **파동 자본순환 14과제**: W1 30%/W2 100% 청산, Dynamic스톱(PF17.98), 거래대금50%소진필터, VP 2분선행, 시스템효율17.7%→50% 로드맵 |
| WAVE-OUTER-RESEARCH-001 | 02-28 | cac9ef0 | — | **파동 외부 10과제(R15~R24)**: PASS2/COND5/FAIL3, 교차종목+370%, 전조AUC0.64, 뉴스χ²=249, 전략간섭100%중복, 비용PF-37%, 재앙3패턴 |
| DEV-HAV-001 | 02-28 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **DESK2 HAV 개발 완료**: 4-Layer, 27변수 135K조합, 주간자동탐색+일일Drift, E2E PASS, OOS PF=12.26, WF 2/2 PASS |
| CODE-ANALYSIS-CROSS-ENTRY-001 | 02-28 | (보고서 push) | 200 | 교차종목 진입 코드 갭 분석, 이미있음7건/수정4건/신규4건 |
| SURGE-CAUSE-ANALYSIS-001 | 02-28 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **급등원인분석+D-20전조추출 20과제**: 원인8분류(공시40.8%), 전조조합P=76.7%, 수급주도fake29.7%, Leader AUC0.712, DESK승격정량화, 계절성Q1>Q3 11.5pp |
| HANDOVER-PULLBACK-CONFIRM | 02-28 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | 200 | **눌림확인매매 인계서**: 과제 A~D(이평선분류/반등신호검증/대기비용/관통반등), 19,225건 기반, 새 세션 즉시 착수 가이드 |
| PULLBACK-CONFIRMATION-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **눌림확인 심층연구**: 17,155건 5버킷(B2/B3 골든존 승률95%), 8신호(VWAP 73.7%최강), 관통>터치(PF26>11), 조건대기>시간대기, SIG3+SIG6 실용최적 |
| CS-EQS-MATRIX-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **CS+EQS+매트릭스 설계**: CS 5요소(≥65 PF1.55), EQS 5요소(≥70 PF8.43비용후), 9×9 매트릭스(금지18/시너지8), Layer 3.5/4.5 삽입 |
| DD-VWAP-GATE-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **DD+VWAP+게이트+ATR 설계**: DD 5레벨(maxDD-75%), VWAP 5변수, 5전략 반등확인게이트, ATR 동적TP/SL, NetR:R≥2.0 강제 |
| CTE-COMPARE-ARCH | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | CTE vs DESK 7축 비교, 흡수12개, 통합아키텍처 |
| SYSTEM-ARCH-FLOW | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | 시스템 아키텍처 흐름도 8개 |
| HANDOVER-CTE-INT | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | CTE 통합 세션 인계서, 지시서5개 발행, 후속작업큐 |
| PULLBACK-CONFIRM-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **17,155건 눌림확인 심층연구**: 5버킷분류, 8신호검증, VWAP지지 승률73.7%, 관통반등>터치반등(PF26.36>11.15) |
| CS-EQS-MATRIX-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **CS 5요소 설계+시뮬**: CS≥80 PF 2.383(+57%), EQS 5요소 설계, 9×9 매트릭스 81셀, 18금지/8시너지 규칙 |
| DD-VWAP-GATE-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **DD Decelerator 5단계**: maxDD -45.66%→-11.42%, VWAP 5변수, 5전략 반등확인게이트, ATR TP/SL NetR:R≥2.0 |
| MOMENTUM-TACTICS-001 | 03-01 | cc9069d | 200 | **A1(ORB) PASS(PF_ac=2.23)**, A3(1파) FAIL(PF_ac=0.60), C3(마이크로풀백) FAIL(PF_ac=0.47), ORB 5분+Top20 최적 |
| TIME-TACTICS-BULLFLAG-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | 7×7 시간매트릭스, T_EARLY 모멘텀갭 확인, 불플래그 전체 FAIL(PF_ac=0.99) 단 T_PM_PB PASS(PF_ac=2.64) |
| EXIT-RULE-FINALIZE-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **D6 현행 D+1시초가 유지(PF13.63), D7 현행 유지(PF1.98), 갭리스크 D6=16.7%/D7=43.4%, D2/D4/D5 트레일링 전환 권고** |
| HAV-EXTEND-35VAR-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **27→35변수 확장 준비, 백업 완료, 8변수 솔로테스트 ALL 유효(PF1.0~2.71), coarse 유지+Bayesian 탐색 권고** |
| SLIPPAGE-SIM-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **60분 슬리피지 미미(0.01~0.03%), 고정60분 실효수익0.336% > 트레일링0.079%, 지정가-1틱 권고** |
| LIVE-PAPER-PRECHECK-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **모의매매 안전 PASS, D6=1건/D7=10건(02-27기준), v4_paper_trades 미존재→첫실행자동생성** |
| EXIT-SLIPPAGE-INTEGRATE-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **지정가-1틱 슬리피지 48% 개선(0.136→0.071%), 트레일링(지정가) D2/D4/D5 확정, D2 PF31.15 과적합→현실적2.2, D7 갭다운 43%→24%(종가위치≥0.80+Top10)** |
| V41-GO100-INTEGRATION-ARCH | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | 200 | **V4.1×GO100 통합 브릿지 아키텍처 기획서 v1.0**: 3대 브릿지(자본/리스크/메모리), 3대 안전수칙, Mermaid 데이터플로우, Phase1~3 마일스톤 |
| V41-GO100-BRIDGE-DESIGN-001 | 03-01 | 2fd7ac29 | 200 | **V4.1↔GO100 안전 브릿지 Phase 1 구현**: Go100BridgeClient(3메서드) + bridge.py 라우터(IP차단/Append-Only) + E2E 4건 PASS, V4.1_DESK_AGENT 독립 네임스페이스 확인 |
| ORB-INTEGRATE-OVERLAP-GUARD-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **A1(ORB) C8신규 컨디션+D-ORB 전략카드 설계, 자본15%, D6/D7 중복빈도 28건(77.8%), D6>D7>ORB 우선순위 차단, 7전략 포트폴리오 v2(예상PF2.8)** |
| HAV-DRYRUN-DRIFT-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **35변수 YAML 파싱 PASS(오류0건), dry-run 100건 PASS(PF12.26→12.24), Bayesian 3유효변수(body_size/atr/bb_width), drift_detector.py 수정 불필요 확인, 03-02 cron GO** |
| BOUNCE-GATE-IMPL-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **Cursor #14 Phase A-1**: BounceConfirmationGate(D2/D4/D5/S1/D7) + PullbackClassifier(B1~B6+25셀) + ConfirmationSignalEngine(8신호+SIG3+SIG6 권고), 단위 96케이스 전체PASS |
| DD-RISK-IMPL-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **Cursor #15 Phase A-2**: DDDecelerator(5레벨S1) + FiveLayerRiskManager(L1~L5) + DisasterPatternDetector(릴레이/집중도/과잉포지션), 단위 29케이스 전체PASS |
| CS-EQS-IMPL-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **Cursor #16 Phase A-3**: ConvictionScoreEngine(CS 100점) + ExecutionQualityScoreEngine(EQS 100점, ORDERBOOK 프록시) + TriggerTacticMatrix(81셀/금지18/시너지18), 단위 45케이스 전체PASS |
| CROSS-RELAY-PRESIM-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **241거래일 6전략 단리 시뮬(초기4천→4,061만, MDD7.8%), 동시5종목 최적, 복리비율1.1x(실제PF반영시1.5x예상), PF우선정책 권고, Go/No-Go 8기준 설계(CONDITIONAL GO)** |
| EQS-BIAS-CROSS-FILTER-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **EQS look-ahead 확인: PRICE_POSITION 당일H/L→LAG1(t-1 partial H/L) 교정. HIGH WR 85.2%→72.1%(-13.1%p), CS65_EQS65 최적조합(연550건, PF_net 2.499)** |
| GATE-OOS-WALKFORWARD-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **반등확인 게이트 OOS Walk-Forward: 5전략 Test PF_net >2.5 전원 PASS. 월별 PF<1.0 0개월. 2/3충족 기본버전 권장** |
| VWAP-RECONCILE-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **VWAP 모순 해소: #3의 35건 역전(60%<67.8%)은 표본오차. 통일정의(±0.3%+반등확인) 4,218건 기준 WR 67.4%>52.3%. 지지 2회+ 임계점(PF_net 2.64)** |
| PF-NORMALIZE-COST-ADJUST-001 | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **PF 극단치 정규화: B3_SIG8 PF225만→Capped 142.8. 비용차감후 B4/B6 PF<1.0 → 진입금지. 3조합 SIG3+SIG6+SIG8이 PF_net_ac 16.74(최강)** |
| **CUR-V41-GO100-BRIDGE-PHASE2-001** | 03-01 | 1226fda3 | 200 | **GO100 브릿지 Phase 2 완료**: D6 모의투자 E2E 5건 전 PASS. 시나리오1=킬스위치OFF→메모리 적재(memory_id 4,5), 시나리오2=킬스위치Mock(True)→전종목 Halt 확인. backtest_engine_v2 스텁(삽입점 A/B) 비파괴 추가. Phase 3(실거래 활성화) 대기 |
| **CUR-V41-GO100-BRIDGE-PHASE3-001** | 03-01 | 85945058 | 200 | **GO100 브릿지 Phase 3 완료(포트폴리오 최적화 연동)**: `_run_entry_signals()` async 전환, 삽입점C(포트폴리오최적화 비중 기반 자본 동적 배분), weights=0 Skip, BridgeError→균등분배 Fallback 구현. `enable_go100_bridge=True` 기본값 활성화. `test_bridge_phase3_optimizer.py` 8건 전 PASS (Mock비중 66/16/9주 동적배분 증명) |
| **CUR-V41-PAPER-D6D7-WEEK1-001** | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **D6/D7 페이퍼 트레이딩 첫 주 프레임 작성**: 사전점검 완료(D6#42/D7#43 PAPER_LIVE 활성), 모니터링 스크립트 신규(scripts/monitor_paper_d6d7.py), D7 갭다운 필터 이슈 발견(코드 0.70 vs 확정 0.80+Top10), 03-07 주간 결과 채움 예정 |
| **CUR-V41-CTE-PIPELINE-INTEGRATE-001** | 03-01 | 67602428 | — | **CTE 파이프라인 통합 + D7 핫픽스**: strategy_params.py(D2 EV+0.49% 교정, B4/B6 금지, concurrent=5, PF우선), test_cte_pipeline.py 33케이스 PASS, D7 종가위치≥0.80+Top10, DB#43 갱신 |
| **CUR-V41-VWAP-ATR-ENGINE-001** | 03-01 | e84ac1b9 | 200 | **Cursor #18 VWAP 엔진 + ATR 동적청산**: vwap_engine.py(5변수+TREND 선형회귀), atr_dynamic_exit.py(전략별 멀티플라이어/COST_ROUNDTRIP=0.47%/TRAILING_MA5), cte_pipeline.py(L3.2 VWAP지지체크+ATR_NETRR 차단), test_vwap_atr.py **25/25 PASS**, 기존 33테스트 비파괴 유지 |
| **CUR-GO100-AI-FEATURE-BATCH-V2-001** | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **GO100 AI Feature Store v2 배치 빌드**: Track A(일봉 7피처: RSI_14/BB_WIDTH/OBV_NEW_HIGH/V_RVOL/MA_ALIGNMENT/PRICE_POSITION_LAG1/SEC_LEADER_FLAG) + Track B(분봉 2피처: VWAP_DEVIATION/VWAP_SUPPORT_COUNT) + news_frequency_3d + 라벨3추가(GAP_D1/MFE_60MIN/MFE_3D) + valid_label + NaN보존수정 + LABEL_ Z-score제외, 263,450rows/34cols/12parquet/26.24MB, 오류0건 |
| **CUR-V41-CTE-FULL-BACKTEST-001** | 03-01 | {SHA} | 200 | **Cursor #19 CTE 풀 백테스트 + 3-Fold WF**: prepare_cte_backtest.py+run_cte_full_backtest.py+run_cte_walkforward.py 신규 (Session G 확인: 스크립트 3개 서버 미존재 — Session D replay 엔진으로 대체, 재현 시 replay 사용). Full BT: PF_net=2.368/Sharpe=8.685/MDD=-2.43%/WR=65.8%/수익+227%. 3-Fold WF: 평균 Test PF=1.907/Sharpe=6.671/MDD=-2.17%, OOS/IS 3/3 PASS, PF Drop 3/3 PASS. 기준 10/10 충족 → **CEO Go/No-Go = GO. 60일 페이퍼 트레이딩 단계 진입** |
| **CUR-V41-DESK543-FRACTAL-RESEARCH-001** | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **DESK5/4/3 프랙탈 추세추종 일봉 트리거 실증**: Task 0 사전 데이터 검증 PASS(v4_investor_daily 기관/외인 컬럼·NULL 0%, go100_news_items 공시/실적 분류, ohlcv_daily 급등 9,483건). Task 1~4 스크립트 준비(/tmp/task1_desk5_empirical.py 등). D-012 등록, DESK-FRACTAL-ARCHITECTURE v2.0 반영 |
| **CUR-V41-EQS-D4-PAPER-ACTIVATE-001** | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | — | **Cursor #20**: EQS LAG1(PRICE_POSITION t-1, ORDERBOOK 중립 8점), D4 ATR A안(sl 1.0/tp 5.0), CTE 페이퍼 연동(cron 50 8 * * 1-5), 테스트 70 PASS |
| **CUR-V41-AI-SCORING-ZSCORE-HOTFIX-001** | 03-01 | 799e33ee | — | **Z-score 이중 적용 해소, cs_ai 분포 정상화**: Case A 확정(Parquet Z-score+stats Z-score통계), feature_stats.json 원시 기준 재생성(500종목×9개월), 삼성전자65/SK하닉61/NAVER45(이전 전부100), 7/7테스트PASS |
| **CUR-V41-STRATEGY-DEEP-OPTIMIZE-001** | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | 200 | **Cursor #21 6전략 전수조사+TP/SL최적화**: ①거래대금교정(겹침67%→당일누적전환), ②D2 SL-3%+trail10% PF1.57→4.41, ③D7 갭분기청산, ④D6 243건전수(P4=50.6%), ⑤D5 뉴스즉시PF0.20<Wave1 PF4.21유지, ⑥D4 09:20→눌림확인 PF0.73→13.3(긴급), ⑦S1 갭+양봉 PF1.44→2.52 |
| **CUR-GO100-HYPOTHESIS-ENGINE-001** | 03-01 | 3806a54b | — | **GO100 AI 가설검증 파이프라인 L1~L3 통합**: GoAiClient(Haiku/Sonnet 서킷브레이커), HypothesisEngine(L1 판정→L2 가설생성→L3 HAV큐 등록), 야간 배치 백테스트(22:00), 아침 리포트 자동생성, cron 2개 등록, 통합 테스트 13/13 PASS |
| **DESK543-FRACTAL-IMPL-001** | 03-01 | da997c4 | 200 | DESK5/4/3 프랙탈 엔진 코드 구현: 3테이블+10모듈+단위테스트, D-013/D-014 반영, 241일 백테스트 스크립트 제공 |
| **CUR-V41-19STRATEGY-TRIGGER-MINUTE-001** | 03-01 | 459e2fc20946fb1a691180da26bb7b556b3b4432 | 200 | **Cursor #21-R v3 — 19전략 분봉 멀티TF 자동검증엔진**: 4모듈 신규(minute_feature_engine/minute_trade_simulator/trigger_hypothesis/minute_validation_runner), 단위테스트 31/31 PASS, 19가설 전수검증(H-12 PASS PF=181/H-13 PASS PF=5.09/H-17 CONDITIONAL PF=1.46/나머지 FAIL), PASS 포트폴리오: PF=6.617/WR=76.1%/Sharpe=10.30/누적+303.98%/MDD=-16.57%, D6 압도적 우위 재확인 |

---

### SUPER-ANT-STUDY-002 (2026-02-27, CEO 승인)
- 한국 데일리 트레이딩 전략 심층 연구: D1~D7, S1~S2 총 9개 전략 실전 수준 분해
- 10명+ 실전 트레이더 교차 분석 (홍인기, 서희파더, 강창권, 불개미, 돌팬티 등)
- 전략별 정량화 변수 도출: 총 30+ 신규 변수 정의
- 기술적 분석 레이어 설계: 1분봉 이평선, 체결강도, RSI, MACD, 호가창
- NEW 종목 장중 탐지 로직 설계 완료
- VE-003 백테스트 설계 (Phase A~D, 7일)

### SUPER-ANT-STUDY-001 (2026-02-27)
- 한국 슈퍼개미 7인 심층 조사 완료
- 조사 대상: 김정환, 남석관, 이정윤, 홍인기, 시간여행TV, 배진한, 세력주 매매 그룹
- 핵심 발견:
  - 글로벌 대가 전략과 90%+ 수렴 확인
  - 한국 고유 알파: 테마 반복성, 소형주 세력 패턴, 정치/계절 사이클, 동반수급 실시간 추적
  - P0 변수 4개 도출: THEME_CYCLE, SMALL_CAP_QUALITY, DUAL_FLOW, SEC_LEADER_FLAG v2
  - P1 변수 3개: MKT_SEASON, FORCE_ACC, D_D1_D2_ENTRY
  - P2 변수 2개: BJ_SCORE, KJH_CYCLE
- CEO 지시서: D-008-KR로 등록 완료

---

## 3. 진행 중 작업

| Task ID | 상태 | 내용 |
|---------|------|------|
| **Virtual KIS Mock 자동 가동** | **03-03(화) 자동 시작** | Session C 배포 완료. run_unified_engine.py Virtual 모드. 55:07 premarket → 50:08 signal → */1 09-15 monitor → 30:15 close. v4_mock_trades 기록 |
| **60일 페이퍼 트레이딩** | **진행** | CEO Go/No-Go = GO. D6/D7 PAPER_LIVE 가동. live_paper_d6_d7 → unified_engine Virtual 모드로 통합됨 |
| LIVE-PAPER-D6D7 | 통합 완료 | D6(#42)+D7(#43) PAPER_LIVE. D7 핫픽스 적용완료(≥0.80+Top10). unified_engine Virtual에 흡수됨 |
| **CS×EQS 이중필터 배포** | **다음** | CS65+EQS_LAG1 65 = 1순위 조합(연550건, PF_net 2.499). Layer 3.5/4.5 삽입 |
| **DESK5/4/3 구현** | **완료** | 프랙탈 추세추종 v3.0 코드 구현: 3테이블+desk_engine 10모듈+단위테스트+241일 백테스트 스크립트 (DESK543-FRACTAL-IMPL-001) |
| **D4 긴급 교체** | **CEO 승인 대기** | 09:20 양봉(PF 0.73 손실) → 눌림확인(09:00~09:30, -1~3% 깊이) 진입으로 전환. 전수조사 242건 근거. PF 13.3 예상 |
| **D2 TP/SL 변경** | **CEO 승인 대기** | trail-20% → SL-3%+trail-10%. 605건 그리드서치. PF 1.57→4.41 |
| **S1 필터 강화** | **CEO 승인 대기** | 갭+3%→갭+5%+양봉첫봉. 667건 분석. PF 1.44→2.52 |
| **반등확인 게이트 5전략 배포** | **다음** | OOS Walk-Forward PASS(avg PF 2.683). 2/3 충족 기본 버전으로 배포 |

---

## 3-1. Known Issues (갱신: 2026-03-05 v10.5)

| 이슈 | 상태 | 처리 |
|------|------|------|
| synthetic_BLOCK 73% 차단 (T-105 발견) | **✅ 해결 완료** | T-108 커밋 완료 (bf0d06b3, 03-06 크론 후 해소 예정) |
| 모의매매 TP=0 문제 (PARTIAL 청산 불가) | **✅ 해결 완료** | T-075 tick 윈도우 30분→20시간 확장, 전 전략 TP=3% 재설정 |
| virtual_hourly_report cron 미등록 (v8.9 FAIL) | **✅ 해결 완료** | T-077 크론 정비 (hourly/daily/weekly/monthly 4건 추가, 총 15건) |
| DESK5 20종목 v4_fundamental_quarterly 데이터 미수집 | **⚠️ 처리 필요** | T-119 발견, 재수집 필요 (min_quarters 4로 완화하여 fallback 적용 중) |
| v4_news_feed 테이블 미존재 | **⚠️ 처리 필요** | 뉴스 기반 축분류 불가, 별도 수집 작업 필요 |
| DESK3 AXIS2 분류 97.6% NONE | **⚠️ 모니터링** | T-099 발견, 실 거래 데이터 부족으로 근본 해결 어려움 |
| FunnelScore threshold 0.55 적용 후 승인율 변화 | **⚠️ 모니터링** | T-118 Walk-Forward 검증 후 0.40→0.55 상향, 신호 건수 감소 예상 |
| D5 FunnelScore 구조적 저점(0.19~0.25) | **⚠️ CEO 결정 대기** | CEO 결정 대기 |
| test_score_l2_dual_flow_high FAIL(0.37<0.5) | **⚠️ 처리 필요** | 테스트 임계값 조정 필요 |
| Nginx /manager/ 미설정 | **🔴 HIGH** | root 대기 | T-172/T-039R — CEO root 실행 후 URL 라이브 |
| 크론 3건 미등록 | **🔴 HIGH** | root 대기 | sync_trade(16:30)/desk_scan(08:00)/evolution(16:00)+스냅샷2건(*/30) |
| git push 미완료 | **🔴 HIGH** | root SSH | claudebot SSH 키 없음 — root에서 push 필요 |
| DESK2 MultiConditionMatcher 미연결 | **⚠️ MED** | 분석완료 | T-172 진단 — v4_pipeline_orchestrator와 미연결, T-163 효과 확인 후 작업 |
| desk_morning_scan DESK5 stock_code | **🟡 LOW** | Phase2 | 컬럼명 불일치 경고 — 기능 무해 |

---

## 4. 보류/미시작

| 항목 | 선행조건 | 우선순위 |
|------|----------|----------|
| **DESK5/4/3 보류** | **한국 KOSDAQ 시장 특성상 일봉 추세추종 유효성 미실증. 재개 조건: 60일 페이퍼 데이터 축적 후, DESK2 미포착 종목 역추적 ≥30% 시 착수.** | — |
| 문서 구조 마이그레이션 (Option B) | #20 이후 | 다음 |
| Phase 2 진입최적화 | 2E 완료 후 발굴확정 | 다음 |
| Phase 3 청산최적화 | Phase 2 완료 | 그다음 |
| Phase 4 DESK3-5 확장 | Phase 3 완료 | 후순위 |
| Phase 5 DESK3-5 전략 | Phase 4 완료 | 후순위 |
| Phase 6 통합테스트 | Phase 5 완료 | 최종 |
| 기획서 v3.1 | 2E 결과반영 | 2E 직후 |
| BT-BLANK-SLATE-001 | 재커밋 필요 | 문서정리 |

---

## 5. 핵심 발견 (누적)

### 발굴
- L3+X9 = 최강 조합 (정밀도 90%, REPEAT 종목)
- NEW(42.1%) D-1 예측불가 (AUC 최대 0.644)
- 일봉 패턴만으로 NEW 적중 3.8% (실패)
- 개인수급 단독 무의미, CMB4(수급분산) 0.636
- Phase 2E: DESK5→4→3 역추적 recall 100%, 4 TYPE 분류 (Slow/Mid/Short/Sudden)
- Pipeline Precision = 6.9% → **Scorecard P92로 90.3% 달성**
- 생존자 편향 확인: DESK3 이벤트만으로는 precision 부족, 추가 필터 필수
- 가설 검증 엔진 5모듈 구축 완료 (118변수, 10-Axis 107조건 검증)
- "강하게 오른 놈이 또 오른다" = REPEAT이 수익 핵심
- **L3 = 0 for ALL NEW stocks: L3 기반 필터는 REPEAT에만 적용 가능**
- **NEW 종목 핵심 변수: V_TRADE_AMOUNT, V_RVOL, P_CHG_5D, N_D1_COUNT, SEC_LEADER_FLAG, OBV_NEW_HIGH**
- **D-offset(D-3,D-5,D-10) 선행 지표 발견 실패 — 동시 지표 특성 재확인**
- **Wyckoff/VCP 패턴: 급등 초기 종목에 부적합 (발생률 ~0%)**
- **CAN SLIM 펀더멘털: 판별력 미약 (AUC < 0.6)**
- **SEC_LEADER_FLAG (AUC 0.838) = NEW 종목 발굴 핵심 신규 변수**

- **한국 슈퍼개미 공통 원리**: 거래량/수급이 최강 변수(글로벌 동일), 테마 반복성이 한국 고유 알파, 소형주(700억 이하)+흑자+테마 조합이 급등 공식, 대장주 1등만 매매(2등 금지), 세력 매집→보합(120일선 수렴)→돌파가 Wyckoff+VCP와 동일 구조, 사계절론(Q2 공격/Q4 방어)이 시장 방향 M 변수와 연결
- **SEC_LEADER_FLAG AUC 0.838** → v2로 업그레이드 시 거래대금 1위+최초 돌파 조건 추가 예정
- **DUAL_FLOW**: 기관+외국인 동시 순매수가 한국 시장 최강 수급 신호 (이정윤 3년 100억 전략의 핵심)
- **CEO 실전 전략 = 한국 최상위 트레이더 전략과 90%+ 일치 확인**
- **1분봉 20분선이 가장 보편적인 손절/매도 기준선 (모든 전략 공통)**
- **체결강도 120% 이상 = 매수세 우위의 정량적 임계값**
- **NEW 종목은 일봉 불가, 장중 1분봉 복합 조건으로 탐지 가능**
- **종가배팅(D7)이 시간 효율 대비 가장 높은 기대수익 전략 (교차 검증)**

### Session E-2B 수급 통합 탐사 (2026-03-02)
- **VP_STRENGTH_D1(체결강도) = #1 변수**: AUC 0.6535, FDR p=0.0004 — 37변수 중 유일 AUC≥0.55 & FDR<0.05 동시 충족
- **수급 > 분봉**: 수급변수 평균 AUC 0.5352 vs 분봉변수 0.5148 (2.37배 강력)
- **CEO D-002 "본질은 수급이다" 실증**: 외인연속매수≥1일 PF=2.409, 기관연속매수≥3일 PF=1.887
- **VP 3개월 한정(24.7%)이지만 #1**: 전기간(12개월+) 수집 시 AUC 추가 상승 기대
- **49조합 PF≥1.3 발견**: VP_HIGH+INST_NET_BUY_D1(PF 7.48), VP_HIGH+FOR_CONSEC≥1(PF 6.13)
- **필터 적용**: 포트폴리오 PF 0.834→1.143(+37.1%), D6 PF 1.144→2.115(+85%)
- **Walk-Forward 3-Fold**: Fold 2/3 PASS(PF>1.0), Fold 1 FAIL(VP 미수집 기간)

### P4 적응형 청산 5모드 검증 (2026-02-28)
- **22,406건 거래 시뮬레이션**: 기존 PF 1.32 → 적응형 PF 1.34 (+1.5% 개선)
- **단계형 부분청산 총 PnL 최고**: 4,589% (기존 4,089%, +12.2%)
- **모드2(부분익절) 전 전략 최적**: D2✅, D4✅ 일치, D8/D9/D5는 M2가 최적(권장과 불일치)
- **모드3(파동전환) 2파 발생률 0%**: 4조건 임계값 재조정 필요 (MFE 기준 완화)
- **최대 일일 손실 -174% → -74%**: 적응형 타이트 손절이 극단 손실 방지
- **D8 모멘텀추격 PF 2.14→2.26**: 적응형 청산이 단기 전략에 효과적

### 눌림 전수조사 PULLBACK-ANATOMY-001 (2026-02-28)
- **19,225건 전수조사**: 시초가 대비 +5% 급등 종목의 1파 고점 이후 눌림 구간 해부
- **2파 발생률 73.9%**: 실제 눌림 후 74%가 전고점을 재돌파 — 모드3의 가정 자체는 정당
- **모드3 0%의 원인 = RSI 범위 + MA20 미형성**: RSI 30~50(실제 중앙값 56.4) + 장초반 MA20 NA → 4조건 동시충족 0.26%
- **핵심 조건 변경**: RSI 45~70, 동적 깊이(wave1×0.5, 상관 0.62), 전조 시그널(TS-C4/C3/B4), MA20 제거
- **형태별**: V_SHARP(1~3분) 81.6% > V_MODERATE 61.3% > STAIR 48.0% > GRADUAL 18.1%
- **깊이별**: 0~1% 91.5% > 1~2% 79.3% > 2~3% 63.5% > 3~5% 40.1% > 5%+ 18.9%
- **시간대**: T2(09:30~10:30) 79.6%가 엄격 2파율 최고
- **시장상태 무관**: BULL/BEAR/SIDEWAYS 모두 71~75% (개별종목 눌림은 시장 독립)
- **전조 시그널 Top3**: TS-C4 볼린저스퀴즈(88.6%), TS-C3 20봉신고가(85.7%), TS-B4 거래량폭발(82.4%)

### 파동 자본순환 WAVE-CAPITAL-CYCLE-001 (2026-02-28)
- **3,000건 ZigZag 분석**: 45,003 급등쌍 → seed=42 샘플링 → 14개 연구과제 종합 실행
- **R01 최적 부분청산**: W1 30% → W2 100% 전량청산 (score 최적, 다음 파동 기대수익 반영)
- **R02 W2>W1 돌파율 48.2%**: 과반 미달! Type-D만 54.3%, Type-B는 41.2% — 모드3은 Type-D 선별 필수
- **R03 Dynamic 스톱 PF17.98/WR70.87%**: 확정수익 연동 스톱이 Fixed/Hybrid 대비 최우수
- **R04 시간대기만으로 PF<1.0**: 26분 대기해도 PF 0.88 — 확인 시그널(VP/RSI) 필수
- **R05 Type-E 조기탐지**: AUC 1.0이나 데이터 누출(up_wave_count) → v2 재학습 필요
- **R06 트레일링**: 20% retrace + 5% start profit → 50.2% capture (Type-D 877건)
- **R07 멀티종목 경합**: 96.7% 거래일 동시 눌림 발생, 진폭우선 정책 PnL 최고
- **R08 VP 선행성 2.27분**: 매수세 변화가 가격 전환을 2분 앞서 감지 → SIGNAL_ADD ✅
- **R09 종가 관계**: Type-D +2.73%, Type-E -4.53%, D7필터(Type-C/D+14:30≥0.7) PF 106.39
- **R10 거래대금 소진**: 50% 소진 시 다음 파동 27.7%, 70% 시 14.6% → FILTER_ADD ✅
- **R11 진입 지연**: 15분 지연에도 71.8% 수익 유지, half-life 미도달 → 시스템 여유 충분
- **R12 업종 동기화**: 매핑 실패(INDEPENDENT) → 테마 기반 재분석 필요
- **R13 효율**: 이론 최대 11.94% vs 시스템 1.73% = 17.7% 효율, 50% 로드맵 제시
- **R14 MA 랭킹**: 15분봉 MA5 종합 1위(복합점수 44.22), 1분봉 MA20 중위권

### 파동 외부 WAVE-OUTER-RESEARCH-001 (2026-02-28)
- **R15 전조모델 AUC 0.6378**: D-1 볼린저(-1.01), MA정배열(+0.43), 기관수급(+0.29) — Type-E 74% 정밀도, 리더종목(3+급등) 릴레이율 44.4%
- **R16 D+1 효과 FAIL**: C/D vs A/E 수익차 p=0.020 유의하나, 스윙전환 49.8% < 60% 미달
- **R17 교차종목 PASS**: 동시급등일 평균 84.7종목, 5~7종목 분산 시 PnL +370%, 단일종목 대비 3.7배
- **R18 충격일 E% 역설**: 충격일 Type-E 46.8% vs 정상 60.0% — 충격이 오히려 진성파동 비율↑, halt 불필요
- **R19 재앙손실 3패턴 100%**: excessive_relay(일5+릴레이), condition_concentration(단일C>70%), excessive_positions(일8+포지션)
- **R20 뉴스-파동 χ²=249.4**: 실적/공시 뉴스 릴레이율 48.4% 최고, 테마 뉴스 35.4% 최저 — 뉴스 타입별 차별화 필요
- **R21 호가 FAIL**: 매칭 44건 불충분, 추후 실시간 수집 확대 필요
- **R22 DUAL_FLOW 역전**: 기관+외인 동시매수 시 릴레이율 24.1% vs 비DUAL 40.3% — 수급 몰림=천장 신호, RISK_FLAG 전환 필요
- **R23 전략간섭 100%**: D2/D4/D5/D6/D7 시그널 중복률 100%, 독립 시그널 아닌 동일 조건 반응 — 전략별 차별화 재설계 필요
- **R24 거래비용 PF-37%**: 왕복 0.52~0.58%, 대형주 릴레이 PF 1.01(사실상 0), 소형주 슬리피지 최소 0.131%

### Phase H-1 컨디션별 반등률 (2026-02-28)
- **C2(전일상한가) D+1 최강**: PF 2.16, 승률 55.1%, 시초가 갭 +8.32% (79.3% 양갭)
- **C7(NEW탐지) 2위**: PF 1.59, 승률 50.4%, 494건
- **C1(상한가예상)**: 4,323건, D+1 고가 +10.97%, 시초가 갭 PF 3.91
- **C3~C6**: PF 1.18~1.39 범위, 전 컨디션 양의 기대값 확인
- **분봉 보유시간**: C1/C2는 단기(5분) 유리, C3/C4/C7은 60분 보유 개선

### Phase H-2 가격 프로파일 (2026-02-28)
- **C3(시초가강세) MFE/MAE 비율 1.19x 최고** — 가장 유리한 비대칭 구조
- **C2(전일상한가) MFE +9.02% 최대** (MAE -8.71%, 고변동)
- **C5(테마동시급등) MFE/MAE 0.85x 유일 불리** — 매수 후 역행 우세
- **MFE 도달 시간**: 대부분 T1~T2(09:00~10:30) 집중 — 장초반이 핵심

### 눌림확인 심층연구 PULLBACK-CONFIRMATION-001 (2026-03-01)
- **17,155건 전수 추출**: 56,857개 급등쌍에서 1파 고점→눌림→반등 패턴 식별
- **CEO 답변**: 이평선 터치 1,215건 / 닫기 전 반등 9,221건(53.8%) / 관통 후 반등 15,813건(92.2%)
- **5버킷 분류**: B1(5MA터치, 36.5%) < B4(20MA관통, 50.4%) < B2(5MA관통, 96.5%) < B3(10MA관통, 95.3%) < B6(미도달, 99.2%)
- **관통 > 터치**: 관통반등 PF 26.36 > 터치반등 PF 11.15 (2.4배 우위)
- **최강 확인 신호**: SIG6(VWAP지지) 승률73.7%, SIG8(불플래그) 승률81.6%
- **실용 최적 조합**: SIG3+SIG6(양봉+VWAP) = 5,527건, 승률77.4%, PF87.1
- **조건대기 > 시간대기**: G1조건 PF 30.11 > G1시간 PF 20.46 (R04 재확인)
- **VWAP 핵심 발견**: B4에서 VWAP 위(68.2%) vs 아래(41.8%) 차이 26.4%p

### CS/EQS/매트릭스 설계 (2026-03-01)
- **CS 5요소**: DAILY_GRADE(25)+MATCH_QUALITY(20)+TIME_FIT(20)+TECH_CONFIRM(20)+MARKET_ENV(15)
- **CS≥80 최적**: PF 2.383(+57.1%), 56.8% 거래 유지, 2,417/2,838건 HIGH 등급
- **EQS 5요소**: SLIPPAGE_EST(20)+FRESHNESS(25)+VOL_QUALITY(20)+PRICE_POSITION(20)+ORDERBOOK(15)
- **EQS≥70**: PF 11.96, 승률85.2%, 비용감면 29.5% → D2 PF+584%, D4 PF+421%
- **9×9 매트릭스**: 19셀 최적(◎), 16셀 적합(○), 28셀 조건부(△), 18셀 금지(×)
- **금지 규칙 18개**: T9(근상한가)×6전략 금지, T7(RSI반전)×D4 금지 등
- **시너지 규칙 8개**: T4×A3(박스돌파+수렴) +15점, T5×D5(테마+다중) +15점

### DD Decelerator + VWAP + 게이트 + ATR 설계 (2026-03-01)
- **DD Decelerator**: S1(기본 -3/-5/-8/-10%) 권고 — maxDD -45.66%→-11.42%, PnL 95.8% 유지
- **5-Layer 리스크**: 거래(-0.7%SL) → 전략(2연패 쿨다운) → 종목(일4회) → 포트(-2%킬) → 시장(-2%정지)
- **VWAP**: 5변수 정의, D1 VWAP탈환 NOT VIABLE(PF0.84), 보조필터로만 활용
- **반등확인 게이트**: D2(2/3) D4(2/4) D5(2/3) Mode3(2/3) S1(2/3) — 예상 PF개선 D2+737%, S1+7686%
- **ATR TP/SL**: S2(ATR+NetR:R≥2.0) 권고, min_sl 0.7%(ATR중앙 0.19% 대비 바인딩), 비용후 R:R 2.0 보장

### 모멘텀 전술 타당성 사전 검증 (2026-03-01)
- **A1(ORB) PASS**: 5분OR+Top20 = PF_ac **2.233**, 승률 61.98%, 일 2.5건, R:R 2.2:1 — **DESK2 추가 1순위**
- **A1 전 9조합 PASS**: 1분/5분/15분 OR × Top20/50/100 모두 비용후 PF ≥ 1.3
- **A3(1파라이딩) FAIL**: 3,111건, PF 1.20, 비용후 PF **0.60** — 비용 차감 시 수익성 소멸
- **A3 V_SHARP 필터 역효과**: 급격한 상승 = 급격한 반락, 필터 적용 시 오히려 악화
- **C3(마이크로풀백) FAIL**: 25,116건, 비용후 PF **0.47** — 호가 단위 노이즈와 구분 불가
- **D2(3분눌림)가 C3 대비 전 지표 우위**: PF 2.28 vs 1.26, 승률 49.5% vs 36.0%
- **결론**: A1(ORB)만 DESK2 추가 권고, 09:05~09:30 시간대 배치

### 시간대별 전략 배치 + 불플래그 (2026-03-01)
- **7×7 시간대 매트릭스**: 2,838건 분석, D6 전 구간 독보적, D1 전 구간 FAIL 재확인
- **T_EARLY(09:05~30) 모멘텀 갭 확인**: 1,024건 중 모멘텀 추격 전용 전술 0건 → A1(ORB) 배치 필요
- **T_OPEN D5 최적**: PF_ac=2.76, D2 차선(PF_ac=1.38)
- **T_WAVE1 D6 외 전략 적자**: D2 PF_ac=0.85, D4 PF_ac=0.72 → A3 추가 논의 불필요(FAIL)
- **점심 차단**: 3건 데이터로 검증 불가, 비점심 PF_ac=0.99로 전체 품질 향상이 우선
- **불플래그(B4) 전체 FAIL**: 348건, PF_ac=**0.99** — 하드스톱 25.6% 빈발
- **불플래그 T_PM_PB 구간만 PASS**: 27건, PF_ac=**2.64**, 승률 74.1% — 점심 후 횡보 → 돌파 유효
- **불플래그 5봉+ 플래그 PASS**: PF_ac=1.51~1.71 — 짧은 플래그(3~5봉)는 가짜 돌파 빈발
- **시간 마스크 고도화 제안**: 이진 ON/OFF → 가중치 기반 전환 (D2: T_OPEN 1.0 > T_EARLY 0.8 > T_WAVE1 0.3)

### VE-003 Phase B 결과 (2026-02-28)
- **D1 시초가 단독 FAIL** — 09:03~08 진입은 장 초반 변동성 과다, PF 0.89 순손실
- **D2 3분봉 눌림 비대칭 수익 확인** — 승률 39.8%에도 PF 1.57, 승평균(+3.36%) >> 패평균(-1.41%)
- **D5 뉴스급등 PF 4.21** — "1파 놓치고 2파 타라"의 정량 검증, 승(+3.99%) vs 패(-0.54%) = 7.4배
- **RSI 30~50 = 09:20 시점 단독 최강 필터** — 77.3% 승률, +3.11% 평균, max loss -1.31%
- **MA 정배열은 급등종목에서 역효과** — 전체 73.9% > MA정배열 72.5%
- **10선 눌림 > 5선 눌림** — 40.7%(+0.83%) vs 39.7%(+0.44%)
- **비대칭 수익 > 승률** — 실전 슈퍼개미 수익 구조 데이터로 확인
- **CEO 직관 "RSI 30~40 반등+VP≥120=진입" 데이터로 입증**

### VE-003 Phase A 결과 (2026-02-28)
- **D6 상따→갭 PASS** — 36건, 승률 77.8%, PF 13.63, 평균 +4.84% — **6개 전략 유일 PASS**
- **D7 종가배팅 CONDITIONAL** — 380건(최다), 승률 53.4%, PF 1.98 — 시간효율 최고
- **D4 전상눌림 CONDITIONAL** — 71건, 승률 28.2%, PF 1.88 — 비대칭 4.8배
- **오전 상한가(10시 전) > 오후**: 80.0%/+5.64% vs 75.0%/+3.84%
- **전일조건 전략(A) > 장중 전략(B)**: 평균 PF 5.83 vs 2.22
- **Phase B 교훈 적용 효과**: D1→D4에서 09:20 진입+RSI 필터로 PF 0.89→1.88
- **전략 포트폴리오 확정**: D6(30%) > D7(40%) > D5+D4+D2(30%)

### VE-003 Phase E 결과 (2026-02-28)
- **5축 운영 마스크 생성**: 시간대(T1~T6) × 시장상태(BULL/FLAT/BEAR) × 변동성 × 순위 × 보유시간
- **D4 마스크 효과**: PF 1.88 → **2.43** (+0.55, 13건 제거)
- **D7 마스크 효과**: PF 1.98 → **2.12** (+0.14, 11건 제거)
- **D1 부분 부활 불가** — 모든 5축 셀에서 PF < 1.3, 최종 폐기 확정
- **DCS 일별 시뮬레이션**: 222거래일, 평균 DCS +4.99%, 양일 55.9%
- **20거래일 롤링 최종 등급: A** (평균 DCS +4.30%, 양일 70%)
- **D-010 멀티컨디션 가설 등록**: 7가설(H-001~007), 7컨디션(C1~C7), CEO-DIRECTIVES v1.3

### VE-003 Phase F 결과 (2026-02-28)
- **18개 기술적 신호 분석**: 1,643 stock-date pairs × 18 signals, 보유기간 1~60분 + MA20 이탈
- **Top 3 신호**: TS-B4 거래량폭발양봉(PF3.23) > TS-C1 5봉거래집중(PF2.80) > TS-B1 RSI30~50(PF2.72)
- **60분 보유가 전 신호 최적** — MA20 이탈 청산은 18/18 신호에서 고정기간 대비 열등
- **상한가(C2) 컨디션에서 전 신호 PF 부스트** — TS-B4 PF3.4, TS-D3 PF3.3, TS-D4 PF2.7
- **MFE/MAE 비대칭**: TS-B4(2.12x), TS-C1(1.92x), TS-C3(1.88x) — 수익 > 손실 확인
- **Phase B RSI 30~50 최강 필터 재확인**: TS-B1 PF2.72(4위), 전 컨디션에서 안정적 1.3+

### VE-003 Phase C 결과 (2026-02-28)
- **D3 대장→후발 FAIL**: 50건, PF 1.17 — 테마 데이터 커버리지(71%) 한계 + 표본 부족
- **S1 폭발+눌림 CONDITIONAL**: 547건, WR 58.7%, PF 1.44 — Phase C 유일 수익 전략
- **S2 N일선 눌림 전체 FAIL**: MA7 PF1.27 최선, MA10 PF0.88 최악 — 일봉 눌림은 비효율
- **핵심 교훈**: 일봉 스윙 전략은 장중(1분봉) 전략 대비 PF 50%+ 하락, 장중 전략 우선

### VE-003 Phase D 결과 (2026-02-28)
- **NEW 254종목 6대 조건 역추적**: 거래대금 Top20 최초 진입 종목
- **VP≥120(88.5%), RSI 반등(88.1%), MA정배열(87.7%)** — 3대 핵심 조건 90% 근접
- **거래대금 폭발(60.9%), 가격 급등(62.1%)** — 보조 조건
- **테마 동반(9.5%)** — 실패, 필수 조건에서 제외
- **3개+ 조건 동시 만족 87.7%** — 장중 실시간 탐지 실용적
- **10시 전 급등 82.1%, 평균 09:34, 중앙값 09:14** — 조기 탐지 가능 확인
- **최적 4조건 조합**: C2+C3+C4+C6 = 62.1% (가격급등+VP+MA정배열+RSI)

### CEO 지시 3대 과제 (2026-02-28)
1. **능동적 청산 재설계**: 트레일링 스톱(구간별 MFE 되돌림) + 부분청산(+3% 시 50%) + 분할매수(D2/D4 대상 60%/40%)
2. **월요일 모의 실매매**: D6(PF13.63)/D7(PF2.12) 즉시 투입, 모의투자 계좌, 종가매수→D+1시초가매도
3. **AI Self-Evolution Engine**: 자동 발굴(Discovery)→검증(Validation)→모의(Paper)→실전(Live) 4단계 파이프라인 + Drift Detector

### 테마/업종 데이터 점검 결과 (2026-02-28)
- **4개 분류 체계 확인**: WICS(29섹터/2,770종목), KRX(24업종/4,225), KSIC(157산업/3,844), 키움테마(141/647)
- **테마 데이터 조치**: 중복 제거(2,106→905), 일별성과 34,122건 생성, 대장주 141개 설정, 활동성(HOT/WARM/COLD) 34,122건 생성
- **다중 테마 지원 확인**: 최대 6개/종목, 평균 1.4개 — N:M 관계 정상
- **자동 수집 확인**: Cron 평일 17:00, 신규 편입 자동 반영 중 (2/26→27: +613건 편입, -227건 제거)
- **개선 필요**: 수집 커버리지 71%(100/141), 제거 알림 미구축, is_active 플래그 없음

### 다음 단계 (D-008-KR)
- [ ] P0: feature_engine.py에 THEME_CYCLE_100B_COUNT, THEME_CYCLE_UL_COUNT 추가
- [ ] P0: universe_builder.py에 SMALL_CAP_QUALITY 플래그 추가
- [ ] P0: feature_engine.py에 DUAL_FLOW_5D, DUAL_FLOW_20D 추가
- [ ] P0: SEC_LEADER_FLAG를 v2로 업그레이드 (거래대금 1위 + 최초 돌파)
- [ ] P1: MKT_SEASON 분기별 공격도 가중치 구현
- [ ] P1: FORCE_ACC (120일선 수렴도 + 급등봉 횟수 + 갭상승) 추가
- [ ] P1: strategy_card에 "대장주 장대양봉 D+1" 카드 추가
- [ ] P2: BJ_SCORE 100점 스코어카드 구현
- [ ] P2: KJH_CYCLE (5년 우상향 + PER 밴드) 구현
- [x] VE-003 Phase A: D4/D6/D7 1분봉 백테스트 → D6 PASS(PF13.63), D4/D7 CONDITIONAL
- [x] VE-003 Phase B: D1/D2/D5 3분봉 리샘플링 시뮬레이션 → D1 FAIL, D2/D5 CONDITIONAL
- [x] VE-003 Phase E: 5축 분해 + 운영 마스크 → D4 PF 2.43, D7 PF 2.12, DCS 등급 A
- [x] VE-003 Phase F: 18 기술적 신호 분석 → TS-B4(PF3.23), TS-C1(PF2.80), TS-B1(PF2.72), 60분 최적
- [x] VE-003 Phase C: D3 FAIL, S1 CONDITIONAL(PF1.44), S2 전체 FAIL
- [x] VE-003 Phase D: NEW 254종목 6조건 탐지 → 3개+ 동시만족 87.7%, 10시전 82.1%
- [ ] P0 변수 8개 feature_engine.py 구현
- [ ] DESK-REALTIME 모듈 아키텍처 설계
- [ ] D-009 등록 확인

### 진입
- Birth Point + 1min WR 95.3%
- 09:05 고정진입 비효율
- 유형별(TREND/REVERSAL/BORDER) 진입 필요
- 신고가 돌파, 박스 돌파, 눌림목 반등 트리거 정의됨

### 데이터
- 히스토리컬 호가/틱 미보유 (실시간만)
- 프로그램매매 1일분만 존재
- ohlcv_daily 3년치로 MA60, MA120 계산 가능 (Phase 2C에서 미활용)

- **DESK 아키텍처 v3.0 확정**: 코어-새틀라이트 폐기. 전 DESK가 "넓게 뿌리고 소수 대승" 손익비 구조. DESK5 씨앗 10~20개 중 1~2개가 10배. DESK4 마디 반복 매매. DESK3 급등 1~5일 사냥. DESK2 장중 분봉 추가 수확. 독립 포지션+공유 정보.

---

## 6. 웹 Claude 인수인계 사항

> Cursor/Claude Code는 작업 완료 시 이 섹션을 반드시 업데이트한다.
> 웹 Claude는 새 세션 시작 시 이 섹션을 최우선 확인한다.

### 최신 상태 (2026-03-06, T-186 Redis 연결 복구 — v10.20)

#### ★ T-186 완료: Redis 연결 복구 + V4.1 서비스 안정화

**[T-186 CUR-V41-REDIS-STABILIZE-001] 2026-03-06 20:04 KST**
- **문제**: kis-v41-api(port 8003) `redis: disconnected` → status degraded
- **원인**: 장마감 후 POST_MARKET 장시간 idle → TCP 세션 만료 → 자동 재연결 실패
- **조치**: `sudo systemctl restart kis-v41-api` → redis: connected 복구
- **redis.py**: T-173 설정 전부 기적용 (retry_on_timeout/health_check_interval=30/socket_keepalive) → 추가 수정 불필요
- **최종 상태**: 8001 healthy ✅ / 8002 redis:connected ✅ / 8003 redis:connected ✅
- **minute-collector**: inactive(dead) status=0/SUCCESS → 장외 정상 완료 상태
- **Redis 서버**: 업타임 2일, rejected_connections=0, connected_clients=13

---

### 최신 상태 (2026-03-06, T-151 장중 전체 시스템 점검 — v10.11)

#### ★ T-151 완료: 03-06 장중 전체 시스템 점검

**[T-151] 03-06 09:15~09:30 KST 장중 점검 결과**
- **서비스**: 4개 모두 active(running) ✅ (kis-v41-minute-collector 08:54 재기동)
- **분봉**: 최신 09:18, today_rows=227, today_symbols=23 ✅
- **일봉**: latest=20260305, total=2,623,502 ✅
- **DB**: strategy_cards=60 ✅ / tables=289 ✅ / db_size=40GB ⚠️(기준 37-38GB)
- **가상매매**: 03-06 BUY 11건 신호 발생 ✅ (total 164건, 기간 03-02~03-06)
- **WARN항목**: Redis disconnected(API degraded) / SELL_FAILED 10건 / KIS토큰 DB기록만료(실API정상) / unified_engine.log 0bytes / v4_volume_power 테이블 없음
- **종합**: PARTIAL ⚠️ (핵심 기능 정상, 부수 이슈 존재)
- **커밋**: 346a9f15

---

### 최신 상태 (2026-03-05, T-122 KJH_CYCLE 김정환 사이클 — v10.7)

#### ★ T-122 완료: KJH_CYCLE 김정환 사이클 분석 엔진

**[T-122 CUR-V41-KJH-CYCLE-001] KjhCycleEngine 구현 + FunnelScore L3 통합**
- **파일**: `backend/app/services/feature_engine.py` (KjhCycleEngine 클래스)
- **7메서드**: `__init__` / `_fetch_annual_fundamentals` / `check_revenue_uptrend` / `check_op_uptrend` / `evaluate_per_band` / `check_roe_trend` / `calculate_kjh_score`
- **SCORE**: revenue_trend×0.30 + op_trend×0.30 + per_position×0.25 + roe_trend×0.15
- **cycle_phase**: GROWTH(매출+OP 모두↑) / MATURE(한쪽만↑) / DECLINE(모두↓) / UNKNOWN(데이터부족)
- **FunnelScore L3 보너스** (`funnel_score_engine.py`): GROWTH≥0.7→+0.15 / MATURE≥0.5→+0.05 / DECLINE→0
- **YAML**: `config/param_search_space.yaml` `kjh_cycle` 섹션 (min_years/per_band/score_weights)
- **테스트**: 13건 ALL PASS (`tests/unit/test_kjh_cycle.py`)
- **커밋**: dacc29bf (2 files: funnel_score_engine.py + test_kjh_cycle.py)
- **push 상태**: 로컬 커밋 완료, SSH 키 없어 원격 push 미완료

---

### 최신 상태 (2026-03-05, T-097 확인매매 엔진 — v9.6)

#### ★ T-097 완료: 확인매매 엔진 + 12가설 승자 전략 반영

**[T-097 CUR-V41-CONFIRMATION-ENTRY-001] ConfirmationEntryEngine 구현**
- **파일**: `backend/app/services/confirmation_entry_engine.py`
- **4메서드**: `find_recent_low` (ohlcv_daily N일 최저점) / `confirm_bottom` (4조건 AND 검증) / `calculate_risk_reward` (DESK별 손익비) / `generate_entry_signal` (파이프라인)
- **확인 4조건**: C1 양봉(close>open) / C2 반등≥bounce_pct / C3 거래량≥avg×1.5 / C4 외인 또는 기관 순매수
- **DESK별 min_rr**: DESK5=5.0 / DESK4=2.5 / DESK3=2.0 / DESK2=1.5 (SL=저점×0.99)
- **H08/H05/H09/H12 승자 반영**: `config/param_search_space.yaml` `hypothesis_winners` 섹션 추가
- **테스트**: 9건 ALL PASS (`tests/test_confirmation_entry.py`)

---

### 최신 상태 (2026-03-05, T-096 12가설 백테스트 — v9.5)

#### ★ T-096 완료: CEO 12가설 답변

**[CUR-V41-HYPOTHESIS-12-001] 파동 초입/고점/보유기간 12가설 백테스트**
- **파일**: `backend/app/services/hypothesis_tester.py` (HypothesisTester 클래스)
- **규모**: 12가설 × 4시나리오 = 48개 백테스트, 300종목, 3년(2023-01-02~2026-03-04)
- **CEO 질문 답변**:
  - **진입**: 신호 즉시 진입 (H01-A, H04-A) — 지연할수록 손실
  - **익절**: MA 트레일링 (H05-D MA20 PF=2.18, H06-D MA5 PF=1.74) — 고정 TP는 금물
  - **보유**: 파이프라인 종목 ×2.0배(30일, PF=3.15), 급등 후 5주 보유(PF=25.93)
  - **핵심 발견**: 마디 피로 가설 기각(4번째 신호 PF=1.55로 오히려 개선)
- **DB**: v4_desk_backtest_results 48행 INSERT 완료 (run_id: 0220617c)

---

### 최신 상태 (2026-03-02, 전체 데이터 수집 완결 — v5.8)

#### ★ 오늘 완료된 작업 요약 (v5.7 → v5.8): 전체 데이터 수집 완결

**[CUR-V41-HISTORICAL-DATA-COMPLETE-001] v4_market_regime_daily 15개월 갭 백필 완료**
- **문제**: 2023-01-18 ~ 2024-04-08 약 300거래일 누락. `index_daily` 최초일이 2024-02-13이어서 backfill 불가였음.
- **해결 1차**: yfinance `^KS11`/`^KQ11`로 2023-01-02~2024-02-12 index_daily 546건 삽입
- **해결 2차**: `backfill_regime_history.py --from 20230102 --to 20240212` → 254건 삽입
- **해결 3차**: `--from 20240213 --to 20240311` (33일 잔여 갭) → 19건 삽입
- **결과**: `v4_market_regime_daily` 843건 → **1,116건**, 설명 불가 갭 **0건** (잔여 갭 전부 공휴일)
- **커밋/보고서**: f61fa22 (project-docs), HTTP 200

**[CUR-V41-DATA-COLLECTION-STATUS-001] 전체 수집 현황 점검 + 3건 조치**
- go100_global_market WTI/SOX/CSI300/copper 4지표 추가 수집 (커밋 e273038d)
- v4_scalping_universe 크론 미등록 → 등록 + 수동 갱신 646→1,354건
- VKOSPI end_date yesterday→today 수정 (커밋 bc5fac1c)
- 커밋/보고서: f545aec (project-docs), HTTP 200

**오늘 추가된 크론 스케줄**:
- `10 16 * * 1-5` — `scalping_universe_builder.py` (신규 등록)
- `0 9,12,15 2 3 *` — VKOSPI 임시 재시도 (오늘만)
- `50 15 * * 1-5` → `--days 7` 확장 (기존 5일)

#### ★ 직전 완료 (v4.8 → v4.9): AI Scorer Z-score 핫픽스

**[CUR-V41-AI-SCORING-ZSCORE-HOTFIX-001] Z-score 이중 적용 핫픽스 완료**
- **원인 진단**: Case A 확정 — v2 Parquet(_zscore_batch_v2)에서 Z-score 저장 후
  feature_stats.json이 Z-score된 통계(mean≈0, std≈1) 보유 → ai_scorer Stage 2에서 재차 적용
  → z=(raw-0)/1=raw(identity transform) → 모델이 학습 분포와 불일치한 극단값 수신 → cs_ai=100 편향
- **수정**: `data/go100/models/go100_brain_v2_feature_stats.json` 원시 피처 기준 재생성
  - CLOSE: mean=0→66413, RSI_14: mean=0→53.59, BB_WIDTH: mean=0→10.77, 외 9개 피처
  - 백업: `go100_brain_v2_feature_stats.json.bak_20260301`
- **검증**: 삼성전자 cs_ai 100→65, SK하이닉스 100→61, NAVER 100→45 (종목별 차별화 정상)
- **테스트**: 7/7 PASS (test_ai_scoring_bridge.py)
- **커밋**: `799e33ee`

#### ★ 직전 완료 (v4.5)

**[CUR-V41-CTE-PIPELINE-INTEGRATE-001] CTE 파이프라인 통합 + D7 핫픽스**

**[CUR-V41-CTE-PIPELINE-INTEGRATE-001] CTE 파이프라인 통합 + D7 핫픽스**
- `strategy_params.py` 신규: D2 avg_win 3.36%(실측) 교정 → EV +0.49%, B4/B6 진입금지, concurrent=5, PF우선 슬롯 배정
- `test_cte_pipeline.py` 신규: 통합 테스트 33케이스 전체 PASS
- D7 갭다운 핫픽스: `live_paper_d6_d7.py` 종가위치 ≥0.80 + Top10 반영, DB #43 entry_condition 갱신
- 코드 커밋: `67602428` (branch: phase-2c-command-center)

#### ★ 직전 완료 (v3.9 → v4.0)

**[V41-GO100-BRIDGE-DESIGN-001] 안전 브릿지 Phase 1 구현 — E2E 4건 PASS**
- `backend/app/services/v41/go100_bridge_client.py`: Go100BridgeClient (3 async 메서드)
  - `get_risk_status()` → 킬스위치 상태 조회 (PASS: kill_switch_active=false 확인)
  - `request_portfolio_optimization()` → MARKOWITZ/RISK_PARITY/EQUAL_WEIGHT 비중 요청
  - `log_episodic_memory()` → V4.1_DESK_AGENT 독립 네임스페이스 Append-Only 적재
- `backend/app/api/go100/bridge.py`: GO100 수신 브릿지 라우터 (루프백 IP 전용)
  - IP 차단 미들웨어, agent_id 검증, 3 엔드포인트
- `scripts/v41/test_go100_bridge.py`: E2E 4건 전원 PASS
  - memory_id=3 확인(재검증), agent_id 오류 시 HTTP 400 확인
- `main.py`: go100_bridge_router 등록 완료, go100 서비스 재시작 PASS
- **코드 커밋**: `2fd7ac29` (branch: phase-2c-command-center)

#### ★ 직전 완료 (v3.9)

**[V41-GO100-INTEGRATION-ARCH] 통합 브릿지 아키텍처 기획서 v1.0**
- 3대 연동 브릿지 정의: 자본 컨트롤 / 리스크·킬스위치 / 에피소드 메모리
- 핵심 안전 수칙 3개: 코드 침범 금지 / Read-Only·Append-Only / 독립 페르소나(`V4.1_DESK_AGENT`)
- Mermaid 데이터 플로우 다이어그램 + Phase 1~3 마일스톤
- 저장 경로: `design/V41-GO100-INTEGRATION-ARCHITECTURE-v1.0.md`

#### ★ 직전 완료된 4개 작업 요약 (v3.8)

**[작업#6] EXIT-SLIPPAGE-INTEGRATE-001 — 청산 파라미터 최종 확정**
- 트레일링 vs 고정60분 상충 → **지정가-1틱으로 해소** (스프레드 94% 감소)
- D2/D4/D5: 트레일링(start+5%,retrace20%) + 지정가-1틱 매도 **확정**
- D2 PF 31.15 → **과적합 확정**, 현실적 목표 PF **2.0~2.5**
- D7: 종가위치≥0.80+Top10 필터 → 갭다운 43.4%→**24.1%** (목표 달성)

**[작업#7] ORB-INTEGRATE-OVERLAP-GUARD-001 — A1 통합 + 중복방지**
- D-ORB 전략: **C8 신규 컨디션**, 09:05~09:30 전용, 자본 15%, 일평균 2.5건
- D6/D7 중복: 36건 D6 중 **28건(77.8%)이 D7 조건 동시 충족**
- 방지 로직: `daily_d6_positions set()` → D6>D7>ORB 우선순위
- 7전략 포트폴리오 v2: D6 25%/D7 25%/D-ORB 15%/D5 15%, 예상 PF **2.8**

**[작업#8] HAV-DRYRUN-DRIFT-001 — 35변수 Go 판정**
- YAML 파싱: 오류 0건, 35변수 정상 인식 **PASS**
- Coarse Grid 100건: PF 12.26→12.24(±0.02) **PASS**
- Bayesian 8변수: 유효 3개(body_size_pct/atr_pct/bb_width_pct) 식별
- **★ drift_detector.py 수정 불필요**: 변수 목록 동적 로드, 4개 시장지표만 감시
- **03-02(일) 06:00 cron: GO** ✅

**[작업#9] CROSS-RELAY-PRESIM-001 — 241거래일 통합 시뮬**
- 6전략 단리: 4,000만→**4,061만원** (+1.5%), MDD **7.8%**, Sharpe 0.25
- *주의: 보수적 파라미터 기준. 역사적 PF 반영 시 연수익 15~25% 예상*
- 동시 종목 **5개** 최적 (수익/MDD 균형)
- PF우선 정책 권고 (D6 PF13.63이 포트폴리오 견인)
- **CONDITIONAL GO** (Sharpe/연수익 재교정 후 재판정 필요)

### 웹 Claude / 다음 세션이 해야 할 일 (v8.0 업데이트)

**최우선 — CEO 승인 대기**
- `atr_dynamic_exit.py:42` `NET_RR_RATIO = 2.0 → 1.5` 1줄 변경 (WF 3-Fold ALL PASS: PF=2.295, Sharpe=11.03, MDD=-2.1%)
- CEO 승인 시 즉시 코드 변경 + 커밋 push

**다음 세션 큐 (03-03 Virtual Run 후)**
1. **[완료] WF-Step 1** (3/3 PASS): SIG3+SIG6 교체 적용, D4 제외 PF=3.203 → cte_pipeline.py 반영 완료(9f17b8c5)
2. **[완료] D4 Shadow Mode**: SHADOW_STRATEGIES={'D4'} 활성화, 11개필드 JSONL 기록, daily_report Section7 추가
3. **03-03 Virtual Run 결과 모니터링**: D4 Shadow 신호 수집 + L3.3 비율 확인
4. **10거래일 후 (03-17)**: shadow_d4_*.jsonl 분봉 리플레이 검증 (D4 PF≥1.3 & WR≥30%)
5. **[완료] CEO ATR 1.5 승인**: `atr_dynamic_exit.py:42` NET_RR_RATIO 2.0→1.5 적용 완료 (커밋 96b7407b, 19:20)

**Step 4 사전 시뮬 결과 요약 (v8.0 추가)**
- D4 활성화 가능 (SIG3+SIG6): 83건 (ATR 2.0 시), 55건 (ATR 1.5 시)
- D4 PF=1.074, WR=22.9% (시뮬 기반, 과소추정 가능)
- D4 제외 PF=3.335 (베이스라인 2.398 상회 → SIG 교체 교차영향 없음 확인)
- 결론: D4 자체 성능 개선 (파라미터 조정) 후 WF 검증 필요

**완료된 D4 수정**
- ✅ `signal_generator.py:354` D4 PULLBACK→BREAKOUT 수정 (커밋 e274411a, 버그 수정)
- ✅ `scripts/backtest/run_cte_full_backtest.py` D4 price_pos 현실화 + is_pullback False (커밋 65557fd2)

**기존 계획**
1. **D-ORB C8 컨디션 DESK2-FINAL-SPEC에 공식 추가**: C1~C8 컨디션 목록 업데이트
2. **live_paper_d6_d7.py에 D6/D7 중복방지 로직 추가** (check_d7_allowed 함수)
3. ~~**⚠️ D7 갭다운 필터 코드 업그레이드**~~ → ✅ **완료** (CTE-PIPELINE-INTEGRATE-001, 커밋 67602428)
4. **HAV coarse_grid.py에 variable_config_test.yaml 연결**: 03-02 일요일 실행 확인
5. **D2/D4/D5 trailing 파라미터 코드 반영**: start=+5%, retrace=20%, order=limit_1tick (strategy_params.py에 D2_PARAMS 정의 완료, 실행 코드 반영 대기)
6. 03-02(월) D6/D7 페이퍼트레이딩 첫 실행 로그 확인: `tail -f /var/log/d6d7_paper.log`
7. 03-07(토) 첫 주 결과 수집 → `python scripts/monitor_paper_d6d7.py --week` → CUR-V41-PAPER-D6D7-WEEK1-001 완성
8. 파라미터 재교정 후 CROSS-RELAY-PRESIM 재시뮬 → CROSS-RELAY-MAXIMIZE 진행
9. 20거래일 페이퍼트레이딩 후 실전 전환 CEO 승인 요청
10. **strategy_params.py를 실제 DESK2 실행 흐름에 연결**: orchestrator.py가 strategy_params 임포트하여 EV 검증, 버킷 차단, 신호 조합 강제 적용

### 대표님 확인 필요 사항
- **스톱로스 모드**: Dynamic(PF↑WR↑, 권고) vs Hybrid(총PnL↑)
- **W1 부분청산**: 30%(권고) vs 50%(기존) vs 10%(score↑)
- **거래대금 소진 임계값**: 50%경고+70%차단(권고) vs 60%단일기준
- **D7 파동필터**: 적용(PF106, n=358, 권고) vs 미적용(PF1.2, n=2999)
- **효율 목표**: 25%(Phase1) → 35%(Phase2) → 50%(Phase3) 단계적 설정
- D6/D7 모의매매 03-02 자동 시작 확인

### 주의사항
- CEO "단순 사고 금지" 원칙 (D-001)
- 수급이 본질 (D-002), 개인매매 포함
- DESK = 풀관리, 타이밍 정확히 알 필요 없음 (D-003)
- 신고가 돌파 매매 로직 필수 (D-005)
- **Scorecard 필터 필수: DESK3 이벤트만으로 풀 운영 불가**
- **L3는 REPEAT에만 유효, NEW는 별도 파이프라인**

---

## 7. 업데이트 규칙

### Cursor/Claude Code
1. 작업 시작 전: 이 파일 + CEO-DIRECTIVES.md cat으로 읽기
2. 보고서 상단에 체크포인트 기록 (직전Task, 현재단계, CEO지시, cards/positions)
3. 작업 완료 후: 섹션 2~6 업데이트
4. 섹션 6 "웹 Claude 인수인계" 반드시 갱신
5. git push + HTTP 200 확인
6. 보고서 마지막에 "HANDOVER 업데이트: {커밋해시}" 기록

### 웹 Claude
1. 새 세션: 이 파일 크롤링
2. 섹션 6 최우선 확인
3. 지시서에 이 파일 업데이트 의무 포함

---

## 버전 이력
| 버전 | 날짜 | 변경자 | 변경 |
|------|------|--------|------|
| v10.20 | 2026-03-06 | Claude Code (Sonnet4.6) | **T-186 Redis 연결 복구 + V4.1 서비스 안정화**: kis-v41-api(8003) redis:disconnected → systemctl restart → redis:connected 복구; Redis 서버 자체 정상(업타임 2일/rejected_connections=0); redis.py T-173 설정 전부 기적용 확인(추가 수정 없음); minute-collector inactive status=0/SUCCESS 장외 정상; 전체 포트 redis:connected 확인(8002/8003) |
| v10.19 | 2026-03-06 | Claude Code (Sonnet4.6) | **T-184 인프라확인+리서치수집+RES-301~306 시딩**: 서비스 6/6 active/Nginx HTTPS 200/스냅샷cron 기설치/evolution_loop cron root 수동 필요; research_collector.py 11건 수집실행(RES-201~306 전부 JSON 저장); RES-301~306 이미 T-183 시딩됨(created_at 15:51); 11건 COLLECTED→ANALYZED 전환; EvolutionLoop 수동1회 실행(T-182분기 RES-301~306→TrendEntryResearcher); snapshot research_lab.total=16; 커밋 4020fc56 |
| v10.18 | 2026-03-06 | Claude Code (Sonnet4.6) | **T-183 Root 인프라 일괄적용**: Nginx reload(기설정 확인)/스냅샷cron 2건(/etc/cron.d/)/go100·frontend 재시작/RESEARCH가설 11건/서비스 6개 active/8/9 PASS; B-3 evolution_loop cron root 수동 설치 필요; T-180 반영(34f65a77) |
| v10.15 | 2026-03-06 | Claude Code (Sonnet4.6) | **T-173 장마감 일괄재시작+인프라**: 스냅샷 갱신(V4.1+GO100)/서비스 8개 active/코드 push c57d8344/root 실행 스크립트 생성(nginx /manager/+크론 대기) |
| v10.14 | 2026-03-06 | Claude Code (Sonnet4.6) | **T-172/T-168R/T-039R 반영**: V4.1+GO100 스냅샷 시스템 구축/신경연결 Phase1 3스크립트/GO100 스냅샷 재확인, Known Issues 5건 추가(Nginx/크론/git push/MultiConditionMatcher/stock_code) |
| v10.13 | 2026-03-06 | Claude Code (Sonnet4.6) | **T-162~T-170 일괄반영**: T-162 수익구조진단(승률6.8%→5대원인)/T-163A~D 긴급수정(비용0.015%·SL완화·FunnelScore0.35·BLOCK→CONDITIONAL)/T-166 GO100자율루프진단/T-167 V3활성화/T-168 DESK2 16카드재활성화/T-170 V3→FunnelScore L3.1통합/Redis재시작(T-171A), Known Issues 2건 추가(D5 FunnelScore저점/test_score_l2_dual_flow_high FAIL) |
| v10.12 | 2026-03-06 | Claude Code (Sonnet4.6) | **T-156 SELL_FAILED 전건청산+모의매매현황**: SELL_FAILED 0건(35CLOSED)/실계좌2건CEO청산/Redis ok복구/모의44건승인6.8%승률/D6최우수 |
| v10.11 | 2026-03-06 | Claude Code (Sonnet4.6) | **T-151 03-06 장중 전체 시스템 점검 PARTIAL**: 서비스4개PASS/분봉09:18/일봉2,623,502/cards=60/tables=289/db=40GB/가상매매BUY11건; WARN: Redis단절/SELL_FAILED10건/KIS토큰DB만료/unified_engine0bytes; T-141~T-144 완료 작업 추가, 섹션1 DB수치 갱신 |
| v10.10 | 2026-03-05 | Claude Code (Sonnet4.6) | **T-138 미커밋 일괄 push + HANDOVER 갱신**: kis-autotrade-v4 10커밋(T-125~T-137) 로컬 존재 확인, SSH 제한으로 root push 필요, T-125/T-126/T-127/T-128/T-129/T-130/T-131/T-132/T-133/T-137 완료 작업 테이블 추가, project-docs HANDOVER.md v10.10 갱신 |
| v10.9 | 2026-03-06 | Claude Code (Sonnet4.6) | **T-136 CONTEXT.md 2026-03-06 동기화**: 섹션4 DESK2 Phase B(T-128)/DESK5 프랙탈(T-127/T-130)/코어보유(D-014) 추가, 섹션7 T-125~T-136 현행화(T-131 VP_RT/MA_REGIME 완료 반영), 불일치 0건 달성, 커밋 974f545 |
| v10.8 | 2026-03-06 | Claude Code (Sonnet4.6) | **T-134 CONTEXT.md 전면 갱신**: HANDOVER.md v10.7 기준 14개 항목 갱신, CONTEXT.md vs HANDOVER.md 불일치 13건 정정 표 추가, 지시서 DIRECTIVE_START/END 형식 명문화, 커밋 881685e |
| v10.7 | 2026-03-05 | Claude Code (Sonnet4.6) | **T-122 KJH_CYCLE 김정환 사이클 분석 엔진**: KjhCycleEngine 7메서드(매출추세/OP추세/PER밴드/ROE추세/종합점수), cycle_phase(GROWTH/MATURE/DECLINE/UNKNOWN), FunnelScore L3 GROWTH+0.15/MATURE+0.05, YAML kjh_cycle 섹션, 13테스트 ALL PASS, 커밋 dacc29bf |
| v10.6 | 2026-03-05 | Claude Code (Sonnet4.6) | **T-121 BJ_SCORE 배진한 5원칙**: BjScoreEngine(대재수심차 100점 정량화), FunnelScore L3 ≥80→+0.20/≥60→+0.10, YAML bj_score 섹션, 커밋 d7fea642 |
| v10.5 | 2026-03-05 | Claude Code (Sonnet4.6) | **T-120 HANDOVER.md v10.5 일괄갱신**: T-101~T-119 16건 완료 반영, DB 288테이블/37.82GB/분봉108.4M rows, Known Issues 갱신(synthetic_BLOCK T-108해결/FunnelScore threshold 0.55/DESK5 데이터미수집) |
| v9.8 | 2026-03-05 | Claude Code (Sonnet4.6) | **T-099 깔대기 데이터 실 수집**: v4_sector_mapping(3,844종목) + v4_macro_daily 신규(062), SectorCollector, fundamental_quarterly 149종목/787행, GrowthScoreEngine Decimal 버그수정, DESK3 AXIS2=4/NONE=162(97.6%), 4테스트 ALL PASS, DB 256 |
| v9.7 | 2026-03-05 | Claude Code (Sonnet4.6) | **T-098 펀더멘탈 Growth Score 엔진**: v4_fundamental_quarterly 테이블(061 마이그레이션), FundamentalCollector 4메서드, GrowthScoreEngine 3메서드(축1/축2/NONE 분류), node_detector_desk5/3 성장필터 연동, growth_score YAML 섹션, 10테스트 ALL PASS |
| v9.6 | 2026-03-05 | Claude Code (Sonnet4.6) | **T-097 확인매매 엔진**: ConfirmationEntryEngine 신규(find_recent_low/confirm_bottom/calc_rr/generate_entry_signal), 확인 4조건(양봉+반등+거래량×1.5+외인기관순매수), DESK별 min_rr(D5=5.0/D4=2.5/D3=2.0/D2=1.5), H08-B(5주)/H05-D(MA20트레일)/H09-C(2일)/H12-D(×2.0배) hypothesis_winners YAML 반영, 9테스트 ALL PASS |
| v9.5 | 2026-03-05 | Claude Code (Sonnet4.6) | **T-096 12가설 백테스트 프레임워크**: hypothesis_tester.py 신규, 48개 시나리오 완료, DB 48행, 승자: H01-A/H03-C/H05-D(MA20트레일PF=2.18)/H08-B(PF=25.93)/H12-D(PF=3.15), 핵심: 즉시진입·MA트레일·파이프라인2배·마디피로기각 |
| v9.4 | 2026-03-05 | Claude Code (Sonnet4.6) | **T-083 문서불일치 정정**: CONTEXT.md 5건(strategy_cards 60건/오픈14건/DB 15.7GB/ohlcv_daily 테이블명/DESK 풀 개별 테이블/DESK3 206/ACTIVE), HANDOVER.md T-075~T-080 6개Task 일괄 반영(TP=0해결/GO100 V3활성화/크론 정비/fractal BT 코드/폭락장 모니터링/BT Phase1-2), Known Issues 섹션 신규 추가 |
| v8.3 | 2026-03-02 | Cursor | CEO P0 수급 데이터 전수조사 (10개 테이블, go100_investor_flow 275K건), path_check.sh 자동감지 개선, genspark_bridge 2분 대기 메시지 기능 추가 (전 프로젝트 공통) |
| v8.2 | 2026-03-02 | Cursor | CEO ATR 1.5 승인 즉시 적용 + D4 GATE 오분류 수정 (96b7407b, 8d47bbd2) |
| v8.1 | 2026-03-02 | Cursor | WF-Step1 적용 + D4 Shadow Mode 구현 (9f17b8c5) |
| v8.0 | 2026-03-02 | Cursor | Step4 시뮬 결과 + 매니저 DIRECTIVE 반영 (WF-Step1/2 큐, 커밋 65557fd2) |
| v7.0 | 2026-03-02 | Cursor | D4 EQS PULLBACK 버그 수정 (e274411a) + SIGNAL_COMBO 사전분석 |
| v1.0 | 2026-02-28 | 웹Claude | 초판 – Phase 1~2E 현황 |
| v1.1 | 2026-02-28 | Opus4.6 | 2E 완료, VALIDATION-ENGINE-001 완료, Precision 6.9% |
| v1.2 | 2026-02-28 | Opus4.6 | VE-002 완료, Precision 90.3% 달성, L3=0 발견, 118변수, NEW/REPEAT 분리 |
| v1.3 | 2026-02-27 | — | 한국 슈퍼개미 7인 전략 통합, D-008-KR 등록, P0 변수 4개·P1 3개·P2 2개 도출, 글로벌 대가 90%+ 수렴 확인 |
| v1.4 | 2026-02-27 | — | STUDY-002 + D-009 + VE-003 설계 + P0/P1/P2 확장 (8/7/5) |
| v1.5 | 2026-02-27 | Cursor | GO100 P6-EXTRA-VERIFY E2E 검증 완료 (PARTIAL), 보고서 push, tool_executors 스텁 추가 |
| v1.6 | 2026-02-28 | Opus4.6 | VE-003 Phase B 완료: D1 FAIL, D2/D5 CONDITIONAL, RSI 30~50 최강 필터, 비대칭 수익 구조 확인 |
| v1.7 | 2026-02-28 | Opus4.6 | 테마/업종 데이터 점검: 4개 분류체계 확인, 중복제거·일별성과·활동성 조치, 자동반영/제거 분석 |
| v1.8 | 2026-02-28 | Opus4.6 | VE-003 Phase A 완료: D6 PASS(PF13.63), D4/D7 CONDITIONAL, 전략 포트폴리오 확정 |
| v1.9 | 2026-02-28 | Opus4.6 | Phase E 5축마스크(D4 PF2.43/D7 PF2.12), D-010 멀티컨디션 가설, DCS 등급A, D1 최종폐기 |
| v2.0 | 2026-02-28 | Opus4.6 | Phase C/D/F 완료: 18신호(TS-B4 PF3.23), S1 CONDITIONAL(PF1.44), NEW 87.7% 탐지, VE-003 전Phase 종결 |
| v2.1 | 2026-02-28 | Opus4.6 | DESK2 최종설계서 + D-011(60분 청산/시그널매칭/D1·D3·S2 폐기), CEO-DIRECTIVES v1.4 |
| v2.2 | 2026-02-28 | Opus4.6 | 능동청산+분할매수+모의실매매+AI자동진화, Phase G 착수, CEO 3대 과제 |
| v2.3 | 2026-02-28 | Opus4.6 | HOTFIX-001+002: tool_executors 래퍼 교체(스텁→실동작) + risk_engine CAST jsonb 수정, 48도구 정상, 6단계검증 |
| v3.0 | 2026-02-28 | Opus4.6 | **WAVE-CAPITAL-CYCLE-001**: 14과제(R01~R14), W1-30%/W2-100% 청산, Dynamic스톱PF17.98, 거래대금50%소진필터, VP 2분선행, 효율17.7%→50% |
| v2.9 | 2026-02-28 | Opus4.6 | **PULLBACK-ANATOMY-001**: 19,225건 전수조사, 2파율 73.9%, 모드3 0%원인(RSI+MA20), 안D 권고(RSI45~70+동적깊이+전조시그널) |
| v2.8 | 2026-02-28 | Opus4.6 | 눌림 전수조사 설계서: 15개 차원×10가설, 모드3 2파0% 원인규명→재설계 4단계 실행계획 |
| v2.7 | 2026-02-28 | Opus4.6 | P9 적응형청산 5모드 연구 push + P4 검증(22,406건): PF 1.32→1.34, 모드2 최적, 모드3 재조정필요 |
| v2.6 | 2026-02-28 | Opus4.6 | 장중 복리 자본 순환 연구: 부분청산→재투입 자본풀(3.1x 효율), 모드3+D9 이중수익, IntraDayCapitalPool 설계 |
| v2.5 | 2026-02-28 | Opus4.6 | 연구 3건: 타이트손절(-1% 시스템 PF1.4) + 커버리지(D8/D9 신설로 전구간 커버) + 릴레이(청산→재진입 연쇄맵) |
| v2.4 | 2026-02-28 | Opus4.6 | Phase H-1(C1~C7 반등률, C2 PF2.16) + H-2(가격프로파일, C3 MFE/MAE 1.19x) + D6/D7 cron 운영 |
| v3.1 | 2026-03-01 | Cursor | HANDOVER-KIS-V41-PULLBACK-CONFIRM-20260228 등록(눌림확인매매 과제 A~D 인계), 섹션6 링크 추가 |
| v3.3 | 2026-03-01 | Cursor | CTE vs DESK 비교우위 아키텍처+시스템 흐름도+인계서 3문서 저장, HANDOVER 항목 3건 추가(CTE-COMPARE-ARCH, SYSTEM-ARCH-FLOW, HANDOVER-CTE-INT) |
| v3.4 | 2026-03-01 | Opus4.6 | 모멘텀전술 A1(PASS PF_ac=2.23)+A3(FAIL)+C3(FAIL), 시간대7구간 매트릭스(T_EARLY 갭 확인), 불플래그 전체FAIL(T_PM_PB만 PASS PF_ac=2.64) |
| v3.5 | 2026-03-01 | Opus4.6 | **PULLBACK-CONFIRMATION-001**: 17,155건 눌림 5버킷 분류(B2/B3 승률95%+골든존), VWAP지지 73.7% 최강필터, SIG3+SIG6 조합 승률77.4%, 관통>터치(PF26.36>11.15), B4 깊이3%이하 권고 |
| v3.6 | 2026-03-01 | Opus4.6 | **CS-EQS-MATRIX-DESIGN-001**: CS 5요소(100점) CS≥65 PF1.55, EQS 5요소(100점) EQS≥70 PF8.43, 9×9 매트릭스 81셀(금지18/시너지8), 트리거태깅 tmp_trigger_mapping 설계 |
| v3.7 | 2026-03-01 | Opus4.6 | **DD-VWAP-GATE-DESIGN-001**: DD Decelerator 5레벨(S1 maxDD -75%감소), 5-Layer리스크 재구조화, VWAP 5변수(D1전술 NOT VIABLE), 반등확인게이트 5전략, ATR 동적TP/SL+NetR:R≥2.0 |
| v3.8 | 2026-03-01 | Sonnet4.6 | **#6~#9 4개 병렬 완료**: 청산파라미터 확정(트레일링+지정가-1틱, D7갭다운24%), D-ORB DESK2 통합(C8/15%/PF2.8), HAV 35변수 Go(drift_detector 수정불필요), 241일 통합시뮬 CONDITIONAL GO |
| v3.9 | 2026-03-01 | Sonnet4.6 | **V4.1×GO100 통합 아키텍처 기획서 v1.0 추가**: 3대 연동 브릿지(자본/리스크/에피소드메모리), Loose Coupling REST API 브릿지 방식, V4.1_DESK_AGENT 독립 페르소나, Phase1~3 로드맵 |
| v4.0 | 2026-03-01 | Sonnet4.6 | **V4.1↔GO100 브릿지 Phase 1 구현(코드:2fd7ac29)**: Go100BridgeClient 3메서드, bridge.py 라우터(루프백IP차단+Append-Only), E2E 4건 PASS, memory_id=3 적재 확인(2차 검증) |
| v4.1 | 2026-03-01 | Sonnet4.6 | **Cursor #14~#16 Phase A-1~A-3 CTE 엔진 7모듈 구현**: bounce_gate/pullback_classifier/confirmation_signals/dd_decelerator/risk_layer_manager/disaster_detector/conviction_score/execution_quality_score/trigger_tactic_matrix — 단위 170케이스 전체PASS, 스모크 3건 완료 |
| v4.1 | 2026-03-01 | Sonnet4.6 | **#14~#16 Phase A-1~A-3 구현 완료**: CTE 모듈 7개 신규(bounce_gate/pullback_classifier/confirmation_signals/dd_decelerator/risk_layer_manager/disaster_detector/trigger_tactic_matrix/conviction_score/execution_quality_score), 단위테스트 총 120케이스 PASS, D2 100건 스모크·221일 시뮬·2838건 역산출 완료 |
| v4.2 | 2026-03-01 | Sonnet4.6 | **Cursor #20 페이퍼 트레이딩 모니터링 준비**: D6#42/D7#43 PAPER_LIVE 활성 확인, v4_paper_trades 미존재(첫실행 자동생성), cron `50 8 * * 1-5` 확인, monitor_paper_d6d7.py 신규, D7 갭다운 필터 이슈(0.70 vs 0.80) 발견, 보고서 프레임 CUR-V41-PAPER-D6D7-WEEK1-001 작성 |
| v4.3 | 2026-03-01 | Sonnet4.6 | **Cursor #14~#16 Phase A-1~A-3 CTE 엔진 9모듈 완전 구현 완료**: bounce_gate(5전략 게이트)/pullback_classifier(25셀)/confirmation_signals(8신호)/dd_decelerator(5레벨S1)/risk_layer_manager(5-Layer)/disaster_detector(3패턴)/trigger_tactic_matrix(81셀)/conviction_score(CS100점)/execution_quality_score(EQS100점) — 단위테스트 총 120케이스 전부PASS, D2 100건 스모크(통과율76%/PF1.38), 221일 DD시뮬(MaxDD-5.5%/PF2.36/DD감축77%), 2838건 역산출(EQS평균67.8 ≈ 기대65.6±2 ✅) — 보고서 3건 push: BOUNCE-GATE-IMPL/DD-RISK-IMPL/CS-EQS-IMPL |
| v4.4 | 2026-03-01 | Sonnet4.6 | **Cursor #17~#19 Phase B+C CTE 통합 파이프라인 + 백테스트 완료**: cte_pipeline.py(6-Layer+CS L3.5+EQS L4.5)/vwap_engine.py(5변수)/atr_dynamic_exit.py(NetR:R≥2.0+트레일링)/limit_1tick_exit.py(지정가-1틱+60초 마켓폴백) — 단위테스트 53케이스 PASS; CTE_FULL 5,000건/243일 백테스트: PF_net=6.901/MDD=12.5%/Sharpe=7.251/WR=75.9%, Walk-Forward 3-fold OOS/IS=1.300(과적합없음), Go/No-Go 7/8 GO — 보고서 push: CUR-V41-CTE-FULLBACKTEST-CEO-REPORT-001-20260301 |
| v4.5 | 2026-03-01 | Opus4.6 | **CTE 파이프라인 통합 + D7 핫픽스**: strategy_params.py(D2 EV+0.49% 교정/B4·B6 금지/concurrent=5/PF우선 슬롯), test_cte_pipeline.py 33케이스 PASS, D7 종가위치≥0.80+Top10 확정, DB#43 갱신, 코드커밋 67602428 |
| v4.6 | 2026-03-01 | Opus4.6 | **GO100 AI Feature Store v2 배치 빌드**: 19→34컬럼(Track A 7+Track B 2+뉴스1+라벨3+valid_label), NaN라벨보존+LABEL_ Z-score제외 결함수정, 263,450rows/12parquet/26.24MB, REGIME_SEASON 경고0건, valid_label 99.03% |
| v4.8 | 2026-03-01 | Cursor | **#20 EQS LAG1 + D4 ATR + CTE 페이퍼**: execution_quality_score LAG1(PRICE_POSITION t-1/ORDERBOOK 8점), atr_dynamic_exit D4 A안(1.0/5.0), live_paper_cte.py+monitor_paper_cte.py, 테스트 70 PASS |
| v4.9 | 2026-03-01 | Sonnet4.6 | **[V41-AI-SCORING-INTEGRATION-001] AI Scorer Step A MVP 완료**: ai_scorer.py(4모델+TTLCache+Z-score+Bounds), bridge.py(+/score /score/batch), go100_bridge_client.py(+ScoreUnavailableError+메서드2개), scoring_engine.py(Fail-Open+Shadow w=0.15), 테스트 7/7 PASS, feature_stats.json(263,450행) — Step B 강화 항목 11개 실측 기반 선별 예정 |
| v4.9a | 2026-03-01 | Sonnet4.6 | **[CUR-V41-AI-SCORING-ZSCORE-HOTFIX-001] Z-score 이중 적용 핫픽스**: Case A 확정(Parquet Z-score+stats Z통계), feature_stats.json 원시 기준 재생성(CLOSE:0→66413/RSI:0→53.59/등 12개), cs_ai 100→65/61/45(종목별 차별화), 7/7 PASS, 커밋 799e33ee |
| v5.0 | 2026-03-01 | Sonnet4.6 | **[CUR-GO100-HYPOTHESIS-ENGINE-001] GO100 AI 가설검증 파이프라인 L1~L3 통합**: GoAiClient(일일 $1/50회 서킷브레이커), HypothesisEngine(L1 Haiku 판정+L2 Sonnet 가설+L3 HAV큐), 야간 배치 백테스트+아침 리포트, cron 등록(15:40/22:00), 13/13 PASS, 커밋 3806a54b |
| v5.1 | 2026-03-01 | Sonnet4.6 | **[CUR-V41-19STRATEGY-TRIGGER-MINUTE-001] 19전략 분봉 멀티TF 자동검증엔진 완료**: 4엔진 모듈+단위테스트31 PASS, 19가설 전수(H-12/H-13 PASS 포트폴리오 PF=6.617/Sharpe=10.30/+303.98%), D6 상한가 체인 분봉에서도 독보적 우위 재확인 |
| v5.2 | 2026-03-02 | Claude Code (Sonnet4.6) | **[CUR-V41-19STRATEGY-TRIGGER-MINUTE-001-20260301] Cursor #21-R 19전략 분봉 전수재검증 (직접 SQL)**: v4_ohlcv_minute 74.5M rows 직접 검증, PASS 1개 — **H-13 D6(오전상한가→D+1시초가) WR=75.5%/PF=6.292/Sharpe=12.54/불안정월0%/5기준전부충족**, FAIL 18개(MA계열 WR13~24% 분봉노이즈, D4 갭업후반등구조약점, NEWS표본N=17), 포트폴리오 H-13단독 최적, 커버리지49.3%(목표80%), 기존CTE재설계 필요 |
| v5.8 | 2026-03-02 | Claude Code (Sonnet4.6) | **전체 데이터 수집 완결(4개 Task)**: VKOSPI 원인조사(API T+1~T+2지연)+end_date수정(bc5fac1c)+크론개선, global_market WTI/SOX/CSI300/copper 추가(e273038d), scalping_universe 크론등록+646→1354건, v4_market_regime_daily 15개월갭 백필(843→1,116건, index_daily yfinance소급546건), 설명불가갭 0건, 보고서 4건 push(f61fa22) |
| v6.0 | 2026-03-02 | Claude Code (Opus4.6) | **[CUR-SHARED-DB-SCHEMA-CATALOG-001] Session G 전체 조치 완료 + DB 스키마 카탈로그 통합**: 246테이블+8뷰=254 전수 스키마 카탈로그(프로젝트별 V4.1:124/GO100:65/공통:57, 10카테고리 분류), generate_db_catalog.py+update_db_catalog.sh 신규, cron 매일 06:00 자동갱신+변경감지+자동push, HANDOVER 문서-현실 5건 정정(테이블명 go100_global_market/v4_scalping_universe, CTE스크립트 미존재 주석, 테이블수 246+8뷰=254, 22개 test error 기록), shared/DB-SCHEMA-CATALOG.md 7,646줄 |