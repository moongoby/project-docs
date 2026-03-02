# DESK2 프로젝트 인수인계서 v3.0

**작성일**: 2026-02-27
**작성자**: Claude PM (대화 세션 3)
**인계 대상**: 새 Claude PM 세션
**저장 위치**: 서버 `/root/project-docs/kis-autotrade-v4/handover/` + GitHub push

---

## 1. 프로젝트 개요

**V4.1 핵심 철학**: DESK1~5는 주식의 생애주기(파동/웨이브)를 나타내는 연결된 시스템이다. DESK5(장기 추세 시작) → DESK4(중기 스윙) → DESK3(단기 스윙) → DESK2(1~3일 폭발) → DESK1(스캘핑 수확). 종목은 데스크 간 승격·강등되며 연속 모니터링된다. 이것이 CEO의 최초 기획이자 핵심 비전이다.

**DESK2 미션**: 당일 수익률 최대 종목을 발굴하여 100% 확신으로 진입, 최적 타이밍에 청산. "숲(전체 시장) → 나무(종목) → 가지(타이밍) → 열매(수익) 수확" 구조.

---

## 2. 완료된 분석 (6개 보고서, 모두 검증 완료)

**보고서 1: DESK2-BT-BLANK-SLATE-001-20260227**
- 14거래일(02/03~02/25), 매일 TOP-20 수익률 종목 280건 추출
- 평균 최대수익 25.8%, 중앙값 24.8%
- 56% 중형주(500~5,000억), 97% 양봉, 94% 당일 뉴스, 평균 갭 +1.37%
- 61% 저가 09:00~09:05 발생, 88% 09:30 이전
- 핵심 발견: RVOL≥3(75% 커버), 10분 변동≥+1%(TOP +2.48% vs 대조군 -0.12%)

**보고서 2: DESK2-BT-SUPPLY-DEMAND-DEEP-001-20260227**
- 280 TOP vs 280 대조군 수급 심층분석 (9개 Phase)
- D-5→D-1 거래량 +456%(대조군 +23%), 뉴스 보유 95.7%(대조군 60%)
- OBV 바닥 ≤09:30: TOP 67.5% vs 대조군 37.1%
- 체결강도 패턴B(매수압력): TOP 31.8% vs 대조군 17.9%
- 익일 보유 시 +2.6pp 추가 수익(16.8% vs 14.2%)
- 반복 등장 종목 30개, 평균 간격 3.7일, 익일 재등장 20.4%

**보고서 3: DESK2-BT-TREND-CLASSIFY-SIMULATE-001-20260227**
- 유형 분류: TREND(dip<1%) 88건/31.4%/평균24.2%, BORDER(1~2%) 54건/19.3%/23.7%, REVERSAL(≥2%) 138건/49.3%/27.7%
- AND 필터 시뮬: Recall 0.4%(1/280), Precision 25%, F1 0.7 → 사실상 사용 불가
- R4(거래량가속도)와 R6(RVOL)이 FP의 77% 원인

**보고서 4: DESK2-BT-SCORING-REVERSAL-DESIGN-001-20260227**
- AND → 스코어링 전환: Recall 0.4% → 99.6% (124배 개선)
- 가중치: F3(D-1거래량비율) 0.822, F2(5일거래량변화) 0.757, F1(뉴스) 0.472, F4(종가위치) 0.365
- R4, R6 가중치 ≈ 0 → 제거 권장
- 최적 컷오프 ≥1.93: TP 261, FP 58, FN 19, Recall 93.2%, Precision 81.8%, F1 0.871
- 연속값 AUC: D-1/5일 거래량비율 0.911, 5일 거래량변화 0.878
- **A-5 수급전환신호**: REVERSAL S1(체결강도 반전) 99% 발생, 중앙값 저가 후 7분, MFE +21.9%; TREND T5(시가+2% 돌파) 97% 발생, 중앙값 1분, MFE +19.9%

**보고서 5: DESK2-BT-PRECISION-FILTER-FP-001-20260227**
- 2단계 필터(C6: 뉴스≥2, C7: 종가위치≥0.6): Precision 4.4% → 56.4% (12.8배)
- TOP-10 포트폴리오(140거래): 승률 74.3%, 평균순이익 +1.31%, 누적 +183.4%
- 하락장에서도 +0.92% 평균수익
- FP 79%가 "수용 가능"(평균최대수익 +9.7%), 진짜 불량 FP 11%만

**보고서 6: DESK2-BT-DEEP-DIAGNOSIS-001** (기존 전략 진단)
- 기존 C1~C7 전략 4일 백테스트 20건 분석
- TARGET_PROFIT 버그: bb_middle 기반 목표가가 진입가보다 낮은 경우 발생
- 소액 이익 수수료 소멸 문제
- → 새 DESK2 엔진에서는 해당 로직 미사용, 기존 카드 병행 시 수정 필요

---

## 3. 확정된 전략 구조

**1단계: D-1 사전 스코어링 (전날 15:40)**
- 전체 종목 → 스코어링(F3×0.822 + F2×0.757 + F1×0.472 + F4×0.365)
- 2차 필터: 뉴스≥2건(C6), 종가위치≥0.6(C7)
- 상위 10종목 선정 → v4_desk2_candidates 저장 → 텔레그램 알림

**2단계: 실시간 유형 분류 (09:00~09:15)**
- 후보 10종목의 분봉 모니터링
- dip% = (시가-저가)/시가 × 100
- TREND(dip<1%): 시가부터 상승, OBV 즉시 우상향
- REVERSAL(dip≥2%): 시초 하락 후 반등

**3단계: 진입 신호 (실시간)**
- TREND: T5 신호(시가 대비 +2% 돌파) 확인 후 +1분 진입
- REVERSAL: S1 신호(체결강도 <0.4 → ≥0.6 반전) 확인 후 +1~2분 진입

**4단계: 청산 (⚠️ 미확정 - PARAM-OPTIMIZE 보고서 대기)**
- 현재 임시값: 전체 +3% / -2%
- 데이터 기반 최적값: TREND 추세추종 +7.19%, REVERSAL 고정 +3%
- TREND 손절 -2%, REVERSAL 손절 -3%
- 시간청산 14:50
- → Cursor 1(PARAM-OPTIMIZE) 보고서로 최종 확정 필요

---

## 4. 현재 병렬 진행 중인 5개 커서 작업

| 커서 | Task ID | 내용 | 상태 |
|------|---------|------|------|
| 1 | DESK2-PARAM-OPTIMIZE-001 | 유형별 청산/손절/사이징 최적화 (14일) | 진행중 |
| 2 | DESK2-LONGTERM-BT-001 | 장기 백테스트 (전체 v4_ohlcv_minute 기간) | 진행중 |
| 3 | DESK2-INFRA-001 | DB 테이블·systemd 서비스 구축 | 진행중 |
| 4 | DESK2-ENGINE-IMPL-001 | 엔진 코드 구현 (prescoring/signal/trader) | 진행중 |
| 5 | DESK2-DASHBOARD-001 | 모니터링 대시보드 | 진행중(P1) |

**새 세션 즉시 확인 사항**: 각 커서의 보고서 완료 여부 확인 → 완료된 것부터 분석 → 파라미터 확정 → config 반영 → 통합 테스트

---

## 5. 절대 규칙 (CEO 지시, 위반 시 즉시 중단)

**서비스 규칙**
- kis-v41-api, monitor, scheduler 재시작 절대 금지 (CEO 승인 시 1회만)
- strategy_cards 테이블 ALTER/DROP/DELETE 금지
- v4_positions 직접 UPDATE/DELETE 금지
- 핵심 파일 수정 시 CEO+Claude 검수 후 적용

**핵심 파일 (수정 시 반드시 리뷰)**: v4_pipeline_orchestrator.py, strategy_engine.py, risk_manager.py, order_executor.py, position_manager.py, split_transfer_engine.py, lifecycle.py, fund/*, adaptive/*, regime_detector.py, backtest_engine_v2.py, collector_minute.py, main.py

**작업 전 확인**: strategy_cards=62건, v4_positions OPEN=5건

**작업 후 필수**: report/v41/{작업ID}-{YYYYMMDD}.md 작성 → /root/project-docs/에 복사 → git push → HTTP 200 확인

**코드 규칙**: datetime.utcnow() 금지 → datetime.now(timezone.utc), 로깅 f-string 금지 → logger.info("msg %s", var), .env/.bak 커밋 금지

---

## 6. 환경 정보

- **서버**: root@211.188.51.113
- **프로젝트 경로**: /root/kis-autotrade-v4
- **가상환경**: /root/kis-autotrade-v4/.venv (또는 venv)
- **PYTHONPATH**: /root/kis-autotrade-v4/backend
- **Branch**: phase-2c-command-center
- **DB**: PostgreSQL 16, localhost:5432, DB명 kisautotrade, 유저 kis_admin
- **Python**: 3.12, FastAPI, asyncpg, Redis 7.x
- **도메인**: trading41.newtalk.kr
- **서비스**: kis-v41-api(8003), monitor, scheduler (모두 active)
- **분봉 데이터**: v4_ohlcv_minute 19,468,781행
- **스캘핑 유니버스**: v4_scalping_universe 708종목
- **디스크**: 53% 사용, 45GB 여유

**계정 현황**: config 4(모의)-81201280, 5(실전)-52568156, 6(실전)-63109343

---

## 7. 기존 데이터 파일 위치

- /tmp/blank_slate_phase{1,2,3}.json (각 280건 TOP 종목 데이터)
- /tmp/sd_phase{0~8}_result.json (수급분석 결과)
- /tmp/sd_control_group.json (대조군 280건)
- /tmp/tc_partA_result.json, /tmp/tc_partB_result.json (유형분류+필터 시뮬)
- /tmp/sr_partA_result.json, /tmp/sr_partA_features.json (스코어링 가중치)
- /tmp/sr_partA5_result.json (수급전환신호 S1/T5 분석)
- /tmp/pf_partA_result.json, /tmp/pf_partB_result.json, /tmp/pf_partC_result.json (정밀필터+FP분석+국면검증)

---

## 8. 문서 참조

- **공개 규칙**: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/rules/kis-v41-rules.md
- **서버 규칙**: /root/kis-autotrade-v4/.cursor/rules/kis-v41-rules.md
- **CLAUDE.md**: /root/kis-autotrade-v4/CLAUDE.md
- **CONTEXT.md**: /root/kis-autotrade-v4/CONTEXT.md
- **보고서 디렉토리**: /root/project-docs/kis-autotrade-v4/reports/
- **보고서 동기화**: bash /root/project-docs/scripts/sync_reports.sh

---

## 9. CEO 대기 중인 결정 사항

1. DESK 간 중복 매수 정책 (같은 종목 여러 DESK에서 보유 가능 여부)
2. 레짐 기반 DESK2 진입 제한 정책
3. 레짐 전환 방어 48시간 적용 여부
4. strategy_cards 61-62 처리 방안
5. index_daily OHLC=0 재수집 여부

---

## 10. 새 세션 즉시 행동 지침

1. 이 인계서를 GitHub에서 확인: `https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/handover/DESK2-HANDOVER-v3-20260227.md`
2. 5개 커서 보고서 완료 여부 확인 (CEO에게 질문)
3. **Cursor 1(PARAM-OPTIMIZE) 보고서 최우선 분석** → 청산 파라미터 확정
4. **Cursor 2(LONGTERM-BT) 보고서 분석** → 14일 결과의 장기 유효성 검증
5. 확정된 파라미터를 Cursor 4(ENGINE)의 desk2_config.yaml에 반영
6. 통합 테스트 → 드라이런 → 실전 투입

**CEO 목표**: 오늘(2026-02-27) 중 실전 테스트까지 완료
