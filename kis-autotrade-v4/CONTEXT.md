# KIS AutoTrade V4.1 프로젝트 컨텍스트 (Claude PM용)
> Public URL: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md
> 최종 갱신: 2026-03-07 (T-233 v10.25 동기화 — strategy_cards 60, OPEN 0, DB 42GB, 290테이블, scalping_universe 1354, T-212~T-218 완료 반영, T-226~T-235 작업큐 갱신, 불일치 0건)

## 1. 프로젝트 개요
- KIS AutoTrade V4.1: 한국투자증권 API 기반 AI 자동매매 시스템
- DESK 1~5 멀티 전략 운영 (60개 전략카드)
- V4.1 코드베이스, 동일 서버/DB에서 타 서비스와 공유
- 도메인: trading41.newtalk.kr
- GitHub: moongoby/kis-autotrade-v4 (private), 문서: moongoby/project-docs (public)

## 2. 서버 환경
- 서버: root@211.188.51.113 (kis-autotrade-v4)
- 프로젝트: /root/kis-autotrade-v4
- 브랜치: phase-2c-command-center
- DB: PostgreSQL 16, kisautotrade / kis_admin / localhost:5432
- Python 3.12, FastAPI, SQLAlchemy (asyncpg), Redis 7.x
- 가상환경: source /root/kis-autotrade-v4/venv/bin/activate
- PYTHONPATH: /root/kis-autotrade-v4/backend

## 3. CEO 절대 규칙
1. kis-v41-* 서비스 재시작 금지 (CEO 승인 시에만)
2. strategy_cards ALTER/DROP/DELETE 금지 (UPDATE는 CEO 승인)
3. v4_positions 직접 수정 금지
4. 핵심 파일 수정 → review/ 업로드 → CEO+Claude 승인 후 적용
5. .env/.bak 커밋 절대 금지
6. 사전확인: strategy_cards=60, v4_positions OPEN=0

## 4. DESK 구성
| DESK | 역할 | max_hold | 라이브/전체 | 상태 |
|------|------|----------|------------|------|
| DESK1 | 초단타/스캘핑 | 0-1일 | 10/10 | 활성 |
| DESK2 | 단타 | 1-3일 | 16/16 | 활성 |
| DESK3 | 단기스윙 | 3-10일 | 11/11 | 활성 (주 수익원) |
| DESK4 | 중기스윙 | 20-40일 | 9/9 | 활성 (D4 Shadow 해제 완료) |
| DESK5 | 장기 | 90-120일 | 10/10 | 활성 (4주 보유기간 테스트 모드) |

## 5. 서비스 현황 (2026-03-06 기준)
| 서비스 | 포트 | 상태 |
|--------|------|------|
| kis-v41-api | 8003 | active (running) |
| kis-v41-monitor | — | active (running) |
| kis-v41-scheduler | — | active (running) |
| kis-v41-minute-collector | — | inactive (장외 정상, 장중 자동기동) |
| redis-server | 6379 | active |
| postgresql | 5432 | active (exited=정상) |

## 6. DB 무결성 기준 (2026-03-06 실측)
- strategy_cards: 60건 (D1:10, D2:16, D3:11, D4:9, D5:10, 미배정:4)
- v4_positions OPEN: 0건 (03-06 기준 전량 청산)
- DB 크기: 42 GB
- 테이블 수: 290개 (snapshot 2026-03-07 기준)
- v4_ohlcv_minute (2026-03 파티션): 403,915행 (누적 ~118M+)
- v4_scalping_universe: 1,354종목
- ohlcv_daily max: 2026-03-06

## 7. 최근 완료 작업 (T-187~T-235)
| Task | 커밋 | 내용 |
|------|------|------|
| T-235 | 20017658 | SMALL_CAP_QUALITY + SEC_LEADER_FLAG v2 구현 (D-008-KR P0): feature_engine.py compute_small_cap_quality + universe_builder.py flag_sector_leaders_v2; TC-01~08 8/8 PASS |
| T-227 | 분석전용 | FunnelScore 구조 해부 및 긴급 재교정: L0~L3 실측 트레이싱; max FS=0.2415<임계값0.35 구조적차단; 방안A/B/C CEO승인대기 |
| T-219 | 7f27b7b4 | THEME_CYCLE feature variable (D-008-KR P0): compute_theme_cycle_100b_count/ul_count 추가; 3케이스 6테스트 PASS |
| T-218 | faa85636 | DUAL_FLOW_5D/20D feature variable (D-008-KR P0): compute_dual_flow_5d/20d 추가; 4케이스 8테스트 PASS |
| T-216 | 8d74d00c | source 전파 수정: session_source→TradeSignal.source 전파; PRE_SOURCE_FILTER Fail-Open 버그 수정; TC-30~35 6건 PASS |
| T-215 | 예정 | T-193/T-195 코드 검증+HANDOVER 반영: exit_manager D5_D014_CONFIG enabled=True/hold_weeks=4; cte_pipeline ENTRY_CUTOFF_HOUR=14 확인; 30/30 PASS |
| T-214 | faf1c576 | DESK3→DESK2 pool_link 크론 연결: desk2_pool_link.py 엔트리포인트; v4_desk2_candidates 10→255건 |
| T-213 | 1cfc435c | DESK4 node_detector watchlist 연결 수정: v4_node_realtime(0행)→v4_desk4_watchlist(11종목) |
| T-212 | fba6f3d2 | DESK5 크론 cd 수정 + T5-2 조건 교체: FIX-001 크론 cd/REL-003 MA60기울기+거래량1.5배; 트리거 0%→10% |
| T-207 | 4cf5a6fe | ATR SL Cap: D-ORB 2.5%/D4 2.0%/D6 2.0%; calculate_atr_sl() 신규; 3/3 PASS |
| T-189 | 7df7dc81 | BEAR 레짐 FunnelScore: bear_min_score_for_entry=0.28, 통과율 +25%p |
| T-193 | bd8d4620 | D5 4주 보유기간 테스트 모드 (D5_D014_CONFIG.enabled=True) |
| T-195 | bd8d4620 | 14:00 이후 진입 차단 게이트 (ENTRY_CUTOFF_HOUR=14) |
| T-199 | 5fa5eb3e | migration 067 (go100_research_iterations), v41_research_loop 크론 |
| T-187 | 854466b8 | exit_manager.py SL/TP/TIMEOUT 조정 (D-ORB/D4/D6) |

## 8. 작업 큐 (2026-03-06 기준)
| 순위 | 작업 | 상태 |
|------|------|------|
| P0-CRITICAL | T-201 Exit Manager 정비 (D5 청산 미작동 + MA20 트레일링) | 대기 |
| P0-CRITICAL | T-202 DESK5→4→3 파이프라인 복원 (프랙탈 트리거) | 대기 |
| P1-HIGH | T-193 D5 Exit Manager 4주 보유기간 테스트 | 완료 |
| P1-HIGH | T-194 SL/TP 파라미터 조정 (ATR 기반 동적 SL) | 대기 |
| P1-HIGH | T-195 14:00 이후 진입 차단 게이트 | 대기 |
| P1-MEDIUM | T-205 CONTEXT.md v10.24 동기화 | 이 작업 완료 |

## 9. CEO 결정 대기
1. T-201 Exit Manager D5 청산 로직 수정 승인
2. T-202 DESK5→4→3 프랙탈 트리거 복원 승인
3. T-194 ATR 기반 동적 SL 파라미터 승인
4. T-195 14:00 이후 진입 차단 정책 승인

## 10. 핵심 파일 (수정 시 검수 필수)
- exit_manager.py (T-187/T-193 적용됨), cte_pipeline.py (T-189 BEAR 분기)
- v4_pipeline_orchestrator.py, strategy_engine.py, risk_manager.py
- order_executor.py, position_manager.py, split_transfer_engine.py
- lifecycle.py, fund/*, adaptive/*, regime_detector.py
- backtest_engine_v2.py, collector_minute.py, main.py
- config/funnel_score.yaml (bear_min_score_for_entry=0.28)

## 11. 문서 체계
- Cursor Rules: .cursor/rules/kis-v41-rules.md (서버)
- Public Rules: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md
- 보고서: /root/project-docs/kis-autotrade-v4/reports/
- 검수: review/ → push_review.sh → CEO+Claude 승인 → clean_review.sh

## 12. AI 세션 시작 시 필수 읽기
1. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md (이 파일)
2. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md
3. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md
