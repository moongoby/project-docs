# HANDOVER – KIS AutoTrade V4.1 DESK 시스템
> 최종 업데이트: 2026-03-01 (v4.8 — **Cursor #20 EQS LAG1 + D4 ATR + CTE 페이퍼 활성화**; v4.7 — CTE 풀 백테스트 + 3-Fold WF, GO)
> 관리자: CEO (moongoby)
> 용도: 모든 AI 세션(웹 Claude, Cursor, Claude Code) 시작 시 필수 읽기

---

## 1. 프로젝트 개요
- KIS AutoTrade V4.1: 한국투자증권 API 기반 AI 자동매매
- 5개 DESK (60개 strategy cards, 14개 OPEN positions)
- 서버: root@211.188.51.113, DB: PostgreSQL kisautotrade
- 225 테이블, 15.7GB, 일봉 3년치 (2,611,905 rows)
- 투자자별 수급 데이터 (261,000 rows), 뉴스 214만건

---

## 2. 완료된 작업

| Task ID | 날짜 | 커밋 | HTTP | 핵심 결과 |
|---------|------|------|------|-----------|
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
| VE-003-PHASE-F | 02-28 | (본 커밋) | — | **18신호분석**: TS-B4(PF3.23) > TS-C1(PF2.80) > TS-B1(PF2.72), 60분 보유 최적, 상한가 부스트 확인 |
| VE-003-PHASE-C | 02-28 | (본 커밋) | — | D3 FAIL(PF1.17), **S1 CONDITIONAL(PF1.44/WR58.7%)**, S2 전체 FAIL(MA7 PF1.27 최고) |
| VE-003-PHASE-D | 02-28 | (본 커밋) | — | NEW 254종목 6조건: VP120 88.5%, RSI 88.1%, MA정배열 87.7%, **3개+ 동시 87.7%**, 10시전 82.1% |
| DESK2-FINAL-SPEC | 02-28 | 7293aed | 200 | 6-Layer 아키텍처, 6전략+1탐지, 60분 청산 전환, 18시그널 매칭, D-011 등록 |
| HOTFIX-001+002 (GO100) | 02-28 | 6cc363b6 | 200 | tool_executors 스텁→실제 래퍼 교체 + risk_engine ::jsonb→CAST 수정, 6단계검증 PASS |
| DESK2-FINAL-SPEC-v2 | 02-28 | (본 커밋) | — | 능동청산(트레일링+부분청산)+분할매수+AI자동진화+모의실매매 추가 |
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
| PULLBACK-ANATOMY-001 | 02-28 | (본 커밋) | 200 | **눌림 전수조사 19,225건**, 2파 발생률 73.9%, 모드3 0%원인=RSI범위+MA20미형성(충족률0.26%), 재설계 안D 권고 |
| WAVE-CAPITAL-CYCLE-001 | 02-28 | (본 커밋) | — | **파동 자본순환 14과제**: W1 30%/W2 100% 청산, Dynamic스톱(PF17.98), 거래대금50%소진필터, VP 2분선행, 시스템효율17.7%→50% 로드맵 |
| WAVE-OUTER-RESEARCH-001 | 02-28 | cac9ef0 | — | **파동 외부 10과제(R15~R24)**: PASS2/COND5/FAIL3, 교차종목+370%, 전조AUC0.64, 뉴스χ²=249, 전략간섭100%중복, 비용PF-37%, 재앙3패턴 |
| DEV-HAV-001 | 02-28 | (본 커밋) | — | **DESK2 HAV 개발 완료**: 4-Layer, 27변수 135K조합, 주간자동탐색+일일Drift, E2E PASS, OOS PF=12.26, WF 2/2 PASS |
| CODE-ANALYSIS-CROSS-ENTRY-001 | 02-28 | (보고서 push) | 200 | 교차종목 진입 코드 갭 분석, 이미있음7건/수정4건/신규4건 |
| SURGE-CAUSE-ANALYSIS-001 | 02-28 | (본 커밋) | — | **급등원인분석+D-20전조추출 20과제**: 원인8분류(공시40.8%), 전조조합P=76.7%, 수급주도fake29.7%, Leader AUC0.712, DESK승격정량화, 계절성Q1>Q3 11.5pp |
| HANDOVER-PULLBACK-CONFIRM | 02-28 | (본 커밋) | 200 | **눌림확인매매 인계서**: 과제 A~D(이평선분류/반등신호검증/대기비용/관통반등), 19,225건 기반, 새 세션 즉시 착수 가이드 |
| PULLBACK-CONFIRMATION-001 | 03-01 | (본 커밋) | — | **눌림확인 심층연구**: 17,155건 5버킷(B2/B3 골든존 승률95%), 8신호(VWAP 73.7%최강), 관통>터치(PF26>11), 조건대기>시간대기, SIG3+SIG6 실용최적 |
| CS-EQS-MATRIX-001 | 03-01 | (본 커밋) | — | **CS+EQS+매트릭스 설계**: CS 5요소(≥65 PF1.55), EQS 5요소(≥70 PF8.43비용후), 9×9 매트릭스(금지18/시너지8), Layer 3.5/4.5 삽입 |
| DD-VWAP-GATE-001 | 03-01 | (본 커밋) | — | **DD+VWAP+게이트+ATR 설계**: DD 5레벨(maxDD-75%), VWAP 5변수, 5전략 반등확인게이트, ATR 동적TP/SL, NetR:R≥2.0 강제 |
| CTE-COMPARE-ARCH | 03-01 | (본 커밋) | — | CTE vs DESK 7축 비교, 흡수12개, 통합아키텍처 |
| SYSTEM-ARCH-FLOW | 03-01 | (본 커밋) | — | 시스템 아키텍처 흐름도 8개 |
| HANDOVER-CTE-INT | 03-01 | (본 커밋) | — | CTE 통합 세션 인계서, 지시서5개 발행, 후속작업큐 |
| PULLBACK-CONFIRM-001 | 03-01 | (본 커밋) | — | **17,155건 눌림확인 심층연구**: 5버킷분류, 8신호검증, VWAP지지 승률73.7%, 관통반등>터치반등(PF26.36>11.15) |
| CS-EQS-MATRIX-001 | 03-01 | (본 커밋) | — | **CS 5요소 설계+시뮬**: CS≥80 PF 2.383(+57%), EQS 5요소 설계, 9×9 매트릭스 81셀, 18금지/8시너지 규칙 |
| DD-VWAP-GATE-001 | 03-01 | (본 커밋) | — | **DD Decelerator 5단계**: maxDD -45.66%→-11.42%, VWAP 5변수, 5전략 반등확인게이트, ATR TP/SL NetR:R≥2.0 |
| MOMENTUM-TACTICS-001 | 03-01 | cc9069d | 200 | **A1(ORB) PASS(PF_ac=2.23)**, A3(1파) FAIL(PF_ac=0.60), C3(마이크로풀백) FAIL(PF_ac=0.47), ORB 5분+Top20 최적 |
| TIME-TACTICS-BULLFLAG-001 | 03-01 | (본 커밋) | — | 7×7 시간매트릭스, T_EARLY 모멘텀갭 확인, 불플래그 전체 FAIL(PF_ac=0.99) 단 T_PM_PB PASS(PF_ac=2.64) |
| EXIT-RULE-FINALIZE-001 | 03-01 | (본 커밋) | — | **D6 현행 D+1시초가 유지(PF13.63), D7 현행 유지(PF1.98), 갭리스크 D6=16.7%/D7=43.4%, D2/D4/D5 트레일링 전환 권고** |
| HAV-EXTEND-35VAR-001 | 03-01 | (본 커밋) | — | **27→35변수 확장 준비, 백업 완료, 8변수 솔로테스트 ALL 유효(PF1.0~2.71), coarse 유지+Bayesian 탐색 권고** |
| SLIPPAGE-SIM-001 | 03-01 | (본 커밋) | — | **60분 슬리피지 미미(0.01~0.03%), 고정60분 실효수익0.336% > 트레일링0.079%, 지정가-1틱 권고** |
| LIVE-PAPER-PRECHECK-001 | 03-01 | (본 커밋) | — | **모의매매 안전 PASS, D6=1건/D7=10건(02-27기준), v4_paper_trades 미존재→첫실행자동생성** |
| EXIT-SLIPPAGE-INTEGRATE-001 | 03-01 | (본 커밋) | — | **지정가-1틱 슬리피지 48% 개선(0.136→0.071%), 트레일링(지정가) D2/D4/D5 확정, D2 PF31.15 과적합→현실적2.2, D7 갭다운 43%→24%(종가위치≥0.80+Top10)** |
| V41-GO100-INTEGRATION-ARCH | 03-01 | (본 커밋) | 200 | **V4.1×GO100 통합 브릿지 아키텍처 기획서 v1.0**: 3대 브릿지(자본/리스크/메모리), 3대 안전수칙, Mermaid 데이터플로우, Phase1~3 마일스톤 |
| V41-GO100-BRIDGE-DESIGN-001 | 03-01 | 2fd7ac29 | 200 | **V4.1↔GO100 안전 브릿지 Phase 1 구현**: Go100BridgeClient(3메서드) + bridge.py 라우터(IP차단/Append-Only) + E2E 4건 PASS, V4.1_DESK_AGENT 독립 네임스페이스 확인 |
| ORB-INTEGRATE-OVERLAP-GUARD-001 | 03-01 | (본 커밋) | — | **A1(ORB) C8신규 컨디션+D-ORB 전략카드 설계, 자본15%, D6/D7 중복빈도 28건(77.8%), D6>D7>ORB 우선순위 차단, 7전략 포트폴리오 v2(예상PF2.8)** |
| HAV-DRYRUN-DRIFT-001 | 03-01 | (본 커밋) | — | **35변수 YAML 파싱 PASS(오류0건), dry-run 100건 PASS(PF12.26→12.24), Bayesian 3유효변수(body_size/atr/bb_width), drift_detector.py 수정 불필요 확인, 03-02 cron GO** |
| BOUNCE-GATE-IMPL-001 | 03-01 | (본 커밋) | — | **Cursor #14 Phase A-1**: BounceConfirmationGate(D2/D4/D5/S1/D7) + PullbackClassifier(B1~B6+25셀) + ConfirmationSignalEngine(8신호+SIG3+SIG6 권고), 단위 96케이스 전체PASS |
| DD-RISK-IMPL-001 | 03-01 | (본 커밋) | — | **Cursor #15 Phase A-2**: DDDecelerator(5레벨S1) + FiveLayerRiskManager(L1~L5) + DisasterPatternDetector(릴레이/집중도/과잉포지션), 단위 29케이스 전체PASS |
| CS-EQS-IMPL-001 | 03-01 | (본 커밋) | — | **Cursor #16 Phase A-3**: ConvictionScoreEngine(CS 100점) + ExecutionQualityScoreEngine(EQS 100점, ORDERBOOK 프록시) + TriggerTacticMatrix(81셀/금지18/시너지18), 단위 45케이스 전체PASS |
| CROSS-RELAY-PRESIM-001 | 03-01 | (본 커밋) | — | **241거래일 6전략 단리 시뮬(초기4천→4,061만, MDD7.8%), 동시5종목 최적, 복리비율1.1x(실제PF반영시1.5x예상), PF우선정책 권고, Go/No-Go 8기준 설계(CONDITIONAL GO)** |
| EQS-BIAS-CROSS-FILTER-001 | 03-01 | (본 커밋) | — | **EQS look-ahead 확인: PRICE_POSITION 당일H/L→LAG1(t-1 partial H/L) 교정. HIGH WR 85.2%→72.1%(-13.1%p), CS65_EQS65 최적조합(연550건, PF_net 2.499)** |
| GATE-OOS-WALKFORWARD-001 | 03-01 | (본 커밋) | — | **반등확인 게이트 OOS Walk-Forward: 5전략 Test PF_net >2.5 전원 PASS. 월별 PF<1.0 0개월. 2/3충족 기본버전 권장** |
| VWAP-RECONCILE-001 | 03-01 | (본 커밋) | — | **VWAP 모순 해소: #3의 35건 역전(60%<67.8%)은 표본오차. 통일정의(±0.3%+반등확인) 4,218건 기준 WR 67.4%>52.3%. 지지 2회+ 임계점(PF_net 2.64)** |
| PF-NORMALIZE-COST-ADJUST-001 | 03-01 | (본 커밋) | — | **PF 극단치 정규화: B3_SIG8 PF225만→Capped 142.8. 비용차감후 B4/B6 PF<1.0 → 진입금지. 3조합 SIG3+SIG6+SIG8이 PF_net_ac 16.74(최강)** |
| **CUR-V41-GO100-BRIDGE-PHASE2-001** | 03-01 | 1226fda3 | 200 | **GO100 브릿지 Phase 2 완료**: D6 모의투자 E2E 5건 전 PASS. 시나리오1=킬스위치OFF→메모리 적재(memory_id 4,5), 시나리오2=킬스위치Mock(True)→전종목 Halt 확인. backtest_engine_v2 스텁(삽입점 A/B) 비파괴 추가. Phase 3(실거래 활성화) 대기 |
| **CUR-V41-GO100-BRIDGE-PHASE3-001** | 03-01 | 85945058 | 200 | **GO100 브릿지 Phase 3 완료(포트폴리오 최적화 연동)**: `_run_entry_signals()` async 전환, 삽입점C(포트폴리오최적화 비중 기반 자본 동적 배분), weights=0 Skip, BridgeError→균등분배 Fallback 구현. `enable_go100_bridge=True` 기본값 활성화. `test_bridge_phase3_optimizer.py` 8건 전 PASS (Mock비중 66/16/9주 동적배분 증명) |
| **CUR-V41-PAPER-D6D7-WEEK1-001** | 03-01 | (본 커밋) | — | **D6/D7 페이퍼 트레이딩 첫 주 프레임 작성**: 사전점검 완료(D6#42/D7#43 PAPER_LIVE 활성), 모니터링 스크립트 신규(scripts/monitor_paper_d6d7.py), D7 갭다운 필터 이슈 발견(코드 0.70 vs 확정 0.80+Top10), 03-07 주간 결과 채움 예정 |
| **CUR-V41-CTE-PIPELINE-INTEGRATE-001** | 03-01 | 67602428 | — | **CTE 파이프라인 통합 + D7 핫픽스**: strategy_params.py(D2 EV+0.49% 교정, B4/B6 금지, concurrent=5, PF우선), test_cte_pipeline.py 33케이스 PASS, D7 종가위치≥0.80+Top10, DB#43 갱신 |
| **CUR-V41-VWAP-ATR-ENGINE-001** | 03-01 | e84ac1b9 | 200 | **Cursor #18 VWAP 엔진 + ATR 동적청산**: vwap_engine.py(5변수+TREND 선형회귀), atr_dynamic_exit.py(전략별 멀티플라이어/COST_ROUNDTRIP=0.47%/TRAILING_MA5), cte_pipeline.py(L3.2 VWAP지지체크+ATR_NETRR 차단), test_vwap_atr.py **25/25 PASS**, 기존 33테스트 비파괴 유지 |
| **CUR-GO100-AI-FEATURE-BATCH-V2-001** | 03-01 | (본 커밋) | — | **GO100 AI Feature Store v2 배치 빌드**: Track A(일봉 7피처: RSI_14/BB_WIDTH/OBV_NEW_HIGH/V_RVOL/MA_ALIGNMENT/PRICE_POSITION_LAG1/SEC_LEADER_FLAG) + Track B(분봉 2피처: VWAP_DEVIATION/VWAP_SUPPORT_COUNT) + news_frequency_3d + 라벨3추가(GAP_D1/MFE_60MIN/MFE_3D) + valid_label + NaN보존수정 + LABEL_ Z-score제외, 263,450rows/34cols/12parquet/26.24MB, 오류0건 |
| **CUR-V41-CTE-FULL-BACKTEST-001** | 03-01 | {SHA} | 200 | **Cursor #19 CTE 풀 백테스트 + 3-Fold WF**: prepare_cte_backtest.py+run_cte_full_backtest.py+run_cte_walkforward.py 신규. Full BT: PF_net=2.368/Sharpe=8.685/MDD=-2.43%/WR=65.8%/수익+227%. 3-Fold WF: 평균 Test PF=1.907/Sharpe=6.671/MDD=-2.17%, OOS/IS 3/3 PASS, PF Drop 3/3 PASS. 기준 10/10 충족 → **CEO Go/No-Go = GO. 60일 페이퍼 트레이딩 단계 진입** |
| **CUR-V41-DESK543-FRACTAL-RESEARCH-001** | 03-01 | (본 커밋) | — | **DESK5/4/3 프랙탈 추세추종 일봉 트리거 실증**: Task 0 사전 데이터 검증 PASS(v4_investor_daily 기관/외인 컬럼·NULL 0%, go100_news_items 공시/실적 분류, ohlcv_daily 급등 9,483건). Task 1~4 스크립트 준비(/tmp/task1_desk5_empirical.py 등). D-012 등록, DESK-FRACTAL-ARCHITECTURE v2.0 반영 |
| **CUR-V41-EQS-D4-PAPER-ACTIVATE-001** | 03-01 | (본 커밋) | — | **Cursor #20**: EQS LAG1(PRICE_POSITION t-1, ORDERBOOK 중립 8점), D4 ATR A안(sl 1.0/tp 5.0), CTE 페이퍼 연동(cron 50 8 * * 1-5), 테스트 70 PASS |

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
| **60일 페이퍼 트레이딩** | **진행** | CEO Go/No-Go = GO. D6/D7 PAPER_LIVE 가동. **CTE 파이프라인 연동 페이퍼 03-02 08:50 첫 실행 준비 완료** (live_paper_cte.py + monitor_paper_cte.py) |
| LIVE-PAPER-D6D7 | 진행 중 | D6(#42)+D7(#43) PAPER_LIVE. D7 핫픽스 적용완료(≥0.80+Top10) |
| **CS×EQS 이중필터 배포** | **다음** | CS65+EQS_LAG1 65 = 1순위 조합(연550건, PF_net 2.499). Layer 3.5/4.5 삽입 |
| **DESK5/4/3 구현** | **착수** | 프랙탈 추세추종 v2.0: Task 0 데이터 검증 완료. 스크립트 실행 후 결과 반영 |
| **반등확인 게이트 5전략 배포** | **다음** | OOS Walk-Forward PASS(avg PF 2.683). 2/3 충족 기본 버전으로 배포 |

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

---

## 6. 웹 Claude 인수인계 사항

> Cursor/Claude Code는 작업 완료 시 이 섹션을 반드시 업데이트한다.
> 웹 Claude는 새 세션 시작 시 이 섹션을 최우선 확인한다.

### 최신 상태 (2026-03-01, CTE 파이프라인 통합 + D7 핫픽스 — v4.5)

#### ★ 오늘 완료된 작업 요약 (v4.4 → v4.5)

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

### 웹 Claude / 다음 세션이 해야 할 일
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
