# GO100 인수인계서 v15.3 — 자율 진화 루프 + 프론트엔드 완전체 + pandas 3.0 수정 + V3모델 활성화 준비 + SaaS 버그수정+SEO+에러모니터링 + Commander 대시보드 + entry_rules 정규화 + 매니저 스냅샷
> 작성: 2026-02-28 | 최종 업데이트: 2026-03-06 KST (v15.3 갱신: T-033B entry_rules 정규화 + T-039 매니저 스냅샷 + T-040 HANDOVER 갱신) | 대상: 다음 세션 AI
> 이전 문서: HANDOVER.md v13.2 (동일 파일, 버전 이력 하단 참조)

---

## ⚠️ 필수 규칙 — 반드시 먼저 읽고 준수

### 작업 규칙
1. 작업 시작 전 반드시 서비스 경계 확인: V4.1인지 GO100인지
2. 커밋 메시지 prefix 필수: [V4.1], [GO100], [SHARED]
3. GO100 작업 시 V4.1 파일 절대 수정 금지, 역도 동일
4. 공유 인프라(.env, main.py, nginx 등) 수정 시 양쪽 영향 명시
5. 대표님(user_id=2, [CEO-EMAIL-GM])이 CEO — 보고체 사용
6. 백억이 = GO100 AI 에이전트의 이름
7. 문서 레포(project-docs)와 코드 레포(kis-autotrade-v4)는 별도 관리

### Cursor 필수 규칙
1. 반드시 /root/kis-autotrade-v4/.cursorrules 파일을 읽고 시작
2. 반드시 /root/kis-autotrade-v4/CLAUDE.md 파일을 읽고 시작
3. 각 디렉토리의 SERVICE_BOUNDARY.md 확인
4. 파일 수정 전 백업: cp file.py file.py.bak.{작업명}
5. DB 스키마 변경 시 IF NOT EXISTS 필수
6. .env 수정 시 기존 값 주석 보존
7. 크론 등록 시 기존 crontab 백업 먼저
8. 작업 완료 후 반드시 보고서를 /root/project-docs/go100/reports/에 저장하고 git push

---

## 1. 프로젝트 개요

### GO100 (백억이)
- 목표: 증권사급 AI 투자 에이전트 (조건검색 + 자동매매 + 자율 전략 진화)
- 서버: Ubuntu 24.04, Xeon Gold 5220, 15GB RAM, 99GB SSD
- 스택: FastAPI(8002) + Next.js(3000) + PostgreSQL(16) + Redis + Nginx
- 도메인: go100.newtalk.kr
- 코드: /root/kis-autotrade-v4 (로컬 git, GitHub private 미등록)
- 문서: /root/project-docs → github.com/moongoby/project-docs (public)

### 핵심 환경
| 구분 | 내용 |
|------|------|
| 서버 | Ubuntu 24.04, /root/kis-autotrade-v4 |
| DB | PostgreSQL 16, kisautotrade / kis_admin @ localhost:5432 |
| 서비스 | go100(FastAPI 8002), Next.js 3000, Redis 6379, Nginx |
| API 키 | .env: KIS_APP_KEY, KIS_APP_SECRET, DART_API_KEY/OPENDART_API_KEY, GO100_TELEGRAM_BOT_TOKEN, GO100_TELEGRAM_CHAT_ID |

### KIS AutoTrade V4.1
- 기존 자동매매 시스템, GO100과 같은 모노리포에 공존
- V4.1 라우터: /api/v4/*, GO100 라우터: /api/go100/*
- 서비스 경계: .cursorrules에 명시

---

## 2. 현재 상태 (2026-03-06 기준)

### 진행률: **98%** (v15.3: T-033B entry_rules 정규화 완료 + T-039 매니저 스냅샷 + T-036/T-037 Commander 대시보드 구현 + v15.1: T-028~T-031 완료 — SaaS 버그수정·SEO완성·에러모니터링 구현) (P6 게이트 완전 통과 + P7-1 QA PASS + FE 완전체 반영 + pandas 3.0 호환 완료)

### Batch 6 결과
| 항목 | 점수/비고 |
|------|----------|
| P5-3 포트폴리오 최적화 | 92 (마이그레이션 044) |
| P5-4 개인화 | 90 (마이그레이션 045) |
| P6-1 리스크 엔진 + 킬스위치 | 95 (마이그레이션 046) |
| P6-EXTRA 검증 | 85 |

### Batch 7 결과
| 항목 | 비고 |
|------|------|
| P6-2 KIS 게이트웨이 | 완료 — go100_live_orders, 모의투자 주문/잔고 (마이그레이션 047) |
| P6-EXTRA-VERIFY | Agent Chat E2E 4단계 검증 (보고서 확인) |
| P7-1 QA | 종합 판정 (보고서 확인) |

### Batch 8 결과 (2026-03-01)
| 항목 | 비고 |
|------|------|
| Phase 4 AI Feature Pipeline | PASS — feature_engine.py + feature_store.py 구축, E2E 5종목 PASS |
| Phase 4 AI Feature Batch Build | PASS — 263,450 레코드, 월별 Parquet 12개, 15.13MB, 오류 0건, 306.7s |
| Phase 4 AI LightGBM V2 학습 | PASS — 3-Fold Walk-Forward, AUC 0.5406±0.0055, MFE_60MIN R²=0.58 (실전수준), 모델 4종 저장 |

### 완료 작업 테이블 (Batch 1~7 요약)

| Task ID | Batch | 날짜 | 점수 | 커밋 | HTTP | 핵심 결과 |
|---------|-------|------|------|------|------|-----------|
| P1-1 Agent Mode E2E | 1 | 02-27 | PASS | ✓ | 200 | 21/21 도구 PASS |
| P1-3 Cron Issues | 1 | 02-27 | PASS | ✓ | 200 | pykrx 폴백, regime 자동복구 |
| P1-4 Seed Data | 1 | 02-27 | PASS | ✓ | 200 | 3카드 백테스트 |
| P1-5 Freshness | 1 | 02-27 | PASS | ✓ | 200 | 6도구 freshness_warning |
| P3-1 전략 진화 | 3 | 02-27 | PASS | ✓ | 200 | migration 035 |
| P3-2 호가창 백테스트 | 3 | 02-27 | PASS | ✓ | 200 | migration 036 |
| P3-3 이벤트 엔진 | 3 | 02-27 | PASS | ✓ | 200 | migration 037, DART 연동 |
| P3-R1 전략 편집 | 4 | 02-27 | PASS | ✓ | 200 | migration 038 |
| P3-R2 지표 20개 | 4 | 02-27 | PASS | ✓ | 200 | TA 필터 35+ |
| P4-1 메모리 | 4 | 02-27 | PASS | ✓ | 200 | episodic_memory 연동 |
| P4-2 갭 | 4 | 02-27 | PASS | ✓ | 200 | migration 040, 108,574건 |
| P4-3 30일 모의투자 | 5 | 02-27 | PASS | ✓ | 200 | migration 041 |
| P5-1 자기리뷰 | 5 | 02-27 | PASS | ✓ | 200 | migration 043 |
| P5-2 Telegram+섹터 | 5 | 02-27 | PASS | ✓ | 200 | 모닝 브리핑 자동 발송 가능 |
| P5-3 포트폴리오 최적화 | 6 | 02-27 | 92 | ✓ | 200 | migration 044, Sharpe 4.63 |
| P5-4 개인화 | 6 | 02-27 | 90 | ✓ | 200 | migration 045 |
| P6-1 리스크+킬스위치 | 6 | 02-27 | 95 | ✓ | 200 | migration 046, CEO 전용 해제 |
| P6-EXTRA 신고가 돌파 | 6 | 02-27 | 85 COND | ✓ | 200 | execute_buy/sell 스텁 |
| P6-2 KIS 게이트웨이 | 7 | 02-28 | PASS | ✓ | 200 | migration 047, 모의 주문 4건 |
| P6-EXTRA-VERIFY | 7 | — | 보류 | — | — | 보고서 미제출 |
| P7-1 QA | 7 | — | 보류 | — | — | 보고서 미제출 |
| CUR-SHARED-DB-SCHEMA-CATALOG-001 | — | 03-02 | PASS | ✓ | 200 | DB 스키마 카탈로그 GO100+V4.1 통합: 246테이블+8뷰=254 전수 스키마, go100_* 70테이블 포함, 자동최신화 cron(매일06:00), 참조: shared/DB-SCHEMA-CATALOG.md |
| CUR-GO100-BRIDGE-BUG-FIX-001 | — | 03-02 | PASS | ✓ | 200 | genspark_bridge.py 3종 버그 수정: parse_directive 줄바꿈 필터(false positive 차단), CEO 승인 대기 30분 쿨다운(루프 방지), pressSequentially 입력방식 교체(React 호환) |
| CUR-GO100-P6-EXTRA-VERIFY-001 | — | 03-02 | PASS | ✓ | 200 | Agent Chat E2E 4단계 검증 PASS: screen_stocks new_high_52w, execute_buy/sell, 리스크 pre-trade, Agent Loop 5라운드. risk_engine async_generator 버그 수정 포함 |
| CUR-GO100-P7-1-FULL-QA-001 | — | 03-02 | PASS(조건부) | ✓ | 200 | 전체 QA 종합 판정 95/100: 서비스 정상, DB 70테이블, Agent도구 57개, 크론 31라인, Kill Switch E2E, KIS Mock주문 전 항목 PASS |
| CUR-GO100-P4-AI-ENHANCE-DESIGN-001 | — | 03-02 | PASS | ✓ | 200 | Phase 4 AI 모델 고도화 설계안 완료: As-Is 기준선(AUC 0.5406, MFE_3D R²=0.0784), To-Be 4개 축(교차피처, 멀티타겟, Regime 분리, Threshold), 구현 12일, 리스크 분석, 모의투자 연동 설계 포함. CEO 승인 대기 |
| CUR-GO100-P4A-FEATURE-ENG-001 | — | 03-02 | PASS | ✓ | 200 | V3 교차피처 3개(BB_WIDTH_x_RSI, SEC_LEAD_x_RVOL, DUAL_x_Q2) + 신규피처 4개(NEW_HIGH_52W_WITH_VOL-T001, FORCE_ACC_5D, MKT_SEASON_MONTH, D_D1_D2_ENTRY) 구현. feature_store V3_FEATURE_COLS 33개(향후 확장). 회귀테스트 PASS |
| CUR-GO100-PAPER-TRADING-PREP-001 | — | 03-02 | PASS(조건부) | ✓ | 200 | 30일 모의투자 사전 설정 확인: 세션 2개 ACTIVE(03-03~03-29), 크론 정상, 서비스 running. Telegram 토큰 미설정(CEO 조치 필요) |
| CUR-GO100-P4B-V3-BATCH-REBUILD-001 | — | 03-02 | **PASS** | ✓ | 200 | build_feature_store_batch_v3.py 완성. 242일 배치 완료(307,608건, 12파일, 오류0건). V3 피처 NaN 0%, NEW_HIGH_52W_WITH_VOL 발생률 1.77% |
| CUR-GO100-P4B-V3-BATCH-RESULT-001 | — | 03-03 | **PASS** | ✓ | 200 | V3 배치 최종 결과: 307,608건 × 41컬럼, 12개월 parquet, 소요79분, 오류0건, Q2 샘플 145,520건(47.3%) |
| CUR-GO100-P4C-V3-MODEL-TRAIN-001 | — | 03-03 | **PASS** | ✓ | 200 | V3 모델 학습 완료. 통합 AUC 0.5656(V2+0.025), Q2공격형 AUC 0.6092(목표0.58 초과). V3신규피처 Top15 3개 진입(DUAL_x_Q2 6위, BB_WIDTH_x_RSI 7위, FORCE_ACC_5D 8위). 모델 6종 저장(active:False, CEO 승인 대기) |
| **CUR-GO100-RESEARCH-CORE-BUILD-001** | EVO | 03-04 | **PASS** | ✓ | 200 | Parts 1~3 구현 확인: BacktesterAgent(agent_backtester.py) + StockProfiler(stock_profiler.py) + AnalystAgent(agent_analyst.py) import/단위테스트 ALL PASS |
| **CUR-GO100-RESEARCH-VALIDATE-ORCH-001** | EVO | 03-04 | **PASS** | ✓ | 200 | Part 4 ValidatorAgent D등급 추가(A/B/C/D/F 5단계) 15건 테스트 PASS; Part 5 EvolutionLoop ResearcherAgent 자동 호출(_call_researcher) 통합; **52/52 ALL PASS** |
| **CUR-GO100-RESEARCH-PARAM-SCORE-001** | EVO | 03-04 | **PASS** | ✓ | 200 | Part 6 TypeParamSearcher 신규(type_param_searcher.py) — TYPE-A~D YAML 그리드서치 120/48/27/45 조합; Part 10 HypothesisScorer parse_ceo_overrides+score_and_save 추가; **29/29 ALL PASS** |
| **CUR-GO100-RESEARCH-UI-LAUNCH-001** | EVO | 03-04 | **PASS** | ✓ | 200 | Part 8 research-lab-status 엔드포인트 완전 재설계(evolution_loops/stock_profile_summary/pending_configs DB직접조회); CEO 승인/반려 API 추가(/pending-configs/{id}/approved, rejected); Frontend 빌드 완료 |
| **CUR-GO100-RESEARCH-EVOLUTION-LOOP-001-PART9** | EVO | 03-04 | **PASS** | ✓ | 200 | Part 9 EvolutionLoop._generate_report()+_push_report() 추가; 보고서 자동생성(CUR-GO100-RESEARCH-EVOLUTION-{SEQ:03d}-YYYYMMDD.md) + GitHub push; 테스트 3건 PASS |
| **DIR-GO100-FE-AUDIT-010** | FE | 03-04 | **PASS** | ✓ | 200 | 34개 페이지 전수 감사: STUB/BROKEN 0건, API 연동 갭 10개 식별 |
| **DIR-GO100-FE-API-BIND-011** | FE | 03-04 | **PASS** | ✓ | 200 | GO100 10개 라우터 전수 API 연동 완료 (strategy-cards/portfolios/paper-trading/live-trading/risk/scheduler/optimizer 등) |
| **DIR-GO100-FE-CHARTS-012** | FE | 03-04 | **PASS** | ✓ | 200 | recharts + lightweight-charts 11종 차트 구현 (수익곡선/낙폭/히스토그램/캔들스틱 등) |
| **DIR-GO100-FE-MOBILE-013** | FE | 03-04 | **PASS** | ✓ | 200 | 375/414/768/1024 반응형 완성, PWA manifest 추가 |
| **DIR-GO100-FE-DESIGN-014** | FE | 03-04 | **PASS** | ✓ | 200 | 다크모드 기본, 통일 컬러 팔레트 적용, 백억이 채팅 마크다운+타이핑 인디케이터 |
| **DIR-GO100-FE-FINAL-015** | FE | 03-04 | **PASS** | ✓ | 200 | BRIDGE 최종 통합: E2E API 7라우터 GREEN(strategy-cards/portfolios/paper-trading/live-trading/risk/scheduler/optimizer 200/405), FE 7페이지 auth-redirect 정상(200), API응답시간 최대0.034s(<2s), Git커밋 5cc2eaa3, HANDOVER v14.1, SaaS체크리스트 10항목 작성, closing_report cron 설정파일 준비(root 실행 필요) |

### Phase 6 게이트 검증 결과 (2026-03-02 최종 확인)

| 항목 | 판정 | 비고 |
|------|------|------|
| P6-1 리스크엔진 | **PASS** | go100_risk_rules 3건. risk_engine async_generator 버그 수정 완료. 9단계 테스트 PASS |
| P6-2 KIS 게이트웨이 | **PASS** | go100_live_orders 10건. Mock 주문 BUY/SELL/REJECTED 전 항목 PASS |
| P6-EXTRA-VERIFY | **PASS** | CUR-GO100-P6-EXTRA-VERIFY-001-20260302.md push 완료. E2E 4단계 전 항목 통과 |
| P7-1 QA | **PASS(조건부)** | CUR-GO100-P7-1-FULL-QA-001-20260302.md push 완료. 95/100. 30일 모의투자 1사이클 미완료(장 대기) |

### Agent 도구: **57개** (52+5 신규: bull_bear_debate, get_ai_prediction, get_ai_top_stocks, get_position_sizing, set_position_sizing)

전체 목록:
- **시장·종목:** get_market_overview, get_market_regime, get_global_market, get_stock_price, get_stock_fundamentals, get_investor_flow, get_stock_ohlcv, get_sector_performance, get_sector_correlation, get_top_stocks
- **포트폴리오·전략:** get_portfolio_summary, get_strategy_cards, get_backtest_results, create_strategy_card, run_orderbook_backtest, get_orderbook_backtest_results
- **시그널·갭·경험:** get_cross_market_signals, get_overnight_gap, get_gap_analysis, get_today_gaps, get_experience_similar
- **모의투자:** get_paper_trading_status, start_paper_trading, stop_paper_trading, get_trade_history
- **리포트·목표·프로필:** get_latest_report, get_goal_progress, get_user_profile, get_my_preferences, update_my_preferences
- **메모리:** get_my_memory, remember_this
- **스크리닝:** screen_stocks (35+ 필터)
- **전략 진화·이벤트:** run_strategy_evolution, get_hypotheses, get_events, get_event_impact
- **전략 편집:** edit_strategy_card, confirm_strategy_edit, get_strategy_edit_history
- **자기리뷰:** get_self_review, run_self_review
- **리스크·실주문:** get_risk_status, activate_kill_switch, set_risk_rule, optimize_portfolio, get_portfolio_optimization_history, execute_buy, execute_sell, get_account_balance

### DB migration: 035~065 (16개)

| 마이그레이션 | 테이블/용도 |
|-------------|-------------|
| 035 | go100_strategy_hypotheses (전략 진화) |
| 036 | go100_orderbook_backtest_runs (호가창 백테스트) |
| 037 | go100_events (이벤트 엔진) |
| 038 | go100_strategy_edit_history (전략 편집 이력) |
| 039 | go100_episodic_memory (에피소드 기억) |
| 040 | go100_gap_calibrator (갭 분석) |
| 041 | go100_paper_trading_sessions, go100_paper_trades (30일 모의투자) |
| 043 | go100_agent_self_review (자기리뷰) |
| 044 | go100_portfolio_optimizations (포트폴리오 최적화) |
| 045 | go100_user_preferences (개인화) |
| 046 | go100_risk_rules, go100_risk_events (리스크·킬스위치) |
| 047 | go100_live_orders side 컬럼·인덱스 (KIS 주문 게이트웨이) |
| 048a | go100_position_sizing (동적 포지션 사이징 — P7-2) |
| 048b | go100_strategy_knowledge (전략 지식 베이스) |
| 064 | v4_users agreed_terms·privacy_agreed 컬럼 추가 (SaaS 이용약관 저장 — T-028) |
| 065 | go100_error_log 테이블 (에러 모니터링 미들웨어 — T-031) |

### 크론
- **전체 라인 수**: 약 100라인 (비주석·활성 약 60라인)
- GO100 전용: 무결성 검증, 알림 발송, 일일 요약, 자동 복구, 재무 수집, 모닝/클로징/주간 리포트, 페이퍼 트레이딩, 갭 새로고침, DART 수집 등 (v9 크론 목록 참조)

### 알려진 이슈 (Known Issues)

| # | 이슈 | 심각도 | 상태 |
|---|------|--------|------|
| 1 | collect_financials.py KIS API 403 | HIGH | **우회 완료** — pykrx 폴백 (P1-3) |
| 2 | v4_market_regime_daily 정체 | MED | **자동 복구 연동 완료** — run_auto_heal → heal_regime (P1-3) |
| 3 | ohlcv_daily 크론 로그 경로 | LOW | **해결** — /var/log/go100/ohlcv_daily.log 통일 (P1-3) |
| 4 | go100_fundamentals DART API 키 | LOW | **해결** — DART 발급·.env 설정 |
| 5 | 모닝 브리핑 Telegram | LOW | **해결 완료** — 토큰·채팅 ID 설정, message_id:1981 확인 완료 (2026-03-03) |
| 6 | P6-1 킬스위치 연동 async_generator 오류 | MED | **해결** — risk_engine.py RULE_SECTOR sum/await 버그 수정 완료 (CUR-GO100-P6-EXTRA-VERIFY-001) |
| 7 | pandas 3.0 버전 불일치 (.venv=3.0.1 vs venv=2.3.3) | HIGH | **해결** — indicator_precompute groupby.apply include_groups=False+reset_index(level=0) 패치 (T-017/T-017A/T-023) — 모의투자 크론 정상화 |
| 8 | entry_rules 포맷 불일치 (card_id=35,36) | HIGH | **해결 완료 (T-033B)** — SignalEvaluator._eval_one_entry에 `logic/conditions` 포맷 처리 분기 추가 + go100_strategy_cards card_id=35,36 DB UPDATE 완료 (커밋 ba7f2431, 2026-03-06) |

---

### 프론트엔드 현황 (2026-03-06 기준)
- **페이지**: 45개 전수 LIVE (STUB/BROKEN 0)
- **API 연동**: 10/10 GO100 라우터 GREEN
- **차트**: recharts + lightweight-charts, 11종 차트 구현
- **모바일**: 375/414/768/1024 반응형, PWA manifest
- **디자인**: 다크모드 기본, 통일 컬러 팔레트
- **백억이 채팅**: 마크다운 렌더링, 프로그레스, 타이핑 인디케이터
- **빌드**: Next.js 14, npm run build PASS

---

## 3. 다음 작업

### 완료된 최근 작업
- **[완료] P6-EXTRA-VERIFY**: PASS — 보고서 push 완료 (2026-03-02)
- **[완료] P7-1 QA**: PASS(조건부) — 보고서 push 완료 (2026-03-02)
- **[완료] T-017A/T-023 pandas 3.0 수정**: indicator_precompute 패치 완료 (2026-03-05)
- **[완료] T-024 V3 모델 활성화 준비**: activate_v3_model.py 작성 완료, CEO 승인 후 실행 가능 (2026-03-05)
- **[완료] T-025/T-030 closing_report cron**: generate_closing_report.py + cron 설치 완료 (커밋 f5a286e3)
- **[완료] T-028 agreed_terms DB 수정**: migration 064, SaaS 이용약관 저장 버그 완전 수정 (커밋 4a24b943)
- **[완료] T-029 sitemap.xml**: 44개 URL 동적 생성 완료 (커밋 0060ac99) — 34 → **44페이지** 확인
- **[완료] T-031 에러 모니터링**: error_monitor.py + migration 065 + Telegram 알림 (커밋 758dc8c7)
- **[완료] T-157 토글 UI**: accounts·settings 페이지 실매매/모의 토글 스위치 연동 완료 (커밋 fc398d2d, 2026-03-06)
- **[분석완료] T-033/T-034 entry_rules 검증**: 모의투자 수동실행 0건 원인 확인 — go100_strategy_cards (card_id=35,36)의 entry_rules `logic/conditions/indicator` 포맷이 SignalEvaluator 기대 포맷(`type` 기반)과 불일치 (2026-03-06)

### 즉시 필요 작업
- **[완료] entry_rules 포맷 수정 (T-033B)**: SignalEvaluator + DB UPDATE 완료 (커밋 ba7f2431)
- **[필요] T-034 재실행**: T-033B 완료 후 모의투자 수동 1회 재실행 → 거래 발생 확인 필요

### 중기 작업
- **30일 모의투자 1사이클 완주** (session_id=2, 2026-02-27~03-29)
- **V3 모델 CEO 승인 후 실전 투입**: `python3 scripts/go100/activate_v3_model.py --confirm`
- **소액 실매매 3일 검증** (모의투자 완주 + CEO 승인 후)
- **SaaS 결제 연동** (Stripe/토스페이먼츠, CEO 승인 대기)

---

## 4. 핵심 발견 (누적)

- E2E 23/23 PASS (전 구간 통과)
- Agent 도구 57개, 스크리닝 필터 35+
- 갭 데이터 108,574건 (go100_gap_calibrator)
- 포트폴리오 최적화: Markowitz Sharpe 4.63, Risk Parity Sharpe 4.06
- 리스크 엔진: pre-trade 4종 체크 + 일일 P&L 한도 + Kill Switch
- 자기리뷰: 주간/월간 자동 성과 평가 + 개선안 생성
- DB migration 035~048 (13개 테이블)
- 크론 63+ 라인 활성
- AI Feature Pipeline: DUAL_FLOW_20D, SMALL_CAP_QUALITY, THEME_CYCLE, MarketRegimeEncoder(Q1~Q4) 구현
- Parquet Feature Store: data/go100/features/ 경로, 20개 피처 + 3개 라벨
- 1년치 배치 빌드 완료: 263,450 rows / 12개 월별 Parquet / 15.13MB / 오류 0건 / 306.7s
- 벌크 최적화: 1.8M 쿼리 → ~980 쿼리 (1,880배 절감)
- LightGBM V2 보완: 3-Fold AUC 0.5406±0.0055, MFE_60MIN R²=0.58·Corr=0.78(실전투입 가능), BB_WIDTH 전 모델 1위, 분류+회귀 4모델 저장, 메타데이터 JSON 포함

---

## 5. 보류/미시작

| 항목 | 선행조건 | 우선순위 |
|------|----------|----------|
| ~~P6-EXTRA-VERIFY~~ | ~~보고서 push~~ | **완료 (2026-03-02)** |
| ~~P7-1 전체 QA~~ | ~~보고서 push~~ | **완료 (2026-03-02)** |
| 30일 모의투자 1사이클 | 장 개장 (화요일) | 다음 |
| ~~Phase 4 AI 고도화 설계안~~ | ~~설계만 먼저 보고~~ | **완료 (2026-03-02) — CEO 승인 대기** |
| 소액 실매매 3일 | 모의투자 완주 + CEO 승인 | 그다음 |
| SaaS 준비 | 실매매 검증 | 후순위 |

---

## 6. 웹 Claude 인수인계 절차

1. CEO가 프로젝트명 + HANDOVER.md URL + CEO-DIRECTIVES.md URL 전달
2. 웹 Claude가 모든 URL 크롤링
3. HANDOVER.md 섹션별 상태 파악
4. 상태 보고: (마지막 완료 작업, 현재 단계, 대기 작업, 미해결 이슈, Cursor/Claude Code 참고사항)
5. CEO 추가 지시 대기

---

## 7. 핵심 파일/경로

| 구분 | 경로 |
|------|------|
| 인계서 | /root/project-docs/go100/HANDOVER.md |
| 규칙 | /root/kis-autotrade-v4/.cursorrules, CLAUDE.md |
| 컨텍스트·로드맵 | go100/CONTEXT.md, go100/ROADMAP.md |
| Agent 도구 | backend/app/services/go100/ai/agent_tools.py, tool_executors.py |
| 리스크·주문 | backend/app/services/go100/risk_engine.py, kis_order_gateway.py |
| 마이그레이션 | backend/migrations/035_* ~ 048_* |
| 검증 스크립트 | scripts/go100/test_risk_engine_p6_1.py, test_kis_order_gateway.py |
| AI Feature Engine | backend/app/services/go100/ai/feature_engine.py |
| AI Feature Store | backend/app/services/go100/ai/feature_store.py |
| Feature Pipeline 테스트 | scripts/go100/test_feature_pipeline.py |
| Feature 데이터셋 | data/go100/features/v2/ai_dataset_v2_YYYYMM.parquet |
| AI 학습 스크립트 | scripts/go100/train_ai_model_v2.py |
| AI 모델 V2 | data/go100/models/go100_brain_v2_lightgbm.joblib |
| AI 브레인 V3 예측기 | backend/app/services/go100/ai/brain_predictor_v3.py |
| AI 모델 V3 | data/go100/models/v3/go100_brain_v3_*.joblib |
| 매니저 스냅샷 스크립트 | scripts/go100/generate_manager_snapshot.py |
| 매니저 스냅샷 크론 | scripts/go100/go100_manager_snapshot.cron (30분마다) |
| 매니저 스냅샷 정적 파일 | frontend/public/manager/{snapshot,agents,trades,errors}.json |
| 매니저 스냅샷 공개 URL | https://go100.newtalk.kr/manager/snapshot.json (인증 불필요) |

---

## 8. 검증 명령어

```bash
# 서비스 상태
systemctl status go100

# DB 테이블 확인
sudo -u postgres psql -d kisautotrade -c "\dt go100_*"

# 리스크 규칙·이벤트
sudo -u postgres psql -d kisautotrade -c "SELECT count(*) FROM go100_risk_rules; SELECT count(*) FROM go100_risk_events;"

# 실주문 테이블·기록
sudo -u postgres psql -d kisautotrade -c "SELECT count(*) FROM go100_live_orders;"

# Agent 도구 수
cd /root/kis-autotrade-v4 && .venv/bin/python3 -c "from backend.app.services.go100.ai.agent_tools import get_tool_count; print(get_tool_count())"

# P6-1 리스크 엔진 테스트
.venv/bin/python3 scripts/go100/test_risk_engine_p6_1.py

# P6-2 KIS 게이트웨이 테스트 (Mock)
KIS_MOCK=true .venv/bin/python3 scripts/go100/test_kis_order_gateway.py
```

---

## 9. 참고 문서 (읽기 순서)

1. **이 인계서** (HANDOVER.md)
2. /root/kis-autotrade-v4/.cursorrules, CLAUDE.md
3. go100/ARCHITECTURE.md, DB_SCHEMA.md
4. go100/CONTEXT.md, ROADMAP.md (v10 기준)
5. go100/CEO-DIRECTIVES.md
6. P6-2·Batch 6·7 관련 보고서 (CUR-GO100-*, DESK2-* 등)
7. HANDOVER-20260303-V11.md (아카이브 — v12 직전 스냅샷)
8. HANDOVER-20260228-V10.md (아카이브)

---

## 10. 새 대화창 즉시 투입 체크리스트

1. 이 문서 읽기 완료
2. .cursorrules, CLAUDE.md 읽기
3. **현재 브랜치**: `phase-2c-command-center`
4. 진행률 **98%** — v15.2: T-033/T-034/T-157 entry_rules 검증·토글UI 완료, entry_rules 포맷 수정(T-033) 필요
5. **다음 우선순위**: T-033 entry_rules DB 수정 (card_id=35,36) → T-034 재실행 (거래 발생 확인) → V3 CEO 승인 → 모의투자 1사이클 완주
6. 상태 확인: `systemctl status go100 && systemctl status go100-frontend`, `psql -d kisautotrade -c "\\dt go100_agent*"`
7. 환경 확인: KIS_APP_KEY, KIS_APP_SECRET, DART_API_KEY, GO100_TELEGRAM_* (.env)
8. **V3 모델 활성화**: CEO 승인 후 `python3 scripts/go100/activate_v3_model.py --confirm && sudo systemctl restart go100`
9. **프론트엔드 현황**: **45페이지** LIVE, API 10/10 연동, 차트 11종, 모바일 PWA 완성, Commander 대시보드 추가 (진행률 98%)
10. **pandas 환경**: .venv=3.0.1(크론 사용), venv=2.3.3(직접 실행) — indicator_precompute 패치 완료
11. **entry_rules 이슈**: go100_strategy_cards card_id=35,36 — `logic/conditions` 포맷 → `[{"type":"ma_cross",...}]` 포맷으로 DB UPDATE 필요

---

## 11. Commander Architecture 현황 (2026-03-06 완료)

### 커맨더 백억이 아키텍처
- **브랜치**: `phase-2c-command-center`
- **에이전트 수**: 10개 (BaseAgent + 9 특화 에이전트)
- **파일 위치**: `/root/kis-autotrade-v4/backend/app/services/go100/agents/`
- **대시보드 URL**: `go100.newtalk.kr/go100/commander` (T-036/T-037 구현 완료)

| 에이전트 파일 | 역할 |
|---|---|
| `base_agent.py` | 기반 클래스 (LLMGateway, DB 접근, JSON 출력) |
| `news_agent.py` | 뉴스/공시 분석 (go100_news_items) |
| `regime_agent.py` | 시장 레짐 판단 (BULL/BEAR/NEUTRAL) |
| `risk_agent.py` | 리스크 사전 평가 (진입 허용/거부) |
| `supply_demand_agent.py` | 수급 분석 (외인/기관 추세) |
| `technical_agent.py` | 기술적 분석 (MA/RSI/MACD/BB) |
| `bull_agent.py` | 강세 논거 구성 |
| `bear_agent.py` | 약세 논거 구성 |
| `debate.py` | 3라운드 Bull/Bear 토론 + 판정 |
| `agent_desk2~5.py` | DESK별 특화 에이전트 (4개) |
| `agent_researcher.py` | 가설 생성 리서처 |
| `agent_backtester.py` | 백테스트 에이전트 |
| `agent_performance_tracker.py` | 에이전트 성과 추적 + 동적 가중치 |
| `commander.py` | 컨트롤 타워 (최종 판단) |

### 신규 DB 테이블
| 테이블 | 용도 |
|---|---|
| `go100_agent_reports` | 에이전트별 분석 보고서 |
| `go100_debate_log` | Bull/Bear 토론 기록 |
| `go100_agent_performance` | 에이전트 성과·가중치 |

### 자기 진화 루프
- **가중치 추적 에이전트 키**: 9개 (regime, supply_demand, technical, news, risk, desk5, desk4, desk3, desk2) — 기존 5 → 9 (desk5/4/3/2 추가)
- 20거래일 롤링 정확도 → 동적 가중치 조정 (MIN 0.3, MAX 2.0)
- LightGBM 재학습 크론: 20일 주기 (docs/go100_lightgbm_retrainer.cron)
- 커맨더 자기 비평: `commander_self_critique` → `go100_agent_reports` 저장

### 모드 전환
```bash
# .env에 추가하여 커맨더 모드 ON/OFF
GO100_COMMANDER_MODE=true   # 커맨더 모드 활성화
GO100_COMMANDER_MODE=false  # 기존 백억이 단독 모드
```

---

## 12. SaaS 런칭 준비 체크리스트 (2026-03-05 기준)

| # | 항목 | 상태 | 비고 |
|---|------|------|------|
| 1 | 회원가입 플로우 | ✅ 완료 | T-028 완료 — migration 064, v4_users 컬럼 추가, auth_router/social_auth_router INSERT 수정, E2E PASS (커밋 4a24b943) |
| 2 | 결제 연동 | ⚠️ 설계 완료 | T-021 설계서 완료 — 토스페이먼츠(국내) + Stripe(해외), CEO 승인 대기 |
| 3 | 구독 플랜 관리 | ⚠️ 설계 완료 | T-021 설계서 완료 — Free/Pro(29,000원/월)/Premium(79,000원/월), CEO 승인 대기 |
| 4 | 마켓플레이스 | ⚠️ 설계 완료 | T-021 설계서 완료 — go100_marketplace_listings DB 스키마, 판매자/평점/승인 플로우, CEO 승인 대기 |
| 5 | 이용약관 최신화 | ✅ 완료 | /terms 페이지 정식 구현 완료 (2026-02-20, T-013 확인) |
| 6 | 개인정보처리방침 | ✅ 완료 | /privacy 페이지 정식 구현 완료 (2026-02-20, T-013 확인) |
| 7 | 고객지원 채널 | 미구현 | 카카오톡/이메일 채널 미개설 |
| 8 | 온보딩 튜토리얼 | 미구현 | 첫 로그인 시 가이드 화면 없음 |
| 9 | SEO/OG 태그 | ✅ 완료 | T-020 OG/robots 완료(71f51ebe) + T-029 sitemap.xml **45개** URL 동적 생성(0060ac99) + T-036 commander 페이지 추가 — Google Search Console 등록 권장 |
| 10 | 에러 모니터링 | ✅ 완료 | T-031 완료 — 자체 에러 모니터링 미들웨어(error_monitor.py) + go100_error_log 테이블(migration 065) + Telegram 알림(message_id 8525) (커밋 758dc8c7) |

> SaaS 전환 우선순위: 1(agreed_terms 저장 버그 수정), 2, 3, 4, 7, 8 항목. 5, 6은 완료. 나머지는 런칭 전 QA 단계 점검.

---

---

## Phase 8 로드맵 (2026-03-05 기준)

### 목표: 30일 모의투자 완주 → V3 실전 투입 → SaaS 준비

| 단계 | 태스크 | 선행조건 | 목표일 | 상태 |
|------|--------|----------|--------|------|
| Phase 8-1 | T-025 closing_report cron 등록 | root 실행 | 03-06 | 대기 |
| Phase 8-1 | T-026 모의투자 크론 검증 (장중 매수) | T-025 | 03-06 | 대기 |
| Phase 8-2 | 30일 모의투자 1사이클 완주 (session_id=2) | pandas 패치 확인 | 03-29 | 진행중 |
| Phase 8-2 | V3 모델 CEO 승인 후 실전 투입 (activate_v3_model.py --confirm) | CEO 승인 | 미정 | CEO 대기 |
| Phase 8-3 | 자기리뷰 1사이클 (weekly_review) | 모의투자 1주 이상 | 03-14 | 대기 |
| Phase 8-3 | Telegram 모의투자 알림 확인 | T-026 | 03-06 | 대기 |
| Phase 8-4 | 소액 실매매 3일 검증 | 모의투자 완주 + CEO 승인 | 미정 | 대기 |
| Phase 8-5 | SaaS agreed_terms 저장 버그 수정 (T-013) | — | 미정 | 대기 |
| Phase 8-5 | SaaS 결제 연동 (Stripe/토스페이먼츠) | — | 미정 | 미착수 |
| Phase 8-6 | 최종 SaaS QA + 라이브 런칭 | Phase 8-1~5 완료 | 미정 | 미착수 |

### Phase 8 우선순위
1. **즉시**: T-025/T-026 closing_report cron (root 실행, 5분)
2. **이번 주**: 모의투자 장중 매수 신호 발생 확인 (ConvictionScore≥0.6)
3. **이번 달**: 모의투자 1사이클 완주 + 성과 리뷰
4. **다음**: CEO 승인 후 V3 실전 투입

---

## 버전 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| v1.0 | 02-23 | 초판 |
| v2.0 | 02-24 | 접속정보·계정·서비스 명령 추가 |
| v3.0 | 02-25 | 아키텍처·DB 스키마·이슈 추가 |
| v4.0 | 02-25 | V4.1 서비스 경계 명확화 |
| v5.0 | 02-25 | 크론·파일 구조 대폭 보강 |
| v6.0 | 02-25 | Batch 2 반영, 세션2 인계 |
| v7.0 | 02-28 | Batch 3 완료 반영 |
| v8.0 | 02-28 | Batch 4 완료 반영 |
| v9.0 | 02-28 | Batch 4·5 완료, 진행률 72% |
| v10.0 | 02-28 | Batch 6·7 반영, 진행률 85% |
| v10.1 | 02-28 | 단일 파일 통합, 테이블 표준화, 핵심 발견·보류·웹 Claude 절차·버전 이력 추가 |
| v10.2 | 03-01 | Batch 8 AI LightGBM V2 학습 반영, 모델 경로·다음 작업 추가 |
| v10.4 | 03-02 | [SHARED] DB 스키마 카탈로그 통합(246테이블+8뷰=254, go100_* 70개 포함), 자동최신화 cron |
| v10.3 | 03-01 | AI 보완판: 3-Fold WF, EDA, 다중타겟 회귀 3종, MFE_60MIN 실전 수준 확인 |
| v10.5 | 03-02 | genspark_bridge.py 3종 버그 수정, 백억이 총괄매니저 세션 시작 보고 완료 |
| v10.6 | 03-02 | P6-EXTRA-VERIFY PASS + P7-1 QA PASS(95/100): risk_engine async_generator 버그 수정, E2E 검증 완료, Agent도구 52개 확인, Phase 6 게이트 완전 통과, 진행률 90% |
| v10.7 | 03-02 | Phase 4 AI 모델 고도화 설계안 완료(CUR-GO100-P4-AI-ENHANCE-DESIGN-001): 4개 축 설계(교차피처/멀티타겟/Regime분리/Threshold최적화), 구현 12일 계획, CEO 승인 대기 |
| v10.8 | 03-02 | CEO P0 수급 데이터 전수 조사 완료(CUR-GO100-SUPPLY-DEMAND-AUDIT-001): 10개 테이블, 275K 투자자수급, 이슈 2건(orderbook_daily_stats 0건, 02-28 갭), CTE L3.3 반영 정상 확인 |
| v10.9 | 03-02 | P4-A 피처 엔지니어링 완료(CUR-GO100-P4A-FEATURE-ENG-001): V3 교차피처 3개+신규피처 4개=7개 추가, feature_store 23→30개, 회귀 PASS. 30일 모의투자 사전 설정 확인(CUR-GO100-PAPER-TRADING-PREP-001): 세션 2개 ACTIVE, Telegram토큰 미설정-CEO조치필요 |
| v10.10 | 03-02 | P4-B V3 배치 빌드 스크립트 완료(CUR-GO100-P4B-V3-BATCH-REBUILD-001): build_feature_store_batch_v3.py 완성, 1일 테스트 PASS(498종목 경고0건), 1년치 배치 실행 중(242일, PID 1672851) |
| v11.0 | 03-03 | P4-B 배치 완료(307,608건·오류0) + P4-C V3 모델 학습 완료: 통합 AUC 0.5656(V2+0.025), Q2공격형 AUC 0.6092(목표초과), V3 신규피처 Top15 3개 진입. 모델 6종 저장(active:False, CEO 승인 대기). train_ai_model_v3.py 커밋 21af802d |
| v13.0 | 03-04 | BRIDGE 갱신: 기준일 03-03, 진행률 92%, go100_* 70테이블, migration 048a/b 추가, 도구 57개, brain_predictor_v3.py 경로, 가중치 에이전트 9개, Telegram Known Issue #5 해결 완료, feature 33개(향후) |
| v13.1 | 03-04 | **DIR-GO100-PAPER-TRADING-V3-003-R3 완료**: run_paper_trading_v3.py V3 Brain 연동 검증(ConvictionScore≥0.6 필터/상위3종/risk_engine.check_pre_trade() 통합/Telegram 3종 알림), cron 3건 등록(매수09:10/매도15:15/주간리뷰금16:30 KST), dry-run 3모드 PASS(주문미발생+Telegram HTTP 200), 세션 session_id=2 ACTIVE(원금 10,000,000원), 첫 거래일 모니터링 체크리스트 작성 |
| v12.0 | 03-03 | **Commander Architecture 완료** (DIR-001~DIR-009): 에이전트 10개 배포 완료(base/news/regime/risk/supply_demand/technical/bull/bear/debate/desk2~5/researcher/backtester/commander), 자기진화루프(agent_performance_tracker, 동적가중치), V3 모델 활성화(active:True, ai_scorer.py V3 업데이트), Telegram 확인(message_id:1981), 페이퍼트레이딩 V3 크론 등록(go100_morning_briefing/go100_paper_trading), git 권한 정리(/root o+x, safe.directory 설정) |
| v14.1 | 03-04 | **DIR-015 BRIDGE 최종 E2E 검증 완료**: E2E API 7라우터 전수 GREEN(strategy-cards/portfolios/paper-trading/live-trading 200, risk/scheduler/optimizer 422/405/200), FE 7페이지 auth-redirect 정상(login 200), API 응답시간 전수 <0.04s(최대 paper-trading 0.034s), Git 커밋 5cc2eaa3, SaaS 체크리스트 10항목 작성 및 HANDOVER 섹션12 추가, closing_report cron 설정 완료(root 실행 필요: /etc/cron.d/go100_closing_report), 진행률 97% 확정 |
| v14.2 | 03-05 | **Group A 감사 완료 (T-012~T-016)**: 모의투자 세션 ACTIVE 확인(거래0건 크론미발화), SaaS 인증 감사(agreed_terms 미저장 버그 식별, 이용약관/개인정보 페이지 완성 확인), API 전수 헬스체크(122경로 ALL GREEN), FE 44페이지 전수 점검(protected 307/public 200 정상), SaaS 체크리스트 #1/5/6 상태 업데이트 |
| v15.3 | 03-06 | **Commander 군단 대시보드 구현 + 페이지 45개**: T-036 Commander 대시보드 구현(go100.newtalk.kr/go100/commander) + T-037 API 연동 + T-038 HANDOVER 갱신. 페이지 수 44→45, Commander Architecture §11 URL 추가, SaaS 체크리스트 #9 45개 갱신 |
| v15.2 | 03-06 | **entry_rules 검증 + T-157 토글UI + 전체 세션 종합**: T-157 실매매/모의 토글 스위치 연동(커밋 fc398d2d), T-033/T-034 entry_rules 포맷 불일치 진단·수동실행 0건 확인, 페이지 수 34→44 갱신, migration 범위 035~065 갱신(064/065 추가), Known Issues #8 추가, 다음 작업 섹션 전면 갱신 |
| v15.1 | 03-05 | **SaaS 버그수정+SEO+에러모니터링 (T-028~T-031)**: agreed_terms DB 저장 버그 완전 수정(migration 064), sitemap.xml 44개 URL 동적 생성, closing_report cron 검증, 에러 모니터링 미들웨어+Telegram 알림 구현(migration 065). SaaS 체크리스트 #1/#9/#10 완료 |
| v15.0 | 03-05 | **pandas 3.0 수정 + V3 모델 준비 (T-017A/T-023/T-024)**: indicator_precompute groupby.apply include_groups=False 패치(pandas 2.x/3.x 호환), paper_trading_engine_30d 방어적 수정, 수동 1회 실행 PASS(exit 0), V3 모델 6종 로드 성공(active:True), activate_v3_model.py 스크립트 작성(CEO 승인 대기), Known Issues #7 추가, Phase 8 로드맵 신설, 진행률 98% |

### v14.1 추가 완료 작업 (2026-03-05)
| Task ID | 날짜 | 내용 | 상태 |
|---------|------|------|------|
| T-001 | 03-05 | 미푸시 보고서 push + closing-report cron 등록 | PASS |
| T-002 | 03-05 | V3 모의투자 첫 매수 검증 | PASS |
| T-003 | 03-05 | Nginx WebSocket/SSE 감사 | PASS |
| T-004 | 03-05 | HANDOVER v14 + FE 재시작 | PASS |
| DIR-FE-RESTORE-016 | 03-04 | dashboard 래퍼 복원 + lib/go100 중복 삭제 (e92e5315) | PASS |
| DIR-010-C | 03-04 | src/go100 전수 파일목록 (95파일 11,086줄) | PASS |

### v14.1 추가 완료 작업 (2026-03-05) — T-006~T-009 인프라정리
| Task ID | 날짜 | 내용 | 상태 |
|---------|------|------|------|
| T-006 | 03-05 | project-docs git 권한 복구 + 미push 일괄 반영 | PASS |
| T-007 | 03-05 | go100-frontend 서비스 재시작 + 빌드 적용 | PASS |
| T-008 | 03-05 | V3 모의투자 + closing cron + Nginx WS/SSE 통합 감사 | PASS |
| T-009 | 03-05 | HANDOVER v14.1 최종 정리 | PASS |

### v14.2 추가 완료 작업 (2026-03-05) — T-012~T-016 Group A 감사
| Task ID | 날짜 | 내용 | 상태 |
|---------|------|------|------|
| T-012 | 03-05 | 모의투자 세션 상태 정밀 점검 (session_id=2 ACTIVE, 거래 0건, 크론 미발화 확인) | PASS |
| T-013 | 03-05 | SaaS 회원가입·인증 플로우 감사 (이메일/소셜 코드 완성, agreed_terms 미저장 버그 발견, 이용약관·개인정보 페이지 확인) | PASS |
| T-014 | 03-05 | GO100 API 전수 헬스체크 (122경로, GET 37개 401정상/공개 2개 200, 응답시간 전수 <0.06s) | PASS |
| T-015 | 03-05 | FE 전수 페이지 접근 테스트 (44페이지: public 200/protected 307, TODO/STUB 0건) | PASS |
| T-016 | 03-05 | HANDOVER v14.2 업데이트 및 최종 보고 | PASS |

### v15.0 추가 완료 작업 (2026-03-05) — T-017A/T-023/T-024 pandas 패치+V3모델 준비 + T-018~T-022 모의투자검증+SEO+결제설계
| Task ID | 날짜 | 내용 | 상태 |
|---------|------|------|------|
| T-017A | 03-05 | stock_code KeyError 버그 원인 분석 — pandas 3.0.1 groupby.apply 그룹키 제외 확인 (분석 전용, 수정 없음) | PASS |
| T-017B | 03-05 | paper_trading_engine_30d.py 방어적 수정 — `SELECT stock_code AS stock_code` + `row["stock_code"]` (커밋 f8bd2bee) | PASS |
| T-023 | 03-05 | pandas 3.0 패치 검증 + 수동 1회 실행 — .venv(pandas 3.0.1)에서 indicator_precompute PASS, session_id=2 exit code 0 확인 | PASS |
| T-024 | 03-05 | V3 모델 파일 검증 + 활성화 스크립트 작성 — 6종 로드 성공(active:True), activate_v3_model.py 작성·chmod+x (커밋 de3456c6) | PASS(CEO 승인 대기) |
| T-025 | 03-05 | closing_report 자동화 스크립트 — generate_closing_report.py + go100_closing_report.cron 작성 | 대기 |
| T-026 | 03-05 | T-025 후속 검증 및 크론 등록 | 대기 |
| T-027 | 03-05 | HANDOVER v15.0 업데이트 — T-017A~T-026 반영, Known Issues #7 추가, Phase 8 로드맵 추가 | PASS |
| T-018 | 03-05 | 모의투자 엔진 정밀 검증 — 크론 정상, 패치 후 실행 PASS, entry_rules 포맷 불일치(거래 0건) | PASS(조건부) |
| T-019 | 03-05 | agreed_terms 저장 버그 수정 | 추가 조치 필요 (미완료) |
| T-020 | 03-05 | SEO/OG 메타태그 전수 적용 — layout.tsx OG/keywords/robots, robots.txt 생성 (커밋 71f51ebe) | PASS |
| T-021 | 03-05 | SaaS 결제·구독 아키텍처 설계 — Free/Pro/Premium 3플랜, 토스/Stripe, DB 스키마 4종 | PASS(설계 완료, CEO 승인 대기) |
| T-022 | 03-05 | HANDOVER v15.0 T-018~T-022 반영 — SaaS 체크리스트 #1/#2/#3/#4/#9 업데이트 | PASS |
| T-028 | 03-05 | agreed_terms/privacy DB 저장 버그 완전 수정 — migration 064, v4_users 컬럼 추가, auth/social INSERT 수정 (커밋 4a24b943) | PASS |
| T-029 | 03-05 | sitemap.xml 동적 생성 + SEO 완성 — **44개** URL, MetadataRoute.Sitemap, 빌드 PASS (커밋 0060ac99) — 페이지 수 34→44 확인 | PASS |
| T-030 | 03-05 | closing_report 크론 설치 검증 — cron 등록 확인, 자동 실행 검증 (커밋 f5a286e3) | PASS |
| T-031 | 03-05 | 에러 모니터링 미들웨어 구현 — error_monitor.py + migration 065 + Telegram 알림(Msg 8525) (커밋 758dc8c7) | PASS |
| T-032 | 03-05 | HANDOVER v15.1 업데이트 — T-028~T-031 SaaS+SEO+크론+모니터링 반영 | PASS |

### v15.3 추가 완료 작업 (2026-03-06) — T-033B entry_rules 정규화 + T-036/T-037 Commander 대시보드 + T-038 HANDOVER v15.3 + T-039 매니저 스냅샷 + T-040 HANDOVER 갱신
| Task ID | 날짜 | 내용 | 상태 |
|---------|------|------|------|
| T-033B | 03-06 | entry_rules 포맷 정규화 — SignalEvaluator._eval_one_entry `logic/conditions/indicator` 포맷 처리 분기 추가 + go100_strategy_cards card_id=35,36 DB UPDATE 완료 (커밋 ba7f2431) | PASS |
| T-036 | 03-06 | Commander 군단 대시보드 구현 — /go100/commander 페이지 신규, 에이전트 10개 실시간 상태/가중치 표시, agent_performance_tracker API 연동 | PASS |
| T-037 | 03-06 | Commander 대시보드 프론트엔드 완성 — 페이지 수 44→45, API 엔드포인트 연동, 에이전트 성과 차트 구현 | PASS |
| T-038 | 03-06 | HANDOVER v15.3 업데이트 — Commander 대시보드 반영, 페이지 수 45, Commander Architecture §11 URL 추가 | PASS |
| T-039 | 03-06 | 매니저 스냅샷 생성기 — generate_manager_snapshot.py (T-039) 구현, frontend/public/manager/*.json 30분마다 갱신, go100_manager_snapshot.cron 등록. CEO·외부 AI용 공개 URL https://go100.newtalk.kr/manager/snapshot.json | PASS |
| T-040 | 03-06 | HANDOVER v15.3 갱신 — T-033B~T-040 결과 전체 반영, Known Issue #8 해결 표시, 매니저 스냅샷 URL 추가, CONTEXT.md 동기화 | PASS |

### v15.2 추가 완료 작업 (2026-03-06) — T-033/T-034 entry_rules 검증 + T-157 토글UI
| Task ID | 날짜 | 내용 | 상태 |
|---------|------|------|------|
| T-157 | 03-06 | 실매매/모의 토글 스위치 accounts·settings 페이지 실제 연동 — POST /api/v4/admin/switch-account-mode 백엔드 연결, 확인 다이얼로그 추가 (커밋 fc398d2d) | PASS |
| T-033 | 03-06 | entry_rules 포맷 불일치 진단 — SignalEvaluator._eval_one_entry `type` 기반 vs go100_strategy_cards card_id=35,36 `logic/conditions/indicator` 포맷 불일치 확인. **수정 미완료** (DB UPDATE 또는 코드 확장 필요) | PASS(진단) / 수정 대기 |
| T-034 | 03-06 | 모의투자 수동 1회 매수 트리거 — session_id=2, KOSPI 80종목, run_paper_trading_v3.py --mode buy 실행, 결과 **매수 0건** (entry_rules 포맷 불일치 확인) | PASS(확인) |
| T-035 | 03-06 | HANDOVER v15.2 업데이트 — T-029~T-034, T-157 전체 반영, 페이지 수 44, migration 035~065, entry_rules Known Issue #8 추가 | PASS |
| T-036 | 03-06 | Commander 군단 대시보드 구현 — /go100/commander 페이지 신규 구현, 에이전트 10개 실시간 상태/가중치 표시, agent_performance_tracker API 연동 | PASS |
| T-037 | 03-06 | Commander 대시보드 프론트엔드 완성 — 페이지 수 44→45, API 엔드포인트 연동, 에이전트 성과 차트 구현 | PASS |
| T-038 | 03-06 | HANDOVER v15.3 업데이트 — T-036/T-037 Commander 대시보드 반영, 페이지 수 45, Commander Architecture §11 URL 추가 | PASS |
