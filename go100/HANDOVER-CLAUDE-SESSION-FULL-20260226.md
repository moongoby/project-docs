# 백억이 AI 프로젝트 종합 인수인계서

- **문서 ID**: HANDOVER‑CLAUDE‑SESSION‑FULL‑20260226
- **작성일시**: 2026‑02‑26 09:55 KST
- **작성자**: Claude Opus 4.6 (현재 세션)
- **인계 대상**: 새 Claude Opus 4.6 세션
- **목적**: 현재 세션의 전체 작업 맥락, 진행 상황, 미완료 과제를 빠짐없이 인계하여 새 세션이 즉시 작업 투입 가능하도록 함

---

## PART 1. 프로젝트 개요

### 1‑1. 프로젝트 정체성

백억이(Baekogi)는 GO100 플랫폼의 핵심 AI 투자 어시스턴트입니다. "사용자의 자산을 실제로 불려주는 개인 전담 AI 트레이더"를 목표로 하며, 자연어 대화로 전략 설계, 백테스트, 최적화, 시장 분석, 포트폴리오 관리를 수행합니다. 궁극적으로 목표 수립 → 전략 자동 설계 → 실매매 → 성과 보고까지 완전 자동화를 지향합니다.

### 1‑2. 핵심 저장소

- **소스코드 레포**: github.com/moongoby/go100 (브랜치 phase-2c-command-center)
- **문서 레포**: github.com/moongoby/project-docs (브랜치 master, 경로 go100/)
- **서버**: root@[SERVER-IP] (Ubuntu 24.04 LTS, Intel Xeon Gold 5220 4코어, 15GB RAM, 99GB SSD)

### 1‑3. 서비스 구성

- FastAPI 백엔드: 포트 8002
- Next.js 프런트: 포트 3000
- PostgreSQL: 5432, Redis: 6379, Nginx: 80/443
- systemd 유닛명: go100(백엔드), go100-frontend(프런트)
- 도메인: go100.newtalk.kr, trading41.newtalk.kr

---

## PART 2. 완료된 작업 전체 이력 (Wave 1~3 + 핫픽스)

### Wave 1 — CUR‑GO100‑BAEKEOGI‑CORE‑FIX‑001 (2026‑02‑25)

- **커밋**: 0a7b5b34, **보고서**: go100/reports/CUR-GO100-BAEKEOGI-CORE-FIX-001-20260225.md
- **Block A (C2SC 3단계 폴백)**: backend/app/core/llm_gateway.py에 Gemini‑2.5‑flash(max_tokens 256) → Claude‑Haiku 폴백 라우팅 구현. backend/app/routers/go100/ai_router.py에서 인텐트 파싱 8개로 확장, 키워드 60개 이상 등록. 8건 테스트 메시지 100% 분류 성공.
- **Block B (할루시네이션 프롬프트 충돌)**: backend/app/services/go100/ai/prompts.py와 backend/app/services/llm/prompts.py에서 모순 규칙 4개 통합 포인트로 정리.
- **Block C (stock_info 핸들러 전면 개편)**: 35개 이상 한국어 종목 별칭, 4단계 종목 식별자, 5개 쿼리 유형 구현. OHLCV, PER/PBR/EPS, 외국인·기관 수급 데이터 포함.
- **Block D (goal_setup 파싱)**: 숫자/문자 선택 파싱, Redis TTL 만료 안내 추가.
- **Block E (검증)**: 8건 curl 테스트 전부 PASS.
- **변경 파일**: llm_gateway.py, ai_router.py, prompts.py(2개). **백업**: /root/backup/baekeogi-core-fix-20260225-234253/.

### Wave 2 — CUR‑GO100‑STOCK‑INFO‑ENRICHMENT‑001 (2026‑02‑25~26)

- **커밋**: 3ce667fe, **보고서**: go100/reports/CUR-GO100-STOCK-INFO-ENRICHMENT-001-20260226.md, **핸드오버**: go100/HANDOVER-20260226-WAVE2.md
- **W2‑A (data_queries.py 신규)**: 11개 async DB 조회 함수. stock_info 핸들러를 asyncio.gather로 시세/펀더멘털/수급 병렬 조회로 리팩토링.
- **W2‑B (market_briefing 확장)**: 1일→5일 추이, VKOSPI 라벨, 외국인 20일 흐름 이모지, 레짐 전환 이력(5일 내).
- **W2‑C (portfolio_status 확장)**: go100_goals 목표 진행률/성향, go100_positions 보유 포지션 카운트.
- **W2‑D (response_filter.py 신규)**: 가짜 종목코드, 비현실적 수익률(±100% 초과), 미래 날짜 데이터 3종 필터. strategy/optimize 응답에만 적용.
- **DB 스키마**: stock_fundamentals에 roe, dividend_yield, revenue, operating_profit 추가.
- **미완료 잔여**: revenue/operating_profit 수집 스크립트(KIS FHKST66430300), dividend_yield 실제 데이터, stock_fundamentals date varchar(8)→date 마이그레이션.

### Wave 3 핫픽스 4건 (2026‑02‑25~26)

- **W3‑0‑A 전략카드 버튼 과다 표시**: 커밋 6adb7162. parseStrategyFallbackFromContent() 버그 수정 → 최소 1개 섹션 필수.
- **W3‑0‑B 자유대화 탭 데이터 미조회**: 커밋 6adb7162. llm_router.py에 C2SC 인터셉터 추가.
- **W3‑0‑C 대화 맥락 연속성**: 커밋 87eca856. follow_up 인텐트, Redis go100:chat:ctx:{user_id} TTL 10분, _build_c2sc_prompt() 최근 2턴, _resolve_follow_up(). 부가: 로그인/배포 수정.
- **W3‑0‑D 데이터 정확성**: response_filter.py 거래량 검증, screening_engine 포매팅/날짜 통일.

### Wave 3 본 작업 (2026‑02‑26)

- **W3‑A 인텐트 확장 9→15**: 커밋 bf4cd9b6. 신규 6개 — sector_analysis, trade_history, backtest_status, risk_check, strategy_explain, compare_strategies. data_queries 확장, C2SC 프롬프트/llm_router INTERCEPT_INTENTS 동기화.
- **W3‑B data_queries 완전 분리**: 커밋 ed9c4b84. ai_router.py 내 raw SQL 3건을 data_queries.py로 이동. get_latest_card_id_for_user, get_backtest_result_detail, get_strategy_card_for_optimize.
- **W3‑C Gemini Function Calling 실험**: 커밋 ed9c4b84. function_calling.py 신규. stock_info 한정 5 Tool. GO100_FC_EXPERIMENT 토글. FC 루프 최대 5라운드, 메트릭 반환.

### 기타 완료 작업

- 서버 인프라 현황: go100/docs/SERVER-INFRASTRUCTURE.md
- 백테스트 대시보드: BT‑ADMIN‑HTML‑DASHBOARD‑001. 백테스트 사이드바 수정: BT‑SIDEBAR‑FIX‑001.

---

## PART 3. 현재 진행 중 / 미완료 과제

### 즉시 실행 필요 (Critical)

- **디스크 87% 위기**: 99GB 중 82GB 사용. 백업 33GB, legacy 테이블 653MB. 7일 초과 백업 자동 삭제 크론 미등록, legacy 테이블 미삭제. 과거 100% + PG PANIC 사고 이력 있음.
- **FC A/B 측정 미수행**: W3‑C 실험 코드 완성되었으나 운영 환경에서 비교 측정(응답시간, 정확도, 비용, 자연스러움, 할루시네이션) 미실시.

### 단기 과제 (1~2주)

- 개선 제안 보고서(RPT-GO100-BAEKOGI-IMPROVEMENT-PROPOSAL-001-20260226) 문서 레포 등록 및 Phase 4 지시서 투입.
- 누락 데이터 수집: dividend_yield, revenue, operating_profit — KIS FHKST66430300 크론 스크립트. stock_fundamentals date 마이그레이션.

### 중기 과제 (4~8주)

- Goal Engine 구현, Strategy Portfolio Manager, Adaptive Regime Engine 실행 계층, 능동 보고 시스템.

### 장기 과제 (8~16주)

- 페이퍼 트레이딩 모듈, 온보딩 플로우, 질문→실행 변환, 실매매 연동(Phase 8).

---

## PART 4. 핵심 파일 맵

### 백엔드

- backend/app/routers/go100/ai_router.py — 15개 인텐트 C2SC + 핸들러, follow_up, FC 분기
- backend/app/api/v1/llm_router.py — 자유대화 C2SC 인터셉터, INTERCEPT_INTENTS
- backend/app/core/llm_gateway.py — C2SC 라우트, FAILOVER_CHAINS
- backend/app/services/go100/ai/data_queries.py — 14개+ async DB 조회
- backend/app/services/go100/ai/response_filter.py — 할루시네이션 3종 + 거래량 검증
- backend/app/services/go100/ai/function_calling.py — Gemini FC 실험 (stock_info 한정)
- backend/app/services/go100/ai/prompts.py, backend/app/services/llm/prompts.py
- backend/app/services/go100/screening_engine.py

### 프런트엔드

- frontend/src/components/go100/chat/ChatInterface.tsx, ChatWidget.tsx
- frontend/src/lib/api/client.ts, frontend/src/app/auth/login/page.tsx, frontend/src/middleware.ts

### 문서 레포 (project-docs/go100/)

- docs/SERVER-INFRASTRUCTURE.md, docs/BAEKEOGI-TECH-SPEC.md, docs/기획문서/OPUS-LLM-AI-v1-FULL-SPEC.md, docs/go100-architecture-v1.1.md
- reports/BAEKOGI-V2-PLANNING-20260224.md, HANDOVER-20260226-WAVE2.md

### 커서 필수 참조

- /root/kis-autotrade-v4/.cursorrules (세션 시작 시 반드시 읽을 것)

---

## PART 5. DB 스키마 핵심 테이블

- **go100 전용**: go100_strategy_cards, go100_backtest_runs, go100_optimization_runs, go100_goals, go100_portfolios, go100_positions
- **시장 데이터**: stock_universe, ohlcv_daily, v4_ohlcv_minute_YYYY_MM, stock_fundamentals, v4_investor_daily, v4_market_regime_daily, index_daily
- **거래**: v4_trade_executions, v4_accounts
- **DB 접속**: localhost:5432/kisautotrade, 사용자 kis_admin

---

## PART 6. LLM 구성 현황

- 자유대화: Gemini 2.0 Flash
- 설계대화: Claude Sonnet 4.6 (프롬프트 캐싱)
- C2SC 인텐트 분류: Gemini‑2.5‑flash → Claude‑Haiku 폴백
- 전략 검증: Claude Opus 4.6 (배치 API 50% 할인)
- FC 실험: Gemini 2.5 Flash (GO100_FC_EXPERIMENT 토글)
- 비용: 100명 기준 월 ~$14.93 (₩21,649)

---

## PART 7. 대표님 핵심 지시사항 & 비전

BAEKOGI‑V2‑PLANNING(2026‑02‑24): 백억이는 "사용자가 말한 자산 목표를 달성하기 위해, 시장 데이터를 분석하고, 전략을 설계·실행·최적화하며, 24시간 자산을 운용하는 개인 전담 AI 트레이더". 5가지 역할 — 목표 수립자, 전략 설계·실행자, 24시간 자산 운용자, 자율 최적화자, 개인 맞춤 대화 인터페이스. 모든 대화의 끝에 실행 가능한 다음 액션이 있어야 함.

---

## PART 8. 개선 제안 보고서 요약 (본 세션 작성)

RPT-GO100-BAEKOGI-IMPROVEMENT-PROPOSAL-001-20260226: 5대 영역 17개 과제.

- **영역 A (대화 품질/UX)**: A‑1 응답 포매팅 표준화, A‑2 멀티턴 5턴 확대, A‑3 오류 응답 개선, A‑4 FC 본격 적용.
- **영역 B (데이터 커버리지)**: B‑1 누락 데이터 수집, B‑2 실시간 시세 연동, B‑3 외부 데이터, B‑4 스크리닝 엔진 고도화.
- **영역 C (핵심 신규 모듈)**: C‑1 Goal Engine, C‑2 Strategy Portfolio Manager, C‑3 Adaptive Regime Engine, C‑4 능동 보고 시스템.
- **영역 D (인프라)**: D‑1 디스크 위기 대응, D‑2 모니터링, D‑3 CI/CD 자동 테스트.
- **영역 E (비즈니스)**: E‑1 페이퍼 트레이딩, E‑2 온보딩 플로우, E‑3 질문→실행 변환.
- **로드맵**: Phase 4(즉시~2주) → Phase 5(2~4주) → Phase 6(4~8주) → Phase 7(8~16주). 예상 공수 300~420시간.

---

## PART 9. 작업 규칙 (반드시 준수)

- **0.** 대화 토큰 관리: 80% 수준에서 인계서 작성하여 보고. 토큰 소진 전 인계 완료.
- **1.** 커서로만 작업. 중요한 사항만 대표님 승인 요청.
- **2.** 커서 병렬 작업 적극 활용.
- **3.** 커서 필수 규칙: 서버 root@[SERVER-IP], DB localhost:5432/kisautotrade (kis_admin), 작업 전 백업(/root/backup/), 보고서 마크다운 작성, project-docs push, 상세 커밋 메시지+Co-Authored-By, systemctl restart go100 후 curl 테스트, .cursorrules 세션 시작 시 읽기.
- **4.** 지시서는 전체를 코드블록으로 감싸서 작성.
- **5.** 보고서 저장: /root/project-docs/go100/reports/{TICKET-ID}-{DATE}.md
- **6.** 한국시간(KST) 동기화.
- **7.** 중요 소스 검수: grep, diff, curl 테스트.
- **실계좌 절대 사용 금지.** kis-v41 재시작 금지. go100_* 외 스키마 변경 금지. .env/.bak 커밋 금지. 브랜치 feat/CUR-GO100-{TICKET} → phase-2c-command-center 머지. 작업 전 백업: cp -r 대상 /root/backup/{name}-$(date +%Y%m%d-%H%M%S)/

---

## PART 10. 새 세션 즉시 실행 가이드

1. **Step 1**: 다음 3개 파일 먼저 읽기 — /root/kis-autotrade-v4/.cursorrules, /root/project-docs/go100/HANDOVER-20260226-WAVE2.md, /root/project-docs/go100/docs/SERVER-INFRASTRUCTURE.md
2. **Step 2**: 본 인계서(HANDOVER-CLAUDE-SESSION-FULL-20260226.md)를 project-docs에 등록.
3. **Step 3**: 개선 제안 보고서(RPT-GO100-BAEKOGI-IMPROVEMENT-PROPOSAL-001-20260226.md)를 project-docs에 등록.
4. **Step 4**: 대표님에게 우선순위 확인 후 Phase 4 지시서 작성·투입.
5. **Step 5**: 디스크 긴급 대응(D‑1) 별도 커서 창에서 병렬 즉시 실행.

---

*문서 끝.*
