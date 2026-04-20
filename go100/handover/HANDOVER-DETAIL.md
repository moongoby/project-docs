# GO100 인수인계서 L2 — 상세 정보
> 최종 업데이트: 2026-04-20 | v18.2
> 요약 → [HANDOVER.md](HANDOVER.md) | 이력 → [HANDOVER-ARCHIVE.md](HANDOVER-ARCHIVE.md)

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
| DB | PostgreSQL 16, kisautotrade / kis_admin @ localhost:5432 |
| 서비스 | go100(FastAPI 8002), Next.js 3000, Redis 6379, Nginx |
| API 키 | .env: KIS_APP_KEY, KIS_APP_SECRET, DART_API_KEY, GO100_TELEGRAM_BOT_TOKEN, GO100_TELEGRAM_CHAT_ID |
| 모델 | V3 Brain (AUC 0.5656), data/go100/models/v3/ |

---

## 2. 완료 작업 테이블 (v15.0~v17.0, 2026-03-05~03-09)

| Task ID | 날짜 | 내용 | 상태 |
|---------|------|------|------|
| T-017A/B | 03-05 | pandas 3.0.1 groupby.apply 패치 (indicator_precompute, paper_trading_engine_30d) | PASS |
| T-023 | 03-05 | pandas 패치 검증 + 수동 1회 실행 PASS | PASS |
| T-024 | 03-05 | V3 모델 파일 검증 + activate_v3_model.py 작성 | PASS |
| T-025/T-030 | 03-05 | closing_report cron 설치 (커밋 f5a286e3) | PASS |
| T-028 | 03-05 | agreed_terms/privacy DB 저장 버그 수정 — migration 064 (커밋 4a24b943) | PASS |
| T-029 | 03-05 | sitemap.xml 44개 URL 동적 생성 (커밋 0060ac99) | PASS |
| T-031 | 03-05 | 에러 모니터링 미들웨어 + migration 065 + Telegram 알림 (커밋 758dc8c7) | PASS |
| T-033B | 03-06 | entry_rules 포맷 정규화 — SignalEvaluator + DB UPDATE (커밋 ba7f2431) | PASS |
| T-036/T-037 | 03-06 | Commander 군단 대시보드 /go100/commander (페이지 44→45) | PASS |
| T-039 | 03-06 | 매니저 스냅샷 generate_manager_snapshot.py, 공개 URL 등록 | PASS |
| T-046 | 03-06 | 어드민 시그널·리스크 + 매매 관리 + 거래 상세 페이지 (페이지 45→48) (커밋 b8f247ca) | PASS |
| T-051 | 03-09 | 능력 전면 개방 — Agent Loop 20R/10T, 환각 방지 hallucination_guard.py | PASS |
| T-052 | 03-09 | 전략 카드 대량 생산 — 5레짐 7전략(strategy_cards 42→49), 커밋 efbc58ce | PASS |
| T-053 | 03-09 | 모의투자 세션 3~7 가동 (session_id 3~7 ACTIVE) | PASS |
| T-054 | 03-09 | Admin War Room 메인 + 스텁 11개 | PASS |
| T-055 | 03-09 | HANDOVER v17.0 갱신 (최종) | PASS |

### 03-09 이후 커밋 반영 (2026-03-09~04-20)

| 날짜 | 커밋 | 내용 |
|------|------|------|
| **04-20** | **6bd70fdb** | **GO100-V5-P2-9: 사이트맵 경로 리다이렉트 10개 추가** (/ai/chat → /llm 등) |
| **04-20** | **ebab09fa** | **GO100-V5-P2-3: /backtest/[id] 사용자용 백테스트 상세 페이지 생성** |
| 03-27 | `958e29b` | Phase 3 — run_unified_engine에 load_active_strategy_cards 통합 |
| 03-27 | `ff74b54` | Phase 1 — 전략카드 기반 CTE 파이프라인 구축 (backend submodule) |
| 03-23 | `3a3a8d6` | v4_desk_config 시드 데이터 + 스케줄러 에러 로그 |
| 03-23 | `947c0cc` | paper trading monitor dashboard 신규 구현 |
| 03-23 | `fd1b5a5` | backtest result dashboard with charts |
| 03-23 | `0f7d44f` | hypothesis center search/filter 강화 (2회 커밋) |
| 03-23 | `089de17` | bridge: go100_strategy_hypotheses → v4_hav_hypotheses on PASS |
| 03-23 | `19834a9` | flock lock + PID guard for backtest worker dedup |
| 03-23 | `65e5369` | P0 cron path + pipeline promote stage + backtest dedup fix |
| 03-16 | `14766a0` | 뉴스매매 백테스트 분석 결과 및 진화 메모리 추가 |

---

## 3. 아키텍처

### Commander Architecture
- 에이전트 수: 10개 (BaseAgent + 9 특화)
- 파일 위치: `/root/kis-autotrade-v4/backend/app/services/go100/agents/`
- 대시보드: `go100.newtalk.kr/go100/commander`

| 에이전트 파일 | 역할 |
|---|---|
| `base_agent.py` | 기반 클래스 (LLMGateway, DB 접근, JSON 출력) |
| `news_agent.py` | 뉴스/공시 분석 |
| `regime_agent.py` | 시장 레짐 판단 (BULL/BEAR/NEUTRAL) |
| `risk_agent.py` | 리스크 사전 평가 |
| `supply_demand_agent.py` | 수급 분석 (외인/기관) |
| `technical_agent.py` | 기술적 분석 (MA/RSI/MACD/BB) |
| `bull_agent.py` / `bear_agent.py` | 강세/약세 논거 |
| `debate.py` | 3→5라운드 Bull/Bear 토론 + 판정 |
| `commander.py` | 컨트롤 타워 (최종 판단) |

### AI 모델 현황
| 버전 | 상태 | AUC | 경로 |
|------|------|-----|------|
| V2 | 대기 | 0.5406 | data/go100/models/go100_brain_v2_lightgbm.joblib |
| V3 | **ACTIVE** | **0.5656** | data/go100/models/v3/go100_brain_v3_*.joblib |

### 능력 전면 개방 환경 변수 (.env)
```
GO100_AGENT_MAX_ROUNDS=20
GO100_AGENT_MAX_TOOLS_PER_ROUND=10
GO100_AGENT_UNLIMITED_MODE=true
GO100_PAPER_TRADING_ENABLED=true
GO100_LIVE_TRADING_ENABLED=false
GO100_LIVE_TRADING_REQUIRES_CEO=true
GO100_DEBATE_ROUNDS=5
```

---

## 4. DB Migration 현황 (035~065)

| 마이그레이션 | 테이블/용도 |
|-------------|-------------|
| 035 | go100_strategy_hypotheses |
| 036 | go100_orderbook_backtest_runs |
| 037 | go100_events |
| 038 | go100_strategy_edit_history |
| 039 | go100_episodic_memory |
| 040 | go100_gap_calibrator |
| 041 | go100_paper_trading_sessions, go100_paper_trades |
| 043 | go100_agent_self_review |
| 044 | go100_portfolio_optimizations |
| 045 | go100_user_preferences |
| 046 | go100_risk_rules, go100_risk_events |
| 047 | go100_live_orders side 컬럼·인덱스 |
| 048a | go100_position_sizing |
| 048b | go100_strategy_knowledge |
| 064 | v4_users agreed_terms·privacy_agreed 컬럼 |
| 065 | go100_error_log |

---

## 5. Agent 도구 목록 (57개)

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
- **AI 예측:** get_ai_prediction, get_ai_top_stocks, get_position_sizing, set_position_sizing, bull_bear_debate

---

## 6. 핵심 파일 경로

| 구분 | 경로 |
|------|------|
| Agent 도구 | backend/app/services/go100/ai/agent_tools.py |
| 리스크 엔진 | backend/app/services/go100/risk_engine.py |
| KIS 주문 게이트웨이 | backend/app/services/go100/kis_order_gateway.py |
| AI Brain V3 예측기 | backend/app/services/go100/ai/brain_predictor_v3.py |
| Feature Engine | backend/app/services/go100/ai/feature_engine.py |
| Feature Store | backend/app/services/go100/ai/feature_store.py |
| 환각 방지 | backend/app/services/go100/ai/hallucination_guard.py |
| 마이그레이션 | backend/migrations/035_* ~ 065_* |
| V3 모델 | data/go100/models/v3/ |
| Feature 데이터셋 | data/go100/features/v2/ai_dataset_v2_YYYYMM.parquet |
| 매니저 스냅샷 | frontend/public/manager/{snapshot,agents,trades,errors}.json |
| 매니저 스냅샷 URL | https://go100.newtalk.kr/manager/snapshot.json |

---

## 7. 프론트엔드 현황 (2026-03-09 기준)

- 페이지: **48개** LIVE (Admin War Room 포함)
- API 연동: 10/10 GO100 라우터 GREEN
- 차트: recharts + lightweight-charts, 11종
- 모바일: 375/414/768/1024 반응형, PWA manifest
- 디자인: 다크모드, 통일 컬러 팔레트
- 빌드: Next.js 14, npm run build PASS

---

## 8. 알려진 이슈 (현재 미해결)

| # | 이슈 | 심각도 | 상태 |
|---|------|--------|------|
| 1~8 | 모두 해결 완료 | — | [L3 아카이브 참조](HANDOVER-ARCHIVE.md#known-issues) |
| 9 | 30일 모의투자 1사이클 미완주 | MED | 기간 만료 (03-29) — 결과 검토 필요 |

---

## 9. SaaS 런칭 체크리스트

| # | 항목 | 상태 |
|---|------|------|
| 1 | 회원가입 플로우 (agreed_terms) | ✅ 완료 (T-028) |
| 2 | 결제 연동 | ⚠️ 설계 완료, CEO 승인 대기 |
| 3 | 구독 플랜 관리 | ⚠️ 설계 완료, CEO 승인 대기 |
| 4 | 마켓플레이스 | ⚠️ 설계 완료, CEO 승인 대기 |
| 5 | 이용약관 | ✅ 완료 |
| 6 | 개인정보처리방침 | ✅ 완료 |
| 7 | 고객지원 채널 | ❌ 미구현 |
| 8 | 온보딩 튜토리얼 | ❌ 미구현 |
| 9 | SEO/OG 태그 | ✅ 완료 (T-020/T-029) |
| 10 | 에러 모니터링 | ✅ 완료 (T-031) |

---

## 10. 검증 명령어

```bash
# 서비스 상태
systemctl status go100

# DB 테이블 확인
sudo -u postgres psql -d kisautotrade -c "\dt go100_*"

# 리스크 규칙
sudo -u postgres psql -d kisautotrade -c "SELECT count(*) FROM go100_risk_rules;"

# Agent 도구 수
cd /root/kis-autotrade-v4 && .venv/bin/python3 -c "from backend.app.services.go100.ai.agent_tools import get_tool_count; print(get_tool_count())"

# 모의투자 세션 상태
sudo -u postgres psql -d kisautotrade -c "SELECT session_id, status FROM go100_paper_trading_sessions ORDER BY session_id;"
```
