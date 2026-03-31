# GO100 인수인계서 L3 — 이력 아카이브
> 최종 업데이트: 2026-03-30 | v18.0 (3계층 전환 시 v17.0 전체 보존)
> 요약 → [HANDOVER.md](HANDOVER.md) | 상세 → [HANDOVER-DETAIL.md](HANDOVER-DETAIL.md)

---

## 필수 규칙 (v17.0 원본 보존)

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

## 완료 작업 테이블 (Batch 1~7, 2026-02-27~03-04)

| Task ID | Batch | 날짜 | 점수 | 핵심 결과 |
|---------|-------|------|------|-----------|
| P1-1 Agent Mode E2E | 1 | 02-27 | PASS | 21/21 도구 PASS |
| P1-3 Cron Issues | 1 | 02-27 | PASS | pykrx 폴백, regime 자동복구 |
| P1-4 Seed Data | 1 | 02-27 | PASS | 3카드 백테스트 |
| P1-5 Freshness | 1 | 02-27 | PASS | 6도구 freshness_warning |
| P3-1 전략 진화 | 3 | 02-27 | PASS | migration 035 |
| P3-2 호가창 백테스트 | 3 | 02-27 | PASS | migration 036 |
| P3-3 이벤트 엔진 | 3 | 02-27 | PASS | migration 037, DART 연동 |
| P3-R1 전략 편집 | 4 | 02-27 | PASS | migration 038 |
| P3-R2 지표 20개 | 4 | 02-27 | PASS | TA 필터 35+ |
| P4-1 메모리 | 4 | 02-27 | PASS | episodic_memory 연동 |
| P4-2 갭 | 4 | 02-27 | PASS | migration 040, 108,574건 |
| P4-3 30일 모의투자 | 5 | 02-27 | PASS | migration 041 |
| P5-1 자기리뷰 | 5 | 02-27 | PASS | migration 043 |
| P5-2 Telegram+섹터 | 5 | 02-27 | PASS | 모닝 브리핑 자동 발송 |
| P5-3 포트폴리오 최적화 | 6 | 02-27 | 92 | migration 044, Sharpe 4.63 |
| P5-4 개인화 | 6 | 02-27 | 90 | migration 045 |
| P6-1 리스크+킬스위치 | 6 | 02-27 | 95 | migration 046, CEO 전용 해제 |
| P6-EXTRA 신고가 돌파 | 6 | 02-27 | 85 COND | execute_buy/sell 스텁 |
| P6-2 KIS 게이트웨이 | 7 | 02-28 | PASS | migration 047, 모의 주문 4건 |
| CUR-SHARED-DB-SCHEMA-CATALOG-001 | — | 03-02 | PASS | DB 스키마 카탈로그 254테이블+8뷰 |
| CUR-GO100-BRIDGE-BUG-FIX-001 | — | 03-02 | PASS | genspark_bridge.py 3종 버그 수정 |
| CUR-GO100-P6-EXTRA-VERIFY-001 | — | 03-02 | PASS | Agent Chat E2E 4단계 검증 |
| CUR-GO100-P7-1-FULL-QA-001 | — | 03-02 | PASS(조건부) | 전체 QA 95/100 |
| CUR-GO100-P4-AI-ENHANCE-DESIGN-001 | — | 03-02 | PASS | Phase 4 AI 모델 고도화 설계 |
| CUR-GO100-P4A-FEATURE-ENG-001 | — | 03-02 | PASS | V3 교차피처 3개+신규피처 4개 |
| CUR-GO100-PAPER-TRADING-PREP-001 | — | 03-02 | PASS | 30일 모의투자 사전 확인 |
| CUR-GO100-P4B-V3-BATCH-REBUILD-001 | — | 03-02 | PASS | build_feature_store_batch_v3.py |
| CUR-GO100-P4B-V3-BATCH-RESULT-001 | — | 03-03 | PASS | 307,608건 × 41컬럼, 12개월 parquet |
| CUR-GO100-P4C-V3-MODEL-TRAIN-001 | — | 03-03 | PASS | V3 AUC 0.5656, Q2 AUC 0.6092 |
| CUR-GO100-RESEARCH-CORE-BUILD-001 | EVO | 03-04 | PASS | BacktesterAgent+StockProfiler+AnalystAgent |
| CUR-GO100-RESEARCH-VALIDATE-ORCH-001 | EVO | 03-04 | PASS | ValidatorAgent D등급+EvolutionLoop, 52/52 PASS |
| CUR-GO100-RESEARCH-PARAM-SCORE-001 | EVO | 03-04 | PASS | TypeParamSearcher+HypothesisScorer, 29/29 PASS |
| CUR-GO100-RESEARCH-UI-LAUNCH-001 | EVO | 03-04 | PASS | research-lab-status 재설계, CEO 승인 API |
| CUR-GO100-RESEARCH-EVOLUTION-LOOP-001-PART9 | EVO | 03-04 | PASS | 보고서 자동생성+GitHub push |
| DIR-GO100-FE-AUDIT-010 | FE | 03-04 | PASS | 34개 페이지 전수 감사, API 갭 10개 식별 |
| DIR-GO100-FE-API-BIND-011 | FE | 03-04 | PASS | GO100 10개 라우터 전수 API 연동 |
| DIR-GO100-FE-CHARTS-012 | FE | 03-04 | PASS | recharts + lightweight-charts 11종 |
| DIR-GO100-FE-MOBILE-013 | FE | 03-04 | PASS | 375/414/768/1024 반응형, PWA manifest |
| DIR-GO100-FE-DESIGN-014 | FE | 03-04 | PASS | 다크모드 기본, 통일 컬러 팔레트 |
| DIR-GO100-FE-FINAL-015 | FE | 03-04 | PASS | BRIDGE 최종 E2E, 7라우터 GREEN |

---

## Batch 8 결과 (2026-03-01)

| 항목 | 비고 |
|------|------|
| Phase 4 AI Feature Pipeline | PASS — feature_engine.py + feature_store.py, E2E 5종목 PASS |
| Phase 4 AI Feature Batch Build | PASS — 263,450 레코드, 월별 Parquet 12개, 15.13MB, 306.7s |
| Phase 4 AI LightGBM V2 학습 | PASS — 3-Fold WF, AUC 0.5406±0.0055, MFE_60MIN R²=0.58 |

---

## Commander Architecture 완료 (2026-03-03~04, DIR-001~DIR-009)

- 에이전트 10개 배포: base/news/regime/risk/supply_demand/technical/bull/bear/debate/desk2~5/researcher/backtester/commander
- 자기진화루프: agent_performance_tracker, 동적가중치 (MIN 0.3, MAX 2.0)
- V3 모델 활성화 (active:True, ai_scorer.py V3 업데이트)
- Telegram 확인 (message_id:1981)
- go100_agent_reports, go100_debate_log, go100_agent_performance 테이블 신규
- 자기 진화 루프: 가중치 추적 에이전트 9개, 20거래일 롤링 정확도
- LightGBM 재학습 크론: 20일 주기
- 커맨더 자기 비평: commander_self_critique → go100_agent_reports 저장

### 모드 전환
```bash
GO100_COMMANDER_MODE=true   # 커맨더 모드 활성화
GO100_COMMANDER_MODE=false  # 기존 백억이 단독 모드
```

---

## 완료 작업 테이블 (v15.0~v17.0, 개별 태스크)

### v14.1 완료 (2026-03-05)
| Task ID | 내용 |
|---------|------|
| T-001 | 미푸시 보고서 push + closing-report cron 등록 |
| T-002 | V3 모의투자 첫 매수 검증 |
| T-003 | Nginx WebSocket/SSE 감사 |
| T-004 | HANDOVER v14 + FE 재시작 |
| DIR-FE-RESTORE-016 | dashboard 래퍼 복원 + lib/go100 중복 삭제 (e92e5315) |
| T-006 | project-docs git 권한 복구 + 미push 일괄 반영 |
| T-007 | go100-frontend 서비스 재시작 + 빌드 적용 |
| T-008 | V3 모의투자 + closing cron + Nginx WS/SSE 통합 감사 |
| T-009 | HANDOVER v14.1 최종 정리 |

### v14.2 완료 (2026-03-05, Group A 감사)
| Task ID | 내용 |
|---------|------|
| T-012 | 모의투자 세션 ACTIVE 확인 (거래 0건, 크론 미발화) |
| T-013 | SaaS 인증 감사 (agreed_terms 미저장 버그 발견) |
| T-014 | GO100 API 전수 헬스체크 (122경로 ALL GREEN) |
| T-015 | FE 44페이지 전수 점검 (public 200/protected 307) |
| T-016 | HANDOVER v14.2 업데이트 |

### v15.0~v15.4 완료 (2026-03-05~06)
| Task ID | 내용 |
|---------|------|
| T-017A/B | pandas 3.0.1 패치 (groupby.apply include_groups=False) |
| T-023 | pandas 패치 검증 + 수동 1회 실행 PASS |
| T-024 | V3 모델 6종 로드 성공, activate_v3_model.py 작성 |
| T-025/T-030 | closing_report cron 설치 (커밋 f5a286e3) |
| T-028 | agreed_terms/privacy DB 저장 버그 완전 수정 (migration 064, 커밋 4a24b943) |
| T-029 | sitemap.xml 44개 URL 동적 생성 (커밋 0060ac99) |
| T-031 | 에러 모니터링 + migration 065 + Telegram (커밋 758dc8c7) |
| T-033B | entry_rules 포맷 정규화 (커밋 ba7f2431) |
| T-036/T-037 | Commander 대시보드 구현 |
| T-039 | 매니저 스냅샷 공개 URL |
| T-046 | 어드민 시그널·리스크 + 매매 관리 + 거래 상세 (커밋 b8f247ca) |
| T-157 | 실매매/모의 토글 스위치 연동 (커밋 fc398d2d) |

### v16.0~v17.0 완료 (2026-03-09)
| Task ID | 내용 |
|---------|------|
| T-051 | 능력 전면 개방 — Agent Loop 20R/10T, hallucination_guard.py (커밋 4e7d5d8d) |
| T-052 | 전략 대량 생산 5레짐 7카드 (strategy_cards 42→49, 커밋 efbc58ce) |
| T-053 | 모의투자 세션 3~7 ACTIVE |
| T-054 | Admin War Room 메인 + 스텁 11개 |
| T-055 | HANDOVER v17.0 통합 갱신 |

---

## Phase 6 게이트 검증 결과 (2026-03-02 최종 확인)

| 항목 | 판정 | 비고 |
|------|------|------|
| P6-1 리스크엔진 | PASS | go100_risk_rules 3건. risk_engine async_generator 버그 수정 완료 |
| P6-2 KIS 게이트웨이 | PASS | go100_live_orders 10건. Mock 주문 BUY/SELL/REJECTED 전 항목 PASS |
| P6-EXTRA-VERIFY | PASS | E2E 4단계 전 항목 통과 |
| P7-1 QA | PASS(조건부) | 95/100. 30일 모의투자 1사이클 미완료 |

### Agent 도구: 57개 (52+5 신규: bull_bear_debate, get_ai_prediction, get_ai_top_stocks, get_position_sizing, set_position_sizing)

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
| 048a | go100_position_sizing (동적 포지션 사이징) |
| 048b | go100_strategy_knowledge (전략 지식 베이스) |
| 064 | v4_users agreed_terms·privacy_agreed 컬럼 추가 |
| 065 | go100_error_log 테이블 (에러 모니터링 미들웨어) |

---

## Known Issues (해결 완료 목록) {#known-issues}

| # | 이슈 | 해결 |
|---|------|------|
| 1 | collect_financials.py KIS API 403 | pykrx 폴백 (P1-3) |
| 2 | v4_market_regime_daily 정체 | run_auto_heal → heal_regime (P1-3) |
| 3 | ohlcv_daily 크론 로그 경로 | /var/log/go100/ohlcv_daily.log 통일 |
| 4 | go100_fundamentals DART API 키 | DART 발급·.env 설정 |
| 5 | 모닝 브리핑 Telegram 토큰 | 설정 완료, message_id:1981 (2026-03-03) |
| 6 | risk_engine async_generator 오류 | risk_engine.py RULE_SECTOR 버그 수정 |
| 7 | pandas 3.0 버전 불일치 | indicator_precompute groupby.apply 패치 (T-017/T-023) |
| 8 | entry_rules 포맷 불일치 (card_id=35,36) | SignalEvaluator + DB UPDATE (T-033B, 커밋 ba7f2431) |

---

## 프론트엔드 현황 (2026-03-06 기준)
- **페이지**: 45개 전수 LIVE (STUB/BROKEN 0) → 48개 (T-046/T-054 이후)
- **API 연동**: 10/10 GO100 라우터 GREEN
- **차트**: recharts + lightweight-charts, 11종
- **모바일**: 375/414/768/1024 반응형, PWA manifest
- **디자인**: 다크모드 기본, 통일 컬러 팔레트
- **백억이 채팅**: 마크다운 렌더링, 프로그레스, 타이핑 인디케이터
- **빌드**: Next.js 14, npm run build PASS

---

## 능력 전면 개방 (v16.0 — T-050, 2026-03-09)

> CEO 지시 2026-03-08: "능력 전면 개방, 실계좌만 잠금, 모의투자 적극 활용, 환각 자가 진화"

### 변경 내역

| 항목 | 이전 | 이후 |
|------|------|------|
| Agent Loop | 최대 5라운드, 라운드당 3도구 | **최대 20라운드, 라운드당 10도구** |
| V3 모델 | train_result.json active:True (이미 활성) | **is_available=True 확인, AUC 0.5656** |
| 모의계좌 매매 | 제한적 운영 | **전면 개방 (CEO 승인 불필요)** |
| 실계좌 매매 | 잠금 | **잠금 유지 — CEO 승인 필수** |
| 환각 방지 | 없음 | **5중 방어 체계 (hallucination_guard.py)** |
| 토론 라운드 | 3라운드 하드코딩 | **5라운드 + DRAW 강제 판정** |
| 메모리 자동로드 | 수동 | **run_agent() 시작 시 자동 주입** |

### 환각 방지 5중 방어 체계 (hallucination_guard.py)
1. **verify_trade_facts**: 종목코드 6자리/가격 범위/거래시간/action 검증
2. **double_check_numbers**: LLM 주장 vs DB 실데이터 수치 비교 (5% 이상 괴리 감지)
3. **paper_trade_first**: 실계좌 전 모의투자 선행 강제 (LIVE_TRADING_ENABLED=false)
4. **post_trade_review**: 거래 24h 후 근거 vs 결과 대조
5. **learn_from_hallucination**: 환각 패턴 go100_episodic_memory에 저장 → 재발 방지

### 적용 환경 변수 (.env)
```bash
GO100_AGENT_MAX_ROUNDS=20
GO100_AGENT_MAX_TOOLS_PER_ROUND=10
GO100_AGENT_UNLIMITED_MODE=true
GO100_PAPER_TRADING_ENABLED=true
GO100_PAPER_TRADING_UNLIMITED=true
GO100_LIVE_TRADING_ENABLED=false
GO100_LIVE_TRADING_REQUIRES_CEO=true
GO100_DEBATE_ROUNDS=5
```

---

## SaaS 런칭 준비 체크리스트 (2026-03-05 기준)

| # | 항목 | 상태 | 비고 |
|---|------|------|------|
| 1 | 회원가입 플로우 | ✅ 완료 | T-028 — migration 064, E2E PASS (커밋 4a24b943) |
| 2 | 결제 연동 | ⚠️ 설계 완료 | T-021 — 토스페이먼츠(국내) + Stripe(해외), CEO 승인 대기 |
| 3 | 구독 플랜 관리 | ⚠️ 설계 완료 | Free/Pro(29,000원/월)/Premium(79,000원/월), CEO 승인 대기 |
| 4 | 마켓플레이스 | ⚠️ 설계 완료 | go100_marketplace_listings DB 스키마, CEO 승인 대기 |
| 5 | 이용약관 최신화 | ✅ 완료 | /terms 페이지 정식 구현 |
| 6 | 개인정보처리방침 | ✅ 완료 | /privacy 페이지 정식 구현 |
| 7 | 고객지원 채널 | 미구현 | 카카오톡/이메일 채널 미개설 |
| 8 | 온보딩 튜토리얼 | 미구현 | 첫 로그인 시 가이드 화면 없음 |
| 9 | SEO/OG 태그 | ✅ 완료 | T-020 OG + T-029 sitemap 45개 URL |
| 10 | 에러 모니터링 | ✅ 완료 | T-031 — error_monitor.py + migration 065 + Telegram (커밋 758dc8c7) |

---

## Phase 8 로드맵 (2026-03-05 기준)

| 단계 | 태스크 | 상태 |
|------|--------|------|
| Phase 8-1 | T-025 closing_report cron 등록 | 완료 |
| Phase 8-2 | 30일 모의투자 1사이클 완주 (session_id=2~7) | 기간 만료 — 검토 필요 |
| Phase 8-2 | V3 모델 CEO 승인 후 실전 투입 | 활성화 완료 (D-008) |
| Phase 8-3 | 자기리뷰 1사이클 (weekly_review) | 대기 |
| Phase 8-4 | 소액 실매매 3일 검증 | 대기 |
| Phase 8-5 | SaaS 결제 연동 | 미착수 |
| Phase 8-6 | 최종 SaaS QA + 라이브 런칭 | 미착수 |

---

## 핵심 파일/경로 (v17.0 기준)

| 구분 | 경로 |
|------|------|
| 인계서 | /root/project-docs/go100/HANDOVER.md |
| 규칙 | /root/kis-autotrade-v4/.cursorrules, CLAUDE.md |
| 컨텍스트·로드맵 | go100/CONTEXT.md, go100/ROADMAP.md |
| Agent 도구 | backend/app/services/go100/ai/agent_tools.py, tool_executors.py |
| 리스크·주문 | backend/app/services/go100/risk_engine.py, kis_order_gateway.py |
| 마이그레이션 | backend/migrations/035_* ~ 065_* |
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

## 검증 명령어 (v17.0 기준)

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

## 웹 Claude 인수인계 절차

1. CEO가 프로젝트명 + HANDOVER.md URL + CEO-DIRECTIVES.md URL 전달
2. 웹 Claude가 모든 URL 크롤링
3. HANDOVER.md 섹션별 상태 파악
4. 상태 보고: (마지막 완료 작업, 현재 단계, 대기 작업, 미해결 이슈)
5. CEO 추가 지시 대기

---

## 참고 문서 (읽기 순서)

1. 이 인계서 (HANDOVER.md → L1)
2. /root/kis-autotrade-v4/.cursorrules, CLAUDE.md
3. go100/ARCHITECTURE.md, DB_SCHEMA.md
4. go100/CONTEXT.md, ROADMAP.md
5. go100/CEO-DIRECTIVES.md
6. 관련 보고서: /root/project-docs/go100/reports/

---

## 핵심 발견 (누적)

- E2E 23/23 PASS (전 구간 통과)
- Agent 도구 57개, 스크리닝 필터 35+
- 갭 데이터 108,574건 (go100_gap_calibrator)
- 포트폴리오 최적화: Markowitz Sharpe 4.63, Risk Parity Sharpe 4.06
- 리스크 엔진: pre-trade 4종 체크 + 일일 P&L 한도 + Kill Switch
- 자기리뷰: 주간/월간 자동 성과 평가 + 개선안 생성
- DB migration 035~065 (16개 테이블)
- 크론 63+ 라인 활성
- AI Feature Pipeline: DUAL_FLOW_20D, SMALL_CAP_QUALITY, THEME_CYCLE, MarketRegimeEncoder(Q1~Q4)
- Parquet Feature Store: 20개 피처 + 3개 라벨
- 1년치 배치 빌드 완료: 263,450 rows / 12개 월별 Parquet / 15.13MB / 오류 0건
- 벌크 최적화: 1.8M → ~980 쿼리 (1,880배 절감)
- LightGBM V2: 3-Fold AUC 0.5406±0.0055, MFE_60MIN R²=0.58
- LightGBM V3: 통합 AUC 0.5656, Q2공격형 AUC 0.6092
- AI Feature Pipeline V3 피처 33개, 1년치 배치 307,608건
- strategy_cards: 최초 0건 → 49장 (T-052 기준)

---

## 버전 이력 (v1.0~v18.0)

| 버전 | 날짜 | 변경 요약 |
|------|------|-----------|
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
| v10.1~v10.10 | 02-28~03-02 | 통합·AI 파이프라인·버그 수정 |
| v11.0 | 03-03 | P4-B 배치 완료 + V3 모델 학습 |
| v12.0 | 03-03 | Commander Architecture 완료 |
| v13.0~v13.2 | 03-04 | BRIDGE 갱신, V3 검증, 도구 57개 |
| v14.1~v14.2 | 03-04~05 | FE 복원, Group A 감사 |
| v15.0~v15.4 | 03-05~06 | pandas 패치, SaaS 버그수정, 어드민 |
| v16.0 | 03-09 | T-051 능력 전면 개방 |
| v17.0 | 03-09 | T-052~T-055 통합, 진행률 99% |
| v18.0 | 03-30 | **3계층 전환** (L1/L2/L3 분리) + 03-09~03-30 커밋 반영 |

---

## v10.1~v17.0 상세 버전 이력

| 버전 | 날짜 | 변경 |
|------|------|------|
| v17.0 | 03-09 | T-055 통합 반영: T-050 능력 전면 개방, T-052 전략 대량 생산 7카드/5레짐, T-053 세션 3~7 ACTIVE, T-054 Admin War Room 스텁 11개, D-008 실행 완료, 진행률 99% |
| v16.0 | 03-09 | T-050 백억이 능력 전면 개방: Agent Loop 20R/10T, HallucinationGuard 5중방어, 환각방지 자동연동, 커밋 4e7d5d8d |
| v15.4 | 03-06 | 어드민 시그널·리스크 + 매매 관리 + 거래 상세 (T-046), 페이지 45→48 |
| v15.3 | 03-06 | Commander 대시보드 + entry_rules 정규화 + 매니저 스냅샷 |
| v15.2 | 03-06 | entry_rules 검증 + T-157 토글UI, migration 035~065 갱신 |
| v15.1 | 03-05 | SaaS 버그수정+SEO+에러모니터링 (T-028~T-031) |
| v15.0 | 03-05 | pandas 3.0 수정 + V3 모델 준비 (T-017A/T-023/T-024) |
| v14.2 | 03-05 | Group A 감사 완료 (T-012~T-016) |
| v14.1 | 03-04 | DIR-015 BRIDGE 최종 E2E 검증, SaaS 체크리스트, 진행률 97% |
| v13.1 | 03-04 | DIR-GO100-PAPER-TRADING-V3-003-R3 완료: V3 Brain 연동, cron 3건 |
| v12.0 | 03-03 | Commander Architecture: 에이전트 10개, 자기진화루프, V3 활성화, Telegram 확인 |
| v11.0 | 03-03 | P4-B 배치 완료(307,608건) + P4-C V3 모델 학습(AUC 0.5656) |
| v10.10 | 03-02 | P4-B V3 배치 빌드 스크립트 완료 |
| v10.9 | 03-02 | P4-A 피처 엔지니어링: V3 교차피처 3개+신규피처 4개, 30일 모의투자 사전 설정 |
| v10.8 | 03-02 | CEO P0 수급 데이터 전수 조사 |
| v10.7 | 03-02 | Phase 4 AI 모델 고도화 설계안 |
| v10.6 | 03-02 | P6-EXTRA-VERIFY PASS + P7-1 QA PASS(95/100), 진행률 90% |
| v10.5 | 03-02 | genspark_bridge.py 3종 버그 수정 |
| v10.4 | 03-02 | DB 스키마 카탈로그 통합(254개) |
| v10.3 | 03-01 | AI 보완판: 3-Fold WF, 다중타겟 회귀 |
| v10.2 | 03-01 | Batch 8 AI LightGBM V2 학습 반영 |
| v10.1 | 02-28 | 단일 파일 통합, 테이블 표준화 |

---

## v14.1~v17.0 완료 작업 상세 (보고서 참조용)

### v14.1 (2026-03-05)
- T-001: 미푸시 보고서 push + closing-report cron 등록
- T-002: V3 모의투자 첫 매수 검증
- T-003: Nginx WebSocket/SSE 감사
- T-004: HANDOVER v14 + FE 재시작
- DIR-FE-RESTORE-016: dashboard 래퍼 복원 + lib/go100 중복 삭제 (e92e5315)
- DIR-010-C: src/go100 전수 파일목록 (95파일 11,086줄)
- T-006: project-docs git 권한 복구 + 미push 일괄 반영
- T-007: go100-frontend 서비스 재시작 + 빌드 적용
- T-008: V3 모의투자 + closing cron + Nginx WS/SSE 통합 감사
- T-009: HANDOVER v14.1 최종 정리

### v14.2 (2026-03-05) — Group A 감사
- T-012: 모의투자 세션 ACTIVE 확인 (거래 0건, 크론 미발화)
- T-013: SaaS 인증 감사 (agreed_terms 미저장 버그 발견)
- T-014: GO100 API 전수 헬스체크 (122경로 ALL GREEN)
- T-015: FE 44페이지 전수 점검 (public 200/protected 307)
- T-016: HANDOVER v14.2 업데이트

### v15.0 (2026-03-05) — pandas 패치 + V3 모델 준비 + SEO + 결제 설계
- T-017A: stock_code KeyError 원인 분석 — pandas 3.0.1 groupby.apply
- T-017B: paper_trading_engine_30d.py 방어적 수정 (커밋 f8bd2bee)
- T-023: pandas 3.0 패치 검증 + 수동 1회 실행 PASS
- T-024: V3 모델 파일 검증 + activate_v3_model.py 작성 (커밋 de3456c6)
- T-018: 모의투자 엔진 정밀 검증 — entry_rules 포맷 불일치 확인
- T-020: SEO/OG 메타태그 전수 적용 (커밋 71f51ebe)
- T-021: SaaS 결제·구독 아키텍처 설계 (CEO 승인 대기)
- T-028: agreed_terms/privacy DB 저장 버그 수정 (migration 064, 커밋 4a24b943)
- T-029: sitemap.xml 44개 URL 동적 생성 (커밋 0060ac99)
- T-030: closing_report 크론 설치 검증 (커밋 f5a286e3)
- T-031: 에러 모니터링 미들웨어 (migration 065, 커밋 758dc8c7)

### v15.2~v15.4 (2026-03-06) — entry_rules + Commander + 어드민
- T-157: 실매매/모의 토글 스위치 연동 (커밋 fc398d2d)
- T-033: entry_rules 포맷 불일치 진단
- T-034: 모의투자 수동 1회 매수 트리거 — 매수 0건
- T-033B: entry_rules 포맷 정규화 (커밋 ba7f2431)
- T-036/T-037: Commander 군단 대시보드 구현, 페이지 44→45
- T-039: 매니저 스냅샷 공개 URL
- T-046: 어드민 시그널·리스크 + 매매 관리 + 거래 상세, 페이지 45→48 (커밋 b8f247ca)

### v16.0~v17.0 (2026-03-09) — 능력 전면 개방 + 전략 대량 생산
- T-051: 능력 전면 개방 (Agent Loop 20R/10T, hallucination_guard.py, 커밋 4e7d5d8d)
- T-052: 전략 대량 생산 5레짐 7카드 (strategy_cards 42→49, 커밋 efbc58ce)
- T-053: 모의투자 세션 3~7 가동
- T-054: Admin War Room 메인 + 스텁 11개
- T-055: HANDOVER v17.0 통합 갱신
