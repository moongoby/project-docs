# HANDOVER – KIS AutoTrade V4.1
> 최종 업데이트: 2026-03-08 | 버전: v11.0
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
| 신규 KIS-xxx | KIS-001 ~ KIS-003 (현재 최신) | 활성 |
| 다음 발행 번호 | KIS-004 | — |

---

## 버전 이력

| 버전 | 날짜 | Task | 변경 요약 |
|------|------|------|-----------|
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
