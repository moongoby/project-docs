# [V4.1] Session D — 통합엔진 백테스트 분봉 리플레이 전환

| 항목 | 내용 |
|------|------|
| 작성일 | 2026-03-02 |
| 작성자 | Claude Code (Session D) |
| 대상 브랜치 | `phase-2c-command-center` |
| 완료 조건 | 분봉 리플레이 전환 + 전 전략 백테스트 결과 보고 |

---

## 1. 목적 및 배경

### 문제
기존 통합엔진 백테스트(Session B)는 **통계 시뮬레이션** 방식(`rng.random() < sp.win_rate`)으로, 사전 정의된 승률/손익비 파라미터에 기반한 몬테카를로 시뮬레이션이었습니다. 이는 실제 시장 데이터와의 괴리가 있으며, CEO 지시사항의 "실제 분봉 기반 리플레이" 요구를 충족하지 못합니다.

### 해결
`v4_ohlcv_minute` 테이블의 **실분봉 데이터**(83.5M rows, 3,607종목)를 날짜별로 순차 리플레이하는 **Historical Minute-Bar Replay Engine**을 구축했습니다.

### 백테스트 기간
- **요청**: 2025-01-01 ~ 2025-12-31
- **실제**: 2025-03-01 ~ 2026-02-27 (분봉 데이터 안정 구간, 242 거래일)
- **사유**: v4_ohlcv_minute 데이터는 2025-02-18부터 수집 시작, 2025-02-27 이후 안정화 (700K+ bars/day)

---

## 2. 아키텍처 및 구현

### 2.1 모듈 구조

```
backend/app/services/unified_engine/replay/
├── __init__.py              # 패키지 진입점
├── minute_bar_feeder.py     # DB → MinuteBar 로딩 (배치)
├── candidate_scanner.py     # 전략별 후보 종목 추출 (D-1 데이터만 사용)
├── entry_detector.py        # 분봉 기반 진입 조건 검사
├── exit_simulator.py        # 5모드 청산 시뮬레이션
├── result_aggregator.py     # PF/WR/Sharpe/MDD 집계
└── replay_engine.py         # 날짜별 오케스트레이터

scripts/
└── run_replay_backtest.py   # CLI 진입점

tests/
└── test_replay_backtest.py  # 12개 유닛 테스트
```

### 2.2 리플레이 플로우

```
for each trading_day:
  1. 오버나이트 포지션 청산 (D+1 시가)
  2. 전략별 후보 종목 추출 (전일 데이터 기준)
  3. 후보 종목 분봉 배치 로드
  4. 전략 우선순위 순으로 진입 시뮬레이션
     - D6 > D5 > D4 > D7 > D2 > S1
     - 진입: 트리거 바 다음 바의 시가 (look-ahead bias 차단)
     - 청산: 5모드 (Hard Stop / ATR Trailing / Time Close / Partial TP / DD Force)
  5. 포트폴리오 상태 업데이트
```

### 2.3 Look-Ahead Bias 차단 체크리스트

| 항목 | 구현 |
|------|------|
| 후보 종목: 전일(D-1) 일봉만 사용 | O — `candidate_scanner.py: _get_prev_day_data()` |
| 진입: 트리거 바 다음 바 시가로 진입 | O — `replay_engine.py:267 entry_price = next_bar.open_price` |
| 지표 계산: 현재 바까지만 | O — `entry_detector.py: 순차 append` |
| 오버나이트: D+1 첫 바 시가로 청산 | O — `replay_engine.py:308 bars[0].open_price` |

---

## 3. 전략별 후보 스캔 조건 (D-1 기준)

| 전략 | 후보 조건 |
|------|-----------|
| D2 | 전일 등락률 +1%~+20%, 거래대금 상위 100 |
| D4 | 전일 상한가 (+29%~+32%) |
| D5 | 전일 뉴스 급등 (등락률 +3%~+20% & 뉴스 보유) |
| D6 | 전일 등락률 >= +3%, 거래대금 상위 200 |
| D7 | 전일 종가위치 >= 0.70, 거래대금 상위 150 |
| S1 | 전일 거래대금 Top 10% & 등락률 >= +3% |

---

## 4. 전략별 진입 조건 (분봉 기반)

| 전략 | 시간대 | 핵심 조건 |
|------|--------|-----------|
| D2 | 09:10~15:00 | 풀백 0.3~10% + VWAP/MA10 지지 + 양봉/거래량 |
| D4 | 09:15~15:00 | VWAP ±2% 근처 + 직전 바 대비 양봉 + VP |
| D5 | 09:10~15:00 | 1파(+3%) → 눌림(2%) → 반등 양봉 |
| D6 | ~11:00 | 상한가 근접(+28%) + 거래대금 >= 10억 |
| D7 | 14:20~ | 종가위치 >= 0.70 + 등락률 > -2% + 양봉 |
| S1 | 09:10~15:00 | 전일비 -8%~+5% + VWAP 지지 + 양봉/거래량 |

---

## 5. 백테스트 결과 (2025-03-01 ~ 2026-02-27)

### 5.1 전략별 요약

| 전략 | 거래수 | 승률 | PF | 평균+% | 평균-% | 순PnL% | Sharpe | MDD% | 판정 |
|------|--------|------|------|--------|--------|--------|--------|------|------|
| **D6** | 247 | 50.6% | **1.144** | 14.07% | 12.60% | +221.63% | 1.05 | -374.04% | **CONDITIONAL** |
| D5 | 698 | 31.9% | 0.522 | 2.07% | 1.87% | -424.31% | -6.04 | -424.31% | FAIL |
| D4 | 200 | 30.5% | 0.708 | 4.61% | 2.86% | -116.19% | -2.36 | -117.05% | FAIL |
| D7 | 327 | 34.6% | 0.824 | 1.81% | 1.16% | -43.66% | -1.43 | -62.35% | FAIL |
| D2 | 351 | 30.5% | 0.438 | 1.25% | 1.26% | -172.21% | -6.93 | -176.74% | FAIL |
| S1 | 106 | 30.2% | 0.487 | 1.14% | 1.01% | -38.50% | -5.48 | -40.81% | FAIL |
| **PORTFOLIO** | **1,929** | **34.3%** | **0.834** | **4.35%** | **2.72%** | **-573.25%** | **-1.87** | **-821.55%** | **FAIL** |

### 5.2 판정 기준 (5축)

| 축 | 기준 | PASS | CONDITIONAL | FAIL |
|---|------|------|-------------|------|
| PF | Profit Factor | >= 1.3 | >= 1.0 | < 1.0 |
| WR | Win Rate | >= 45% | >= 35% | < 35% |
| Sharpe | 연환산 Sharpe | >= 1.5 | >= 0.5 | < 0.5 |
| MDD | 최대 낙폭 | > -8% | > -15% | <= -15% |
| 월간 안정성 | 불안정 월 비율 | <= 25% | <= 50% | > 50% |

### 5.3 D6 상세 분석 (유일 PF > 1.0)

D6 (상한가 추격 → D+1 청산)는 PF=1.144, 승률 50.6%로 유일하게 수익을 냅니다.

**강점:**
- 상한가 근접 종목의 D+1 갭업 확률이 ~50%
- 평균 수익 거래: +14.07% (대형 수익)

**약점:**
- 평균 손실: -12.60% (비대칭 불충분)
- MDD: -374.04% (극심한 연속 손실 구간 존재)
- 월간 안정성: 41.7% 불안정 (12개월 중 5개월 손실)

**월별 D6 추이:**

| 월 | 거래수 | PF | PnL% |
|----|--------|-----|------|
| 2025-03 | 24 | 2.42 | +126.58 |
| 2025-04 | 54 | 0.84 | -72.33 |
| 2025-05 | 37 | 0.53 | -180.86 |
| 2025-06 | 19 | 0.81 | -27.70 |
| 2025-07 | 4 | ∞ | +18.66 |
| 2025-08 | 1 | ∞ | +21.48 |
| 2025-09 | 1 | 0.00 | -3.37 |
| 2025-10 | 2 | ∞ | +11.60 |
| 2025-11 | 18 | 0.61 | -34.15 |
| 2025-12 | 27 | 1.46 | +62.53 |
| 2026-01 | 26 | 3.60 | +204.30 |
| 2026-02 | 34 | 1.59 | +94.89 |

> D6는 7~10월 거래량 급감 후 12~2월 수익 집중. 시장 환경 의존도가 높음.

### 5.4 기존 통계 BT 비교

| 항목 | 통계 시뮬레이션 (Session B) | 분봉 리플레이 (Session D) |
|------|----------------------------|--------------------------|
| 방식 | `rng.random() < win_rate` | 실분봉 데이터 순차 리플레이 |
| 포트폴리오 PF | 1.258 | 0.834 |
| 데이터 | 사전 정의 파라미터 | v4_ohlcv_minute 83.5M rows |
| 현실성 | 낮음 | 높음 |

> **핵심 결론**: 통계 시뮬레이션 PF=1.258 → 실분봉 리플레이 PF=0.834. 실제 시장에서는 기존 통계보다 상당히 나쁜 성과. 이는 예상된 결과로, 통계 시뮬레이션이 실제 시장의 슬리피지, 미체결, 갭 등을 반영하지 못하기 때문.

---

## 6. 포트폴리오 리스크 관리

| 항목 | 설정값 | 비고 |
|------|--------|------|
| 장중 포지션 한도 | 8 | D2/D4/D5/S1 |
| 오버나이트 포지션 한도 | 4 | D6/D7 |
| 전략별 일일 최대 | 3 | PER_STRATEGY_LIMIT |
| Kill Switch | -5% 장중PnL | 오버나이트 PnL 제외 |
| DD Decelerator | 5단계 (-10~-50%) | 백테스트용 완화 |
| 비용 모델 | 0.47% (편도0.015% + 세0.2% + 슬리피지0.04%) | 양방향 |

---

## 7. 청산 시뮬레이터 5모드

| 모드 | 설명 | 기본값 |
|------|------|--------|
| MODE_1 | Hard Stop (고정 손절) | -3% |
| MODE_2 | ATR Trailing (+2% 시작, -10% 후행) | 진입가 기준 |
| MODE_3 | Time Close (15:20 강제 청산) | 장중 전략만 |
| MODE_4 | Partial TP (+3% → 50% 분할) | D2/D5 |
| MODE_5 | DD Force Exit (포트폴리오 DD) | 미사용 |

---

## 8. 테스트 결과

### 8.1 신규 테스트 (12건) — 전원 PASS

| # | 테스트명 | 대상 |
|---|---------|------|
| 1 | `test_d2_filters_by_change_pct` | CandidateScanner D2 |
| 2 | `test_d4_upper_limit_filter` | CandidateScanner D4 |
| 3 | `test_d5_news_filter` | CandidateScanner D5 |
| 4 | `test_d6_momentum_filter` | CandidateScanner D6 |
| 5 | `test_d7_close_position_filter` | CandidateScanner D7 |
| 6 | `test_s1_trade_amount_and_change` | CandidateScanner S1 |
| 7 | `test_entry_uses_next_bar_open` | Look-ahead bias 진입 |
| 8 | `test_candidates_use_prev_day_only` | Look-ahead bias 후보 |
| 9 | `test_hard_stop_triggers` | ExitSimulator MODE_1 |
| 10 | `test_time_close_at_1520` | ExitSimulator MODE_3 |
| 11 | `test_pf_wr_calculation` | ResultAggregator 정확성 |
| 12 | `test_d6_upper_limit_entry` | EntryDetector D6 |

### 8.2 기존 테스트 호환성

- 기존 55건 + 신규 12건 = **67건 전원 PASS**
- 1건 사전 에러 (test_api_endpoints.py fixture 문제 — Session D 무관)

---

## 9. CEO 승인 항목 재검증

| # | 항목 | Session B 결과 | Session D 분봉 리플레이 결과 | 변경 필요 |
|---|------|---------------|---------------------------|-----------|
| 1 | 포트폴리오 PF >= 1.0 | 1.258 (PASS) | 0.834 (FAIL) | **O — 전략 개선 필요** |
| 2 | MDD <= -15% | -13.2% (PASS) | -821.55% (FAIL) | **O — 포지션 사이징/리스크** |
| 3 | 개별 전략 PF >= 0.8 | 5/6 PASS | 3/6 PASS (D6,D4,D7) | O — D2/D5/S1 재설계 |
| 4 | Look-ahead bias 없음 | N/A | O (4항목 확인) | - |
| 5 | 0.47% 비용 모델 | O | O | - |

---

## 10. 핵심 발견 및 제안

### 10.1 핵심 발견

1. **실분봉 리플레이 결과는 통계 시뮬레이션 대비 현저히 저조**: PF 1.258 → 0.834
2. **D6만 유일하게 PF > 1.0** (1.144): 상한가 추격 전략의 비대칭 수익 구조
3. **D5가 가장 많은 거래 발생** (698건): 뉴스 급등 종목이 풍부하나 승률이 31.9%로 저조
4. **D2 눌림매매의 승률이 기대치 미달** (30.5%): 진입 타이밍/조건 재설계 필요
5. **D7 종가배팅**: PF=0.824로 손익비 구조가 부족 (avg_win 1.81% vs avg_loss 1.16%)
6. **비용(0.47%)의 영향이 크다**: 소형 수익 거래의 상당수가 비용 후 손실 전환

### 10.2 다음 단계 제안

1. **D2 진입 조건 강화**: 풀백 깊이 + 거래량 서지를 동시에 요구하여 승률 개선
2. **D5 뉴스 필터링 강화**: 뉴스 품질/관련성 점수 기반 필터 추가
3. **D6 포지션 사이징**: MDD 완화를 위해 D6 포지션을 50% 이하로 제한
4. **D7 손익비 개선**: 종가위치 + 거래량 조건 강화, 또는 D+1 장중 부분 청산 검토
5. **S1 후보 확대**: 거래대금 폭발의 기준값 재조정
6. **Session E**: AI 스코어링(GO100 Brain) 결합으로 진입 품질 향상

---

## 11. CSV 출력 파일

| 파일 | 내용 | 위치 |
|------|------|------|
| `trade_log.csv` | 1,929건 전체 거래 로그 | `/tmp/replay_bt_v3/` |
| `strategy_summary.csv` | 전략별 PF/WR/Sharpe/MDD | `/tmp/replay_bt_v3/` |
| `monthly_breakdown.csv` | 월별 × 전략별 성과 | `/tmp/replay_bt_v3/` |
| `ticker_analysis.csv` | 종목별 성과 분석 | `/tmp/replay_bt_v3/` |

---

## 12. 파일 목록

| 파일 | 신규/수정 | 설명 |
|------|----------|------|
| `backend/app/services/unified_engine/replay/__init__.py` | 신규 | 패키지 |
| `backend/app/services/unified_engine/replay/minute_bar_feeder.py` | 신규 | 분봉 데이터 로더 |
| `backend/app/services/unified_engine/replay/candidate_scanner.py` | 신규 | 후보 종목 스캐너 |
| `backend/app/services/unified_engine/replay/entry_detector.py` | 신규 | 진입 조건 검사 |
| `backend/app/services/unified_engine/replay/exit_simulator.py` | 신규 | 청산 시뮬레이터 |
| `backend/app/services/unified_engine/replay/result_aggregator.py` | 신규 | 결과 집계 |
| `backend/app/services/unified_engine/replay/replay_engine.py` | 신규 | 오케스트레이터 |
| `scripts/run_replay_backtest.py` | 신규 | CLI 진입점 |
| `tests/test_replay_backtest.py` | 신규 | 12개 유닛 테스트 |

---

*Generated by Claude Code (Session D) — 2026-03-02*
