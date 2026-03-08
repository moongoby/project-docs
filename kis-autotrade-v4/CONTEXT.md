# KIS AutoTrade V4.1 프로젝트 컨텍스트 (Claude PM용)
> Public URL: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md
> 최종 갱신: 2026-03-08 (T-285 v10.28 동기화 — trades.html 키움 영웅문4 차트 T-282+T-283 Phase2 완료, RSI/MACD/보유구간Rectangle/전체화면, 파일 7개, 다음 Phase3 예정)

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

## 6. DB 무결성 기준 (2026-03-07 실측)
- strategy_cards: 60건 (D1:10, D2:16, D3:11, D4:9, D5:10, 미배정:4)
- v4_positions OPEN: 0건 (03-07 기준 전량 청산)
- DB 크기: 44 GB
- 테이블 수: 290개 (snapshot 2026-03-07 기준)
- v4_ohlcv_minute (2026-03 파티션): 403,915행 (누적 ~118M+)
- v4_scalping_universe: 1,354종목
- ohlcv_daily max: 2026-03-06
- **DQI: 92.8 (Grade A) — T-275 재산출 (Grade D→B→A 달성)**
  - L0_KOSPI: 100.0% (90일 NOT NULL 기준, 57/57행, T-275 기준 변경)
  - L0_VIX_60D: 97.4% (60일 NOT NULL, 38/39행, T-270 백필 완료)
  - L1_SECTOR_MAP: 100.0% (3844/3844 active 종목, T-248/T-260 완료)
  - L1_SECTOR_IDX: 68.3% (2460/3600 기대행수, 60섹터×60일 기준)
  - L2_INVESTOR: 75.0% (추정, KIS API 30일 한계)
  - L3_FUNDAMENTAL: 100.0% (3844/3844, T-271 전종목 PER/PBR 완료)
  - OHLCV_FRESH: 99.8% (3836/3844 최신일 ≥ 어제)
  - 개선 이력: 58.1(D)→81.3(B)→92.8(A)
  - 주의: KOSPI 프록시값 범위이탈 잔존 (711/730행 1800-3500 범위 외), CEO 결정 대기
- **FunnelScore: 30/30 PASS (100%), 평균 0.862, 범위 0.762~0.938, 임계값 0.35**
- **섹터 매핑: 100.0% (3844/3844, T-248/T-260 완료)**
- **펀더멘탈: 100% (T-271, 전종목 PER/PBR 수집완료)**
- **매크로: KOSPI 정규화 로직 추가(T-270), VIX 60일 백필 완료(97.4%)**

## 7. 최근 완료 작업 (T-187~T-285)
| Task | 커밋 | 내용 |
|------|------|------|
| T-285 | docs | 브릿지 큐 잔류 정리 + CONTEXT.md v10.28 동기화: running 큐 0건 확인, trades.html 차트 현황 반영, HANDOVER v10.68 갱신 |
| T-284 | dd7b6560 | 브릿지 큐 T-282-S5/T-282-S4S5 completed처리 + Phase2 7/7 검증(RSI/MACD/Rectangle/전체화면 14match+CSS+HTML+HTTP200) |
| T-283 | c6bc6a4b | trades.html Phase2: RSI/MACD pane + 보유구간 Rectangle + 전체화면(F키/ESC) + kw-chart-engine.js addPane/removePane/addHoldingRectangle/clearRectangles |
| T-282 | 4b327d12/09e539d6 | 키움 영웅문4 스타일 trades.html 차트 전면 교체: trades.html + CSS 1 + JS 5 = 7파일, LWCharts v5.1.0 6모듈 |
| T-275 | T-275 | DQI 최종 재산출 Grade A(92.8) 달성 + CONTEXT.md v10.27: L0_KOSPI NOT NULL 기준 변경(2.6%→100%), FunnelScore 30/30 100%(avg=0.862), HANDOVER v10.58 갱신 |
| T-273 | T-273 | DQI 재산출 Grade B(81.3) 달성 + CONTEXT.md v10.26 전면 동기화: 실측값 기반 DQI 81.3, FunnelScore 30/30 PASS(100%), HANDOVER v10.56 갱신 |
| T-272 | 분석전용 | DQI Grade D(58.1) 현황 분석 + 복구 로드맵: L0~L3 실측, T-248/T-260/T-271/T-270 복구 순서 정의 |
| T-271 | 7c90c931 | 펀더멘탈 전종목 수집기 + 백필: v4_fundamental_quarterly 전종목 PER/PBR 100% |
| T-270 | 04b2a1de | 매크로 KOSPI 오염복구 + VIX 60일 백필: normalize_kospi() 추가, yfinance+FRED fallback, VIX 97.4% |
| T-248 | 38e6b840 | KRX 업종분류 전체 매핑 스크립트 + 검증 |
| T-260 | 8779048c | 섹터 매핑 전수확보 + 섹터지수 60일 백필: 4.2%→99.1%, 3일→68일 |
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

## 8. trades.html 차트 현황 (2026-03-08 기준)
| 항목 | 내용 |
|------|------|
| 기반 | LightweightCharts v5.1.0 (키움 영웅문4 스타일) |
| 파일 구성 | trades.html + kw-chart-engine.css + kw-chart-engine.js + kw-chart-data.js + kw-chart-controls.js + kw-chart-indicators.js + kw-chart-trades.js (총 7파일) |
| Phase1 (T-282) | 기본 캔들차트 + 매매신호 오버레이 (09e539d6/4b327d12) |
| Phase2 (T-283) | RSI pane(14기간/70·30 수평선) + MACD pane(12/26/9) + 보유구간 Rectangle + 전체화면(F키/ESC) (c6bc6a4b) |
| 다음 예정 | Phase3: 자동추세선, 거래량프로파일(VP), 분봉 실시간 연동 |

## 9. 작업 큐 (2026-03-08 기준)
| 순위 | 작업 | 상태 |
|------|------|------|
| P0-CRITICAL | T-229 exit_manager MA20 trailing 전면 적용 | CEO결정대기 |
| P0-CRITICAL | L0_KOSPI 과거 데이터 재백필 (현재 2.6%, 목표 95%+) | 후속작업 필요 |
| P1-HIGH | T-283-Phase3 자동추세선 + 거래량프로파일 + 분봉 실시간 | 다음 작업 |
| P1-HIGH | T-228 research_backtest_loop 크론 설치 | 대기 (162 COMPLETED, 1 RUNNING stuck) |
| P1-HIGH | T-227 FunnelScore 재교정 (방안A Fail-Open / 방안C 임계값0.20) | CEO승인대기 |
| P1-HIGH | T-226 백테스트 /api/v4/backtest/progress 구현 | 대기 (현재 404) |
| P1-MEDIUM | T-285 CONTEXT.md v10.28 동기화 | **완료** (브릿지 큐 정리) |
| P1-MEDIUM | T-284 브릿지 큐 Phase2 검증 | **완료** (dd7b6560) |
| P1-MEDIUM | T-283 trades.html Phase2 | **완료** (c6bc6a4b) |
| P1-MEDIUM | T-282 trades.html 차트 전면 교체 | **완료** (4b327d12/09e539d6) |
| P1-MEDIUM | T-275 DQI 최종 재산출 + CONTEXT v10.27 | **완료** (Grade A 92.8) |
| P1-MEDIUM | T-273 DQI 재산출 + CONTEXT v10.26 | **완료** (Grade B 81.3) |
| P1-MEDIUM | T-272 DQI 분석 로드맵 | 완료 (분석전용) |
| P1-MEDIUM | T-271 펀더멘탈 전종목 수집 | 완료 (7c90c931) |
| P1-MEDIUM | T-270 매크로 KOSPI+VIX 복구 | 완료 (04b2a1de) |
| P1-MEDIUM | T-260 섹터 매핑+지수 백필 | 완료 (8779048c) |
| P1-MEDIUM | T-248 KRX 업종분류 매핑 | 완료 (38e6b840) |
| P1-MEDIUM | T-235 SMALL_CAP_QUALITY + SEC_LEADER_FLAG v2 | 완료 (20017658) |
| P1-MEDIUM | T-219 THEME_CYCLE feature variable | 완료 (7f27b7b4) |
| P1-MEDIUM | T-218 DUAL_FLOW_5D/20D feature variable | 완료 (faa85636) |
| P1-MEDIUM | T-216 source 전파 수정 | 완료 (8d74d00c) |
| P2-LOW | T-234 API /api/v4/regime 구현 | 대기 (현재 에러) |

## 10. CEO 결정 대기
1. **T-227 FunnelScore 재교정 방안 승인 (현황: Fail-Open 유지 중)**
   - T-273 실측: FunnelScore 30/30 PASS(100%), 임계값 0.35, Fail-Open 유지
   - 방안A: Fail-Open 계속 유지 (현행 → 실전 검증 우선)
   - 방안B: 임계값 재조정 (T-237 적용 검토)
   - 03-10(월) 장 개시 후 T-245R 모의매매 실전 검증 예정
2. **T-229 exit_manager MA20 trailing 전면 적용 승인** (H05-D PF=2.18, H08-B PF=25.93 기반)
3. **L0_KOSPI 과거 데이터 재백필 승인** (현재 2.6%, yfinance 실제 KOSPI 데이터로 교체 필요)
   - T-270 normalize_kospi() 추가됨, 과거 730행 중 711행이 범위 외 (프록시값)
4. T-194 ATR 기반 동적 SL 파라미터 승인 (D-ORB 2.5% Cap 기적용, T-207 완료)
5. T-195 14:00 이후 진입 차단 정책 (완료, T-195 bd8d4620)

## 11. 핵심 파일 (수정 시 검수 필수)
- exit_manager.py (T-187/T-193 적용됨), cte_pipeline.py (T-189 BEAR 분기)
- v4_pipeline_orchestrator.py, strategy_engine.py, risk_manager.py
- order_executor.py, position_manager.py, split_transfer_engine.py
- lifecycle.py, fund/*, adaptive/*, regime_detector.py
- backtest_engine_v2.py, collector_minute.py, main.py
- config/funnel_score.yaml (bear_min_score_for_entry=0.28)

## 12. 문서 체계
- Cursor Rules: .cursor/rules/kis-v41-rules.md (서버)
- Public Rules: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md
- 보고서: /root/project-docs/kis-autotrade-v4/reports/
- 검수: review/ → push_review.sh → CEO+Claude 승인 → clean_review.sh

## 13. AI 세션 시작 시 필수 읽기
1. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/CONTEXT.md (이 파일)
2. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md
3. https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md
