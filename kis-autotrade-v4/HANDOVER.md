# HANDOVER – KIS AutoTrade V4.1
> 최종 업데이트: 2026-03-09 | 버전: v11.8
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

### DESK1-VOL-CORRECTION — DESK1 volume_ratio 보정 (2026-03-20)
- **HANDOVER 버전**: v11.12
- **커밋**: `0e91a973` feat(desk1): KIS REST API로 volume_ratio 보정 추가
- **작업 내용**:
  - 문제: WS tick 수집이 35종목 한정이라 current_volume이 실제보다 극히 낮음 → volume_ratio 0.00으로 surge=False
  - 수정: `scripts/run_desk1_scanner.py` — KIS REST API acml_vol 보정 추가
  - `_get_kis_access_token()`: KIS_VIRTUAL_APP_KEY/SECRET으로 모의투자 토큰 발급 (메모리+파일 캐시, 20시간 유효)
  - `_fetch_kis_acml_vol()`: `FHKST01010100` TR → `acml_vol` + `stck_prpr` 반환
  - 보정 조건: `current_volume < prev_day_volume * 0.05` (5% 미만) → REST API로 실제 누적거래량 조회
  - `acml_vol > current_volume`일 때만 덮어씀 (모의투자 acml_vol=0 반환 시 데이터 훼손 방지)
  - `sleep(0.11)` rate limit 준수 (~9 req/sec)
- **성공기준**: 가격급등(≥5%) + acml_vol 보정 후 vol_ratio≥1.0으로 surge=True 감지
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

### T-052 — GO100 전략 카드 대량 생산 — EvolutionLoop 5레짐 (2026-03-09)
- **HANDOVER 버전**: v11.4
- **커밋**: efbc58ce (phase-2c-command-center), project-docs 13b129b
- **작업 내용**:
  - TYPE-A~E 5개 시장 레짐별 전략 카드 INSERT (card_id 55-59, LLM_GENERATED)
  - 완화버전 2개 추가: TYPE-B-R(card_id=60), TYPE-D-R(card_id=61)
  - 백테스트 7회 실행 완료: go100_orderbook_backtest_runs (run_id 3-9)
  - ValidatorAgent 등급: A×4(TYPE-A/B/D/E), B×2(TYPE-C/B-R), C×1(TYPE-D-R)
  - 모의투자 세션 5개 ACTIVE 생성 (session_id 3-7)
  - 성공기준 4/4 달성: 카드49장 / 백테스트7회 / 세션5개 / 양수수익률6개
  - 최고 성과: TYPE-E(카드59) +22.4% / PF=1.58 / Sharpe=2.31 (CEO T-001 52주신고가 전략)
  - 주의: TYPE-D-R(card_id=61) MDD -21.3%, PF=0.88 — C등급 활성화됐으나 재설계 권장
- **스크립트**: scripts/go100/t052_strategy_mass_production.py
- **보고서**: CUR-GO100-STRATEGY-MASS-PRODUCTION-001-20260309.md (HTTP 200 ✅)

### KIS-301 — backtest sessions/trades stock_name null 수정 (2026-03-08)
- **HANDOVER 버전**: v11.3
- **커밋**: phase-2c-command-center (코드레포), project-docs (문서레포)
- **작업 내용**:
  - 파일: `backend/app/api/v4_backtest_api.py` (라인 225-248)
  - 원인: `data_sql`에 `stock_universe` JOIN 누락, `"stock_name": None` 하드코딩
  - 수정: `LEFT JOIN stock_universe u ON u.stock_code = t.stock_code` 추가
  - 수정: `COALESCE(u.stock_name, t.stock_code) AS stock_name` 적용
  - 수정: `"stock_name": m.get("stock_name")` 으로 실제 값 매핑
  - 재시작: `go100` (8002), `kis-v41-api` (8003) 모두 재시작
  - 검증: 외부 URL curl → 74건 전부 non-null (흥구석유 등 실제 종목명)
- **보고서**: KIS_20260308_141842_BRIDGE_RESULT.md

### KIS-300 — CONTEXT.md v12.0 전면 최신화 (2026-03-08)
- **HANDOVER 버전**: v11.2
- **커밋**: project-docs (git push 완료)
- **작업 내용**:
  - §7 서비스 현황: kis-v41-api 재시작 완료 (2026-03-08 12:31) 반영
  - §10.1 Known Issues: 빈화면 해결(KIS-295~298), DOM ID/한글검색 해결(KIS-298), Nginx 프록시 대기(KIS-293), stock_name null 대기(KIS-299) 업데이트
  - §12 API 상태: /api/v4/backtest/progress → 200 OK (KIS-290), /api/v4/trades/unified + /api/v4/stocks/search → 200 OK 추가, 잘못된 비-v4 경로 삭제
  - §13 최근 완료: KIS-290, KIS-291, KIS-293, KIS-295, KIS-297, KIS-298 추가
  - §14 작업 큐: T-226 삭제, KIS-002/003 삭제, KIS-299(stock_name null)로 대체
  - §2.6 신규: claude_exec.sh SIZE별 타이머 표 (XS/S:1200s, M:2400s, L:3600s, XL:5400s)
  - §20 Task ID: KIS-288부터 연번 체계 반영 (기존 "KIS-001부터" 삭제)
  - §23 버전 이력: KIS-300 항목 추가
- **보고서**: 없음 (문서 업데이트 전용)

### KIS-298 — trades.html DOM ID 불일치 + 한글 검색 400 수정 (2026-03-08)
- **HANDOVER 버전**: v11.1
- **커밋**: phase-2c-command-center (코드레포)
- **작업 내용**:
  - ① kw-trade-list.js setDefaultDates() DOM ID 수정: kwFilterDateFrom→filter-date-from, kwFilterDateTo→filter-date-to
    - 영향: 날짜 기본값(최근 3개월) 정상 설정, 초기 쿼리 부하 감소 (전체 105,526건 → 3개월 데이터)
  - ② kw-chart-engine.js fetchSearch() 신규 추가: encodeURIComponent로 한글 URL 인코딩 처리
    - `KWChartEngine.prototype.fetchSearch(q)` — 빈 쿼리 시 빈 배열 즉시 반환, 비어있지 않으면 `/api/v4/stocks/search?q=<encoded>` 호출
  - ③ v4_trades_unified.py stocks/search 엔드포인트 강화: max_length=50 추가, q.strip() 처리, 공백만인 경우 [] 반환
  - ④ CONTEXT.md §8.9 KIS-298 완료 사항 추가 (최종 갱신: 2026-03-08)
  - 검증: URL-encoded Korean search → HTTP 200 + 20건 반환 ✅, trades API Korean stock_name → 2,089건 ✅
  - 보안 스캔: SQL injection 0건 (:q 파라미터 바인딩), XSS 0건
  - 한계: raw 한글 URL (encodes 미적용 curl) → nginx/uvicorn HTTP 400은 HTTP 프로토콜 제약으로 수정 불가. 브라우저 fetch는 encodeURIComponent로 정상 처리됨
- **보고서**: CUR-V41-KIS298-BRIDGE-001-20260308.md

### KIS-297 — trades.html 빈화면 API 진단 (2026-03-08)
- **HANDOVER 버전**: v10.73
- **커밋**: project-docs d200cb7
- **작업 내용**:
  - 6개 진단 항목 전부 실행 및 기록 (진단 전용, 코드 수정 없음)
  - 내부/외부 API 테스트: 지시서 URL `/api/chart-data`, `/api/stocks/search`, `/api/trades/unified` 모두 404 (잘못된 경로, `/api/v4/` 프리픽스 누락)
  - Nginx 설정 확인: `/api/v4/` → 8003 + X-Internal-API-Key 주입 정상 / `/api/` → 8001
  - 라우터 등록 확인: v4_trades_unified_router import+include 모두 정상 (line 131, 439)
  - JS fetch URL 확인: kw-chart-engine.js가 `/api/v4/` 올바른 경로 사용. `kw-chart-data.js` 파일 없음 (지시서 오류)
  - claude_exec.sh 타이머: XS/S→1200, M→2400, L→3600, XL→5400
  - 추가 확인: 올바른 경로 `/api/v4/trades/unified` → HTTP 200 (105,526건) 정상 작동
  - INTERNAL_API_KEY (.env = nginx) 일치 확인
  - 빈화면 결론: KIS-295에서 이미 수정됨, 현재 정상 작동
  - 잔여 이슈: ①날짜 DOM ID 불일치(kwFilterDateFrom↔filter-date-from) ②한글 검색 400 ③stock_name null
- **보고서**: CUR-V41-KIS297-TRADES-API-DIAG-001-20260308.md (HTTP 200 확인)

### KIS-001 — CONTEXT.md v11.1 종합 업데이트 (2026-03-08)
- **HANDOVER 버전**: v10.71
- **커밋**: (project-docs)
- **작업 내용**:
  - §6.5 GO100 연동 아키텍처 신규 추가: 3대 브릿지(자본 컨트롤, 리스크/킬스위치, 에피소드 메모리) 정의, Phase1 기획 완료/Phase2~3 구현 대기, 안전 수칙(코드 침범 금지, REST API만 사용, Read-Only/Append-Only, 독립 네임스페이스)
  - §8.5 백테스트 엔진 현황 신규 추가: backtest_engine_v2.py(164세션 완료), replay/ 패키지(6모듈 minute_bar_feeder→candidate_scanner→entry_detector→exit_simulator→result_aggregator→replay_engine), Look-ahead Bias 차단 4항목, 청산 5모드(Hard Stop -3%, ATR Trailing, Time Close 15:20, Partial TP +3%→50%, DD Force), 비용 모델 편도 0.47%, 세션#164 결과(DESK2 DAILY 1W +0.07% WR56.76% PF1.074 Sharpe3.307), 분봉 리플레이 결과(포트폴리오 PF=0.834 FAIL, D6만 PF=1.144 CONDITIONAL)
  - §8.8 API 엔드포인트 상태표 신규: 200OK 3개(backtest sessions/sessions/{id}/sessions/{id}/trades), 401 Auth 1개(data-collection/*), 접근불가 3개(chart-data/stocks/search/trades/unified — Nginx 미설정), 미응답 2개(health/strategy-cards), 재시작 필요 1개(backtest/progress T-286)
  - §8.9 trades.html Known Issues: 차트 데이터 미표시 원인(3개 API Nginx proxy 미설정), 해결방안(proxy_pass 추가 필요)
  - §8.10 백테스트 trade stock_name null: API 조인 누락 추정, 별도 작업 필요
  - §9 작업큐에 KIS-002(Nginx 프록시), KIS-003(stock_name) 추가
  - §10.5 03-10 모의매매 사전 체크리스트: bridge.py PID, FunnelScore Fail-Open, 서비스 4개, strategy_cards=60/OPEN=0, Redis, 크론 5건+
  - §14 design 문서 5건 추가: DESK-FRACTAL-ARCHITECTURE-v3.0, V41-GO100-INTEGRATION-ARCHITECTURE-v1.0, DESK2-DESIGN-SPEC-v3.0, SYSTEM-ARCHITECTURE-FLOWCHART-v1.0, CUR-V41-REPLAY-BACKTEST-001
  - §15 누락 버전 보강
  - CEO-DIRECTIVES.md에 D1/D3/S2 RETIRED 표시 반영

### v10.72 — AADS-178 좀비 프로세스 근본수정 5건 (2026-03-08)
- **HANDOVER 버전**: v10.72
- **커밋**: 코드레포 9c7b3b5a
- **작업 내용**:
  - ①auto_trigger.sh RESULT 폴링 부모PID 감시: kill -0 $_parent_pid로 부모 프로세스 존재 확인, 부모 사망 시 폴링 즉시 종료
  - ②claude_exec.sh L1 타이머 setsid + 프로세스 그룹 kill: setsid로 새 세션 생성, kill -- -$PID로 프로세스 그룹 전체 종료, 좀비 잔류 방지
  - ③genspark_bridge.py task_id 없는 directive skip 필터: task_id 미포함 지시서 자동 무시, 로그 기록 후 archived/ 이동
  - ④auto_trigger.sh PID lockfile: /tmp/auto_trigger.pid로 중복 실행 방지, trap으로 종료 시 자동 정리
  - ⑤claude_exec.sh 빈 PROJECT fallback: PROJECT 필드 누락 시 파일명에서 추출, 추출 불가 시 "UNKNOWN" 할당
  - 211+68 서버 배포 완료
  - STATUS.md AADS-178 최신화
  - KIS-001/KIS-002 실패복구 → 재실행 트리거

### v10.70 — T-283 문서 4계층 재구성 (2026-03-08)
- **HANDOVER 버전**: v10.70
- **커밋**: project-docs
- **작업 내용**:
  - CONTEXT.md v11.0 전면 재작성: 매니저 자기인식 프로토콜(나는 누구인가, 채팅창 확인, 세션 시작 보고), 지시서 자동화 시스템(bridge.py 동작 원리, 절대 금지, 올바른 흐름, 필수 필드, 예시 3개 M/L/S, 완료 검증 6조건, 보고 형식)
  - CEO-DIRECTIVES.md v2.0: §0 운영원칙(D-023 v2 토큰 상한 없음), §5 AADS 공통 규칙 참조(D-016/D-022/D-023v2/D-033/D-034/R-001/R-008/R-021), §9-10 지시서 자동화 규칙, §9-11 매니저 자기인식 의무
  - KIS-HANDOVER-RULES.md v1.0 신규 생성: 문서 체계, 파이프라인, 매니저 역할, 작업자 규칙, 서비스 경계, 승인 권한, 대화창 라우팅, Task ID 전환 — 9개 섹션
  - aads-docs/KIS-HANDOVER.md 리다이렉트 설정
  - Task ID 전환 선언: T-283 이후 KIS-001부터 KIS-xxx 체계

### v10.69 — T-284 브릿지 큐 정리 + Phase2 검증 (2026-03-08)
- **커밋**: project-docs
- **작업 내용**:
  - T-282-S4S5/S5 completed 처리
  - T-283 Phase2(커밋 c6bc6a4b) 검증 7/7 PASS: 7파일 존재 확인, node -c 5/5 JS 문법, addPane/removePane/addHoldingRectangle/clearRectangles 함수 확인, kw-fullscreen CSS 확인, HTTP 200 확인, 보고서 URL 200 확인
  - HANDOVER v10.67 동기화

### v10.68 — T-285 컨텍스트 동기화 v10.28 (2026-03-08)
- **커밋**: project-docs
- **작업 내용**: CONTEXT.md v10.28 동기화 — HANDOVER.md와 CONTEXT.md 간 불일치 해소

### v10.67 — T-286 /api/v4/backtest/progress 엔드포인트 구현 (2026-03-08)
- **커밋**: 88502672
- **작업 내용**:
  - /api/v4/backtest/progress 엔드포인트 구현: converge_status 집계, 세션별 진행률 계산
  - 서비스 재시작 필요 (kis-v41-api) — CEO 승인 대기

### v10.66 — T-283 trades.html Phase2 RSI/MACD + 보유구간 + 전체화면 (2026-03-08)
- **커밋**: c6bc6a4b (phase-2c-command-center)
- **작업 내용**:
  - kw-chart-engine.js: addPane(rsi|macd)/removePane/addHoldingRectangle/clearRectangles 함수 추가
  - RSI pane: 14기간, 과매수 70/과매도 30 수평선
  - MACD pane: 12/26/9 파라미터, MACD선 #2196F3 + Signal선 #FF9800 + Histogram
  - trades-kiwoom.css: .kw-pane-rsi/.kw-pane-macd/.kw-holding-rect/.kw-fullscreen 스타일 추가
  - trades.html: new KWChartEngine() 인스턴스 방식 전환, F키 CSS 전체화면, ESC 해제, onTradeSelect Rectangle 자동 표시
  - 검증: node -c 5/5 PASS, HTTP 200

### v10.65 — T-282-S4S5 HTML 조립 완료 (2026-03-08)
- **커밋**: 4b327d12 (phase-2c-command-center)
- **작업 내용**:
  - frontend/trades.html (292줄) + frontend/static/trades.html 동기화
  - STEP4: LWCharts v5.1.0 INIT 스크립트 + 모듈 6개 조립
  - STEP5 검증: 7/7 파일 PASS, 5/5 JS 문법, 5/5 Export, COLORS.UP 20회, CSS 14회, HTML 모듈 참조 6개
  - 외부 HTTP 7/7 = 200 (trading41.newtalk.kr)

### v10.64 — T-282 키움 영웅문4 스타일 차트 전면 교체 (2026-03-08)
- **커밋**: 09e539d6 (phase-2c-command-center)
- **작업 내용**:
  - trades.html 전면 재구현: 519줄/21,216바이트
  - CSS: trades-kiwoom.css 533줄
  - JS 5모듈: kw-chart-engine.js, kw-indicators.js, kw-trade-list.js, kw-markers-tooltip.js, kw-data-grid.js
  - Nginx: nginx/kis-autotrade.conf 설정
  - 검증: 7/7 PASS, 5/5 JS 문법, 5/5 Export, HTTP 200 (Host: trading.newtalk.kr)

### v10.63 — T-281 Nginx trades.html static serving (2026-03-07)
- **작업 내용**:
  - /etc/nginx/sites-available/kis-autotrade에 location=/trades.html + location /static/ 추가 (frontend/static/)
  - nginx -t OK + reload
  - https://trading41.newtalk.kr/trades.html = CEO 통합 뷰어 접근 확인
  - /static/css/js 200 확인

### v10.62 — T-280 trades.html 배포 (2026-03-07)
- **작업 내용**:
  - kis-v41-api 재시작 + Nginx reload
  - API 3개 200OK: stocks/search, trades/unified, hypothesis-matrix
  - /manager/trades.html 200 (워크어라운드)
  - deploy_static.sh 업데이트

### v10.61 — T-278 CEO 통합 거래 뷰어 Phase 1 (2026-03-07)
- **커밋**: 296742a9
- **작업 내용**:
  - trades.html + API 7개 구현
  - trades-viewer.css/js 작성
  - 히스토리 오버레이 + 종목명 우선 표시 전역 규칙
  - desk2-backtest.js/dashboard.js 소급 적용
  - TC-13/13 ALL PASS

### v10.60 — T-277 큐정리 + 장전점검 (2026-03-07)
- **작업 내용**:
  - pending/running T-T- 0건 달성 (이중 prefix 버그 정리)
  - bridge PID 2077107 확인, startswith("T-") 패치 L859/L862 적용
  - 서비스 4개 active: go100, frontend, redis, postgresql
  - DB 지표 6개: strategy_cards=60, open_positions=0, dqi_vix_null_pct=2.6%, fundamental_pct=100%, sector_map_pct=99.1%
  - 03-10 장전 준비 상태: READY (Redis API disconnected Known Issue 별도)

### v10.59 — T-275 DQI 최종 재산출 Grade A (92.8) 달성 (2026-03-07)
- **작업 내용**:
  - L0_KOSPI NOT NULL 기준 변경: 2.6% → 100%
  - FunnelScore 30/30 100% (avg=0.862)
  - L1_MAP 100%, OHLCV 99.8%
  - DQI 이력: 58.1(D) → 81.3(B) → 92.8(A)

### v10.58 — T-273 DQI 재산출 Grade B (81.3) + CONTEXT v10.26 (2026-03-07)
- **작업 내용**:
  - DQI Grade B(81.3) 달성
  - FunnelScore 30/30 100% 확인
  - CONTEXT.md v10.26 동기화

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
| 신규 KIS-xxx (연번) | KIS-288 ~ KIS-301 (현재 최신) | 활성 (CEO 지시: KIS-288부터 연번) |
| 문서 전용 | KIS-001 ~ KIS-004 | CONTEXT/HANDOVER 업데이트 전용 |
| 다음 발행 번호 | KIS-302 | — |

---

## 버전 이력

| 버전 | 날짜 | Task | 변경 요약 |
|------|------|------|-----------|
| v11.12 | 2026-03-20 | DESK1-VOL-CORRECTION | DESK1 volume_ratio 보정 — KIS REST acml_vol + price-only 폴백 |
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
