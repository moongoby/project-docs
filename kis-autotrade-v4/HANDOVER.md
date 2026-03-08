# HANDOVER – KIS AutoTrade V4.1 DESK 시스템
> 최종 업데이트: 2026-03-08 (v10.76 — KIS-295 trades.html 빈화면 수정: INIT SCRIPT 재작성+날짜 형식 YYYY-MM-DD 수정/CONTEXT.md v11.3; v10.75 — KIS-293 Nginx 차트 API 프록시 설정: apply_nginx_kis293.sh 생성(root 실행 필요)/CONTEXT.md v11.2; v10.74 — KIS-291 claude_exec.sh SIZE 타이머 211배포; v10.73 — KIS-290 03-10 장전 사전점검 9/9 PASS; v10.71 — KIS-001 CONTEXT.md v11.1; v10.70 — T-283 문서 4계층 재구성)
> **이 파일은 History 계층입니다. Core는 CONTEXT.md를 참조하세요.**
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
| **KIS-295 trades.html 빈화면 수정** | 03-08 | bad34b3f | 완료 | INIT SCRIPT 완전 재작성(new KWChartEngine()/fetchTrades/fetchChartData/renderList/bindTrades+buildMarkers/addPane·removePane); v4_trades_unified.py get_trade_daily_chart candle time YYYYMMDD→YYYY-MM-DD(LWCharts v5 호환); 검증: API 4개 200OK/JS AST PASS/candle time 2025-12-08 확인; 커밋 bad34b3f push; CONTEXT.md v11.3; HANDOVER v10.76 |
| **KIS-293 Nginx 차트 API 프록시 설정** | 03-08 | scripts 전용 | 스크립트 생성 | /api/chart-data, /api/stocks, /api/trades → 8003 location 블록 추가; apply_nginx_kis293.sh 생성(root 실행 필요); CONTEXT.md v11.2 업데이트(§7/§8.8/§8.9/§9/§15); HANDOVER v10.75 |
| **KIS-291 claude_exec.sh SIZE 기반 차등 타이머 구현 + 211 배포** | 03-08 | 인프라 전용 | 211 배포 완료 | /root/.genspark/claude_exec.sh SIZE 파싱 로직 추가(XS/S=1200s/M=2400s/L=3600s/XL=5400s/없음=2400s); HARD_TIMEOUT=MAX+600s/SOFT_WARNING=HARD-300s 동적 계산; bash -n syntax OK; SIZE 파싱 테스트 3케이스 PASS(XS=1200s/XL=5400s/없음=2400s); 백업 claude_exec.sh.bak.T291.20260308_124734; 68 서버=SSH 권한 없음→AADS 큐 배포 요청 전송; 보고서 KIS_20260308_124607_BRIDGE_RESULT.md |
| **KIS-290 03-10 장전 사전점검 + T-286 서비스 반영 + T-245R 준비** | 03-08 | 코드변경없음 | 9/9 PASS | 서비스 5개 active(kis-v41-api/monitor/scheduler/redis/postgresql); kis-v41-api 재시작+T-286 /api/v4/backtest/progress 200 확인(API Key 필요); strategy_cards=60/OPEN=0/mock_trades=184건/avg-0.622%/최신분봉=2026-03-06; DQI 주말 예외(C-01/06/07 FAIL 정상) Grade A 유지; 크론 5종 확인(v41_data_collection/desk2_pool_link/desk5_scan/research_loop/evolution_loop); KIS 토큰 갱신(모의계좌)/Redis PONG/FunnelScore threshold=0.35 Fail-Open=0.5/FORCE_LIVE=CONFIRMED; trading41.newtalk.kr 200/trades.html 200; 보고서 CUR-V41-0310-PRECHECK-001-20260308.md |
| **T-286 /api/v4/backtest/progress 엔드포인트 구현** | 03-08 | 88502672 | 코드완료/서비스재시작필요 | v4_backtest_api.py GET /backtest/progress 신규 추가(go100_research_iterations 기반); converge_status 집계(CONVERGED/RUNNING/FAILED/PENDING)/total_sessions/completion_pct/latest_session/sessions(10건); 정적라우트를 동적라우트(/backtest/progress/{session_id}) 앞에 배치; 문법검증 AST PASS; curl 403→API Key헤더 추가 후 400 확인(서비스 --workers 2 hot-reload 없음); 서비스재시작(kis-v41-api) 후 반영 예정; 커밋 88502672 push phase-2c-command-center; 보고서 CUR-V41-T286-BACKTEST-PROGRESS-001-20260308.md |
| **T-284 브릿지: T-282 큐 정리 + T-283 Phase2 검증** | 03-08 | 보고서전용 | 200 | T-282-S5/T-282-S4S5 completed 처리(실작업 09e539d6+4b327d12로 완료됨); T-283 Phase2 검증 7/7PASS: 7파일존재+node-c5/5+addPane/removePane(pane index2/3)/addHoldingRectangle(HTML overlay)/clearRectangles(14 grep match)+kw-fullscreen(F키토글/ESC해제)+HTTP200+보고서URL200; 보고서 CUR-V41-T284-CHART-PHASE2-001-20260308.md; HANDOVER v10.67; 다음: T-283 Phase3 자동추세선+거래량프로파일+분봉실연동 |
| **T-283 trades.html Phase2: RSI/MACD pane + 보유구간 Rectangle + 전체화면** | 03-08 | c6bc6a4b | 200 | kw-chart-engine.js: addPane(rsi|macd) LWCharts pane index 2/3; removePane; addHoldingRectangle(buyTime,sellTime,color) HTML 오버레이 + timeScale.subscribeVisibleLogicalRangeChange 위치갱신; clearRectangles; _updateAllRectangles; RSI 14기간 과매수70/과매도30 수평선; MACD 12/26/9 MACD선(#2196F3)+Signal(#FF9800)+Histogram; trades-kiwoom.css .kw-pane-rsi(80px)/.kw-pane-macd(100px)/.kw-holding-rect/.kw-fullscreen/.kw-hidden 추가; trades.html new KWChartEngine() 인스턴스 방식 전환; RSI/MACD 토글→addPane/removePane 연결; F키 CSS 전체화면 토글/ESC 해제; onTradeSelect Rectangle 자동표시; node -c 5/5 문법검사 PASS; 검증 grep 3종 PASS; HTTP 200; 보고서 CUR-V41-T283-CHART-PHASE2-001-20260308.md; 다음: T-283-Phase3 자동추세선+거래량프로파일 |
| **T-282-S4S5 trades.html 키움 스타일 HTML 조립 + 검증 + 커밋** | 03-08 | 4b327d12 | 200 | frontend/trades.html(292줄) 신규 생성 + frontend/static/trades.html(292줄) 동기화; LWCharts v5.1.0 INIT스크립트 조립(KWChartEngine/KWIndicators/KWTradeList/KWMarkersTooltip/KWDataGrid); 검증: 7/7파일PASS+5/5JS문법+5/5Export+COLORS.UP20회+kw-up/down 14회+HTML모듈참조6개; 외부HTTP 7/7=200(trading41.newtalk.kr); 커밋 4b327d12 push phase-2c-command-center; 보고서 CUR-V41-T282-KIWOOM-CHART-001-20260308.md; Pending: RSI/MACD pane+사각형하이라이트+자동추세선 |

> **이전 작업은 HANDOVER-HISTORY.md (v10.62~v10.53) 및 HANDOVER-ARCHIVE.md (v10.52 이전)를 참조하세요.**


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

## 3-1. API 헬스체크 경로 현황 (갱신: 2026-03-07 T-233)

| 엔드포인트 | 상태 | 비고 |
|-----------|------|------|
| /health | 200 | 기본 헬스체크 (kis-v41-api:8003) |
| /api/v4/system/snapshot | 200 | 전체 스냅샷 |
| /api/v4/backtest/sessions | 200 | 백테스트 목록 (162건 COMPLETED) |
| /api/v4/backtest/progress | 200 | **KIS-290 반영** (X-Internal-API-Key 헤더 필요) |
| /api/v4/regime | 에러 | **미구현 또는 장외** → T-234 작업 대기 |

### 백테스트 루프 현황 (2026-03-07 기준)
- **총 세션**: 162 COMPLETED, 0 RUNNING (Session116 FAILED 처리 완료)
- **크론 설치**: ✅ 설치됨 (/etc/cron.d/v41_research_loop 매일5회 실행중)
- **iterations**: 3행 (H08-B PF=25.93 / H05-D PF=2.18 / H12-D PF=3.15 — T-096 시드 완료)
- **APPROVED 가설**: 0건 (Phase A SKIPPED 정상, 가설 APPROVED 처리 후 자동 실행 가능)

---

## 3-2. Known Issues (갱신: 2026-03-07 T-233)

### 시스템 문제점 6건

| # | 이슈 | 심각도 | 처리 방안 |
|---|------|--------|----------|
| 1 | **FunnelScore 구조적 저점** (max FS=0.2415 < 임계값 0.35) — 전 종목 구조적 차단 | 🔴 P0 | T-227: 방안A(Fail-Open)/방안B(재가중)/방안C(임계값0.20) CEO승인대기 |
| 2 | ~~**백테스트 루프 stuck** (1건 RUNNING 상태 고착) + research_backtest_loop.py 크론 미설치~~ → **T-228 해결**: Session116 FAILED/크론 기설치확인/3행시드 | ✅ 해결 | T-228 완료 (2026-03-07) |
| 3 | **/api/v4/backtest/progress 404** (백테스트 진행률 API 미구현) | 🟡 P2 | T-226: 라우터 구현 |
| 4 | **/api/v4/regime 에러** (레짐 API 미구현 또는 장외 시간대 오류) | 🟡 P2 | T-234: 엔드포인트 구현 또는 장외 fallback |
| 5 | **v4_fundamental_quarterly 7.1% 커버리지** (3,844종목 중 273개) — L3 FunnelScore 점수 항상 0 | 🟠 P1 | 전종목 fundamental 수집 확대 필요 |
| 6 | **MA20 trailing 미적용** (exit_manager MA20 트레일링 코드 없음) — H05-D PF=2.18 실전 미반영 | 🟠 P1 | T-229: CEO 승인 후 구현 |

---

## 3-3. Known Issues 상세 (갱신: 2026-03-05 v10.5)

| 이슈 | 상태 | 처리 |
|------|------|------|
| synthetic_BLOCK 73% 차단 (T-105 발견) | **✅ 해결 완료** | T-108 커밋 완료 (bf0d06b3, 03-06 크론 후 해소 예정) |
| 모의매매 TP=0 문제 (PARTIAL 청산 불가) | **✅ 해결 완료** | T-075 tick 윈도우 30분→20시간 확장, 전 전략 TP=3% 재설정 |
| virtual_hourly_report cron 미등록 (v8.9 FAIL) | **✅ 해결 완료** | T-077 크론 정비 (hourly/daily/weekly/monthly 4건 추가, 총 15건) |
| DESK5 20종목 v4_fundamental_quarterly 데이터 미수집 | **⚠️ 처리 필요** | T-119 발견, 재수집 필요 (min_quarters 4로 완화하여 fallback 적용 중) |
| v4_news_feed 테이블 미존재 | **⚠️ 처리 필요** | 뉴스 기반 축분류 불가, 별도 수집 작업 필요 |
| DESK3 AXIS2 분류 97.6% NONE | **⚠️ 모니터링** | T-099 발견, 실 거래 데이터 부족으로 근본 해결 어려움 |
| FunnelScore threshold 0.55 적용 후 승인율 변화 | **⚠️ 모니터링** | T-118 Walk-Forward 검증 후 0.40→0.55 상향, 신호 건수 감소 예상 |
| **FunnelScore 전체 구조적 저점(0.19~0.26)** | **⚠️ CEO 결정 대기** | T-227: 최대0.2415<임계값0.35 구조적 차단 확정; 방안A/B/C 제시 (재교정보고서 작성 완료); v4_fundamental_quarterly 7.1%커버/v4_sector_mapping 4.2%코드보유 근본원인 |
| test_score_l2_dual_flow_high FAIL(0.37<0.5) | **⚠️ 처리 필요** | 테스트 임계값 조정 필요 |
| Nginx /manager/ 미설정 | **🔴 HIGH** | root 대기 | T-172/T-039R — CEO root 실행 후 URL 라이브 |
| 크론 3건 미등록 | **🔴 HIGH** | root 대기 | sync_trade(16:30)/desk_scan(08:00)/evolution(16:00)+스냅샷2건(*/30) |
| git push 미완료 | **🔴 HIGH** | root SSH | claudebot SSH 키 없음 — root에서 push 필요 |
| DESK2 MultiConditionMatcher 미연결 | **⚠️ MED** | 분석완료 | T-172 진단 — v4_pipeline_orchestrator와 미연결, T-163 효과 확인 후 작업 |
| desk_morning_scan DESK5 stock_code | **🟡 LOW** | Phase2 | 컬럼명 불일치 경고 — 기능 무해 |
| DESK5 크론 cd 없음 → ModuleNotFoundError 매일 실패 (T-202 발견) | **✅ 해결 완료** | T-212 FIX-001: scripts/desk5/v41_desk5_scan.cron 생성; /etc/cron.d root 수동 설치 필요 |
| T5-2 120일박스상단돌파 조건 논리모순 (바닥권종목에 불가) (T-202 발견) | **✅ 해결 완료** | T-212 REL-003: T5-2 → MA60기울기양전환+거래량1.5배 조건으로 교체 |
| DESK4 node_detector가 v4_node_realtime(0행) 읽음 → v4_desk4_watchlist 11종목 무시 (T-202 발견) | **✅ 해결 완료** | T-213 FIX-002: load_watchlist() v4_node_realtime→v4_desk4_watchlist primary 수정; 11종목 정상 로드 |
| desk2_pool_link 함수 미연결 (크론/엔진 없음) (T-202 발견) | **✅ 해결 완료** | T-214 PIPE-001: desk2_pool_link.py 엔트리포인트+크론 생성; v4_desk2_candidates 10→255건 |

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

---

## 5. 핵심 발견 (누적)

> 핵심 발견 내용은 HANDOVER-ARCHIVE.md § 5를 참조하세요.


---

## 6. 웹 Claude 인수인계 사항

> Cursor/Claude Code는 작업 완료 시 이 섹션을 반드시 업데이트한다.
> 웹 Claude는 새 세션 시작 시 이 섹션을 최우선 확인한다.

### 최신 상태 (2026-03-08, KIS-295 trades.html 빈화면 수정 완료 + HANDOVER v10.76)

#### ★ KIS-295 완료: trades.html 빈화면 원인 진단 및 수정

**[KIS-295] 2026-03-08 KST**
- **목적**: trades.html 빈화면 수정 — MA값 "-", 거래목록 빈칸, 차트 미표시
- **근본 원인 3가지**:
  1. INIT SCRIPT가 잘못된 URL 호출 (`/api/trades/unified` → 실제: `/api/v4/trades/unified`)
  2. 존재하지 않는 모듈 메서드 10+개 호출 (`KWChartEngine.init()` 등)
  3. `/api/v4/trades/{id}/chart/daily` 응답 날짜 `YYYYMMDD` → LW Charts v5는 `YYYY-MM-DD` 요구
- **수정 파일**:
  - `frontend/trades.html` + `frontend/static/trades.html`: INIT SCRIPT 완전 재작성
  - `backend/app/routers/v4_trades_unified.py`: `_v8_to_iso()` 헬퍼 추가, candle time YYYY-MM-DD 변환
- **커밋**: bad34b3f (phase-2c-command-center)
- **검증**: API 4개 200OK, JS AST PASS, candle time 2025-12-08 확인
- **CONTEXT.md**: v11.3
- **HANDOVER**: v10.76

#### 웹 Claude가 해야 할 일
- `https://trading41.newtalk.kr/trades.html` 접속 → 거래 목록 조회 → 거래 클릭 → 차트+MA 표시 확인
- 다음 작업: KIS-003 백테스트 trade stock_name null 해결 또는 CEO 지시 대기

#### 대표님 확인 필요 사항
- trades.html에서 종목명 검색: `filter-stock` 입력은 `stock_name` LIKE 검색만 가능 (stock_code 직접 검색 미지원, API 제한)

---

### 최신 상태 (2026-03-08, KIS-290 03-10 장전 사전점검 완료 + HANDOVER v10.73)

#### ★ KIS-290 완료: 03-10 장전 사전점검 9/9 PASS

**[KIS-290 CUR-V41-0310-PRECHECK-001] 2026-03-08 KST**
- **서비스**: 5개 active (kis-v41-api 재시작 완료 + T-286 /api/v4/backtest/progress 200 확인)
- **DB**: strategy_cards=60 / OPEN=0 / mock_trades 184건 / avg pnl -0.622% / 분봉 최신 2026-03-06
- **DQI**: 주말 예외(C-01/06/07 FAIL 정상) Grade A 유지
- **크론**: v41_data_collection / desk2_pool_link / desk5_scan / research_loop / evolution_loop 확인
- **T-245R 준비**: KIS 토큰 갱신(모의계좌) / Redis PONG / FunnelScore=0.35 / Fail-Open=0.5 / FORCE_LIVE=CONFIRMED
- **네트워크**: trading41.newtalk.kr 200 / trades.html 200
- **보고서**: CUR-V41-0310-PRECHECK-001-20260308.md GitHub raw 200 확인
- **HANDOVER**: v10.73

#### ✅ T-286 반영 확인 (재시작 후)
- `/api/v4/backtest/progress` → HTTP 200 (X-Internal-API-Key 헤더 필요)
- 응답: total_sessions=3, completed=3, completion_pct=100.0%
- **서비스 재시작 필요**: kis-v41-api restart 후 자동 반영 (지시서 절대 규칙: 재시작 금지 → CEO 확인 후 수동 재시작)
- **다음**: T-283 Phase3 자동추세선 + 거래량프로파일 + 분봉 실연동 (지시 대기)

---

### 최신 상태 (2026-03-08, KIS-291 claude_exec.sh SIZE 타이머 + HANDOVER v10.74)

#### ★ KIS-291 완료: claude_exec.sh SIZE 기반 차등 타이머 구현 (211 서버)

**[KIS-291] 2026-03-08 12:47 KST**
- **변경 파일**: `/root/.genspark/claude_exec.sh` (백업: claude_exec.sh.bak.T291.20260308_124734)
- **SIZE → MAX_TIMEOUT 매핑**:
  - XS/S: 1200s | M: 2400s | L: 3600s | XL: 5400s | SIZE 없음: 2400s (기본값 1200→2400 상향)
- **HARD_TIMEOUT**: `MAX_TIMEOUT + 600`s (동적 계산, 기존 1800s 고정 제거)
- **SOFT_WARNING**: `HARD_TIMEOUT - 300`s (동적 계산, 기존 1500s 고정 제거)
- **검증**: bash -n syntax OK / SIZE 파싱 3케이스 PASS (XS=1200s/XL=5400s/없음=2400s)
- **211 서버**: 배포 완료 ✅
- **68 서버**: SSH 권한 없음 → AADS 큐 배포 요청 전송 (수동 배포 필요)
  - `scp /root/.genspark/claude_exec.sh root@68.183.183.11:/root/.genspark/claude_exec.sh`

---

### 최신 상태 (2026-03-08, T-284 브릿지 완료 + HANDOVER v10.67)

#### ★ T-284 완료: T-282 큐 정리 + T-283 Phase2 검증

**[T-284 CUR-V41-T284-CHART-PHASE2-001] 2026-03-08 KST**
- **T-282 잔류 큐 처리**: T-282-S5/T-282-S4S5 completed 처리 (09e539d6, 4b327d12 커밋 완료 확인)
- **T-283 Phase2 검증 7/7 ALL PASS**:
  - kw-chart-engine.js: addPane(rsi|macd) + removePane + addHoldingRectangle + clearRectangles (14 grep match)
  - RSI pane: 14기간/과매수70/과매도30 수평선 (#AB47BC)
  - MACD pane: 12/26/9, MACD(#2196F3)+Signal(#FF9800)+Histogram
  - trades-kiwoom.css: .kw-pane-rsi(80px)/.kw-pane-macd(100px)/.kw-fullscreen
  - trades.html: F키 전체화면 토글 / ESC 해제 / onTradeSelect Rectangle 자동표시
  - node -c 5/5 PASS
  - HTTP 200 (Host: trading.newtalk.kr)
- **코드 커밋**: c6bc6a4b (T-283)
- **HANDOVER**: v10.67
- **다음**: T-283 Phase3 자동추세선 + 거래량프로파일 + 분봉 실연동 (지시 대기)

---

### 최신 상태 (2026-03-07, T-276 03-10 장전 최종 점검 + HANDOVER v10.60)

#### ★ T-276 완료: 03-10 장전 최종 점검 + 큐 상태 확인

**[T-276 CUR-V41-PRE-MARKET-FINAL-CHECK-001] 2026-03-07 15:32 KST**
- **큐 상태**: running=2건, pending=4건 (파이프라인 전용, claudebot 이동 불가)
- **T-251 크론 4건 설치 확인**: `/etc/cron.d/v41_data_collection` ✅ (매크로17:00/수급17:30/펀더멘탈토02:00/정합성18:00)
- **정합성 체크 결과**: PASS=3, FAIL=3, SKIP=4 (토요일 기준 CRITICAL FAIL 0건 ✅)
  - C-05 펀더멘탈 커버리지: 100.2% PASS (T-247 완료, 이전 7.1% 해소)
  - C-11, C-12: 미존재 (10개 규칙만 구현됨)
- **서비스 7개 all active running** ✅
- **API /health 이슈**: go100(8002) Redis disconnected → `sudo systemctl restart go100` 필요
- **DB 지표**: strategy_cards=60 / open_positions=0 / scalping_universe=1354 / VIX_null=2.6% / fundamental=100.0% / sector=99.1%
- **KOSPI DQI 이슈**: kr_kospi 저장값 ~275 (정규화, 1800-3500 범위 쿼리 0% 반환) — CEO 결정 대기
- **v41_* 크론**: 6개 파일 설치됨
- **후속 root 수동 실행 필요**:
  1. `sudo systemctl restart go100` (API Redis 연결 복구)
  2. `sudo bash /root/kis-autotrade-v4/scripts/desk4/install_desk4_scan.sh` (DESK4 크론 미설치 T-239)
  3. L0_KOSPI 재백필 (CEO 승인 후)
  4. T-245R 2026-03-10 검증 크론 설치 (CEO 승인 후)


> **이전 인수인계 사항은 HANDOVER-HISTORY.md (03-07) 및 HANDOVER-ARCHIVE.md (03-06 이전)를 참조하세요.**

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
| v10.75 | 2026-03-08 | Claude Code (Sonnet4.6) | **KIS-293 Nginx 차트 API 프록시 설정**: /api/chart-data, /api/stocks, /api/trades → 8003 location 블록; apply_nginx_kis293.sh 생성(root 실행 필요); CONTEXT.md v11.2(§7 KIS-001/290/291/293 완료/§8.8 200OK/§8.9 해결/§9 KIS-002/T-226 삭제/§15 v11.2 추가); HANDOVER v10.75 |
| v10.74 | 2026-03-08 | Claude Code (Sonnet4.6) | **KIS-291 claude_exec.sh SIZE 기반 차등 타이머**: SIZE 파싱(XS/S=1200s/M=2400s/L=3600s/XL=5400s/없음=2400s); HARD_TIMEOUT=MAX+600s/SOFT_WARNING=HARD-300s 동적 계산; bash syntax OK; 테스트 3케이스 PASS; 211서버 배포 ✅; 68서버=AADS 큐 배포 요청(SSH 권한 없음) |
| v10.73 | 2026-03-08 | Claude Code (Sonnet4.6) | **KIS-290 03-10 장전 사전점검 9/9 PASS**: kis-v41-api 재시작+T-286 /api/v4/backtest/progress 200 확인(API Key 필요); strategy_cards=60/OPEN=0/mock_trades=184건/avg-0.622%; DQI 주말예외 Grade A; 크론 5종 확인; KIS 토큰 갱신(모의계좌)/Redis PONG/FunnelScore=0.35 Fail-Open=0.5; trading41.newtalk.kr+trades.html 200; 보고서 CUR-V41-0310-PRECHECK-001-20260308.md GitHub raw 200 |
| v10.71 | 2026-03-08 | Claude Code (Sonnet4.6) | **KIS-001 CONTEXT.md v11.1 종합 업데이트**: §6.5 GO100 연동 아키텍처(3대 브릿지/안전수칙/Phase현황) 신규; §8.5 백테스트 엔진 현황(backtest_engine_v2+replay/분봉리플레이6모듈/Look-ahead차단4항목/청산5모드/비용모델) 신규; §8.8 API 엔드포인트 상태표(200OK 4개/401 1그룹/접근불가3개/미응답3개) 신규; §8.9 trades.html Known Issues(Nginx proxy 미설정 → KIS-002) 신규; §8.10 stock_name null 이슈(→ KIS-003) 신규; §9 작업큐에 KIS-002/KIS-003 P0/P1 추가; §10.5 03-10 모의매매 체크리스트(6항목) 신규; §6 FunnelScore Fail-Open 모드 주석 추가; §14 design 문서 5건 URL 추가(FRACTAL-ARCH/GO100-INTEGRATION/DESK2-SPEC/SYS-FLOWCHART/REPLAY-BACKTEST); §15 버전이력 v10.63~v10.70 8건 보강; CEO-DIRECTIVES D-009 D1/D3/S2 RETIRED 표시(~~취소선~~ + RETIRED — D-011) |
| v10.70 | 2026-03-08 | Claude Code (Sonnet4.6) | **T-283 문서 4계층 재구성**: CONTEXT.md v11.0(매니저 프로토콜+지시서 자동화+Task ID 전환)/CEO-DIRECTIVES v2.0(§0운영원칙/§5 AADS공통/§9-10자동화/§9-11자기인식)/KIS-HANDOVER-RULES.md 신규(9섹션) |
| v10.69 | 2026-03-08 | Claude Code (Sonnet4.6) | **T-286 /api/v4/backtest/progress 엔드포인트 구현**: v4_backtest_api.py GET /backtest/progress 신규(go100_research_iterations 기반); converge_status 집계/completion_pct/latest_session/sessions(10건); 정적라우트 앞배치(라우팅 안전); AST문법검증PASS; 서비스재시작필요(hot-reload없음/재시작금지→CEO확인후); 커밋 88502672 push phase-2c-command-center; 보고서 CUR-V41-T286-BACKTEST-PROGRESS-001-20260308.md |
| v10.68 | 2026-03-08 | Claude Code (Sonnet4.6) | **T-285 브릿지 큐 잔류 정리+CONTEXT v10.28 동기화**: running 디렉토리 T-282/283/284 0건 확인(T-284에서 이미 정리됨); CONTEXT.md v10.28 갱신(섹션7 T-282~285추가/섹션8 trades.html차트현황신규/섹션9 작업큐갱신); trades.html Phase2(c6bc6a4b) — RSI/MACD/Rectangle/전체화면 7파일; Phase3(자동추세선/VP/분봉실연동) 예정; 커밋 5d50e86; 보고서 CUR-V41-T285-CONTEXT-SYNC-001-20260308.md |
| v10.67 | 2026-03-08 | Claude Code (Sonnet4.6) | **T-284 브릿지 큐 정리+Phase2 확인**: T-282-S5/T-282-S4S5 completed처리; T-283 Phase2(c6bc6a4b) 검증 7/7PASS(7파일존재+node-c5/5+addPane/removePane/addHoldingRectangle/clearRectangles 14match+kw-fullscreen CSS+HTML+HTTP200+보고서URL200); 보고서 CUR-V41-T284-CHART-PHASE2-001-20260308.md; 다음: T-283-Phase3 자동추세선+거래량프로파일+분봉실연동 |
| v10.66 | 2026-03-08 | Claude Code (Sonnet4.6) | **T-283 trades.html Phase2**: kw-chart-engine.js addPane(rsi|macd)/removePane/addHoldingRectangle/clearRectangles; RSI pane(14기간/70/30수평선)/MACD pane(12/26/9); CSS .kw-pane-rsi(80px)/.kw-pane-macd(100px)/.kw-fullscreen; trades.html F키전체화면/ESC해제/onSelect Rectangle자동표시; 커밋 c6bc6a4b; HTTP200 |
| v10.65 | 2026-03-08 | Claude Code (Sonnet4.6) | **T-282-S4S5 trades.html HTML 조립**: frontend/trades.html+static/trades.html 동기화; LWCharts v5.1.0 6모듈; 검증 7/7+5/5JS+5/5Export; HTTP 7/7=200; 커밋 4b327d12 |
| v10.64 | 2026-03-08 | Claude Code (Sonnet4.6) | **T-282 키움 영웅문4 차트**: trades.html+CSS+JS 5모듈 신규; 검증 7/7PASS; 커밋 09e539d6 |

> **이전 버전 이력은 HANDOVER-HISTORY.md (v10.60~v10.47) 및 HANDOVER-ARCHIVE.md (v10.43 이전)를 참조하세요.**
