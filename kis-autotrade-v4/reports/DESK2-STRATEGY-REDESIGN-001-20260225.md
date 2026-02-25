# DESK2-STRATEGY-REDESIGN-001 전략 재설계 보고서

**지시서**: DESK2-STRATEGY-REDESIGN-001  
**작성일**: 2026-02-25  
**프로젝트**: KIS AutoTrade V4.1  
**브랜치**: phase-2c-command-center  
**우선순위**: P0  

---

## 1. full 구간 상세 분석 (v3 기준)

### 1-A. 월별 ECHO_ABCD 성과

- **출처**: `full_bt_result_v3.txt` TRADE_DETAIL 716건 → `all_trades_detail.txt` 추출 후 월별 집계  
- **결과**: `report/v41/desk2-bt/monthly_analysis.txt`

| 월      | 건수 | 승률   | 평균 PnL | 누적 PnL |
|---------|------|--------|----------|----------|
| 2025-06 | 74   | 48.6%  | -0.03%   | -2.16%   |
| 2025-07 | 80   | 38.8%  | -0.34%   | -29.10%  |
| 2025-08 | 78   | 38.5%  | -0.27%   | -50.12%  |
| 2025-09 | 90   | 47.8%  | -0.10%   | -59.36%  |
| 2025-10 | 72   | 45.8%  | -0.28%   | -79.69%  |
| 2025-11 | 91   | 46.2%  | -0.08%   | -87.19%  |
| 2025-12 | 85   | 45.9%  | -0.33%   | -115.33% |
| 2026-01 | 92   | 50.0%  | -0.21%   | -134.32% |
| 2026-02 | 54   | 55.6%  | 0.26%    | -120.31% |

- 7·8월 승률 최저(38%대), 2026-02만 평균 PnL 양수. 전 구간 누적 -120%대.

### 1-B. 청산 유형별 분석

| exit_type   | 건수 |
|------------|------|
| TRAILING   | 291  |
| STOP_LOSS  | 237  |
| TIMEOUT    | 126  |
| DAILY_LIMIT| 62   |

- 손실 유발: STOP_LOSS 237건, TIMEOUT·DAILY_LIMIT 다수.

### 1-C. desk_score 구간별 승률·평균 PnL

| 구간    | 건수 | 승률   | 평균 PnL |
|---------|------|--------|----------|
| 60-69   | 3    | 66.7%  | -0.17%   |
| 70-79   | 241  | 45.2%  | -0.34%   |
| 80-89   | 76   | 50.0%  | 0.12%    |
| 90-99   | 360  | 45.6%  | -0.14%   |
| 100-109 | 36   | 47.2%  | 0.12%    |

- 70-79 구간 비중 높고 평균 PnL 최저 → desk_score 80 상향으로 고품질만 진입하는 방향 정합.

---

## 2. 근본 원인과 대응

### 2-A. ECHO_ABCD 거래 과다 제한

- **원인**: full 716건 중 ECHO_ABCD 683건(95%) 단일 전략 의존, Short에서 PF 1.21 → Full에서 0.82 과적합.
- **대응**  
  - 일일 ECHO 최대 거래수: 5건 → **2건**  
  - 동시 ECHO 포지션: 3 → **1**  
  - desk_score 최소: 70 → **80** (echo_abcd.py DESK_SCORE_MIN, config desk_score_min)

### 2-B. MDD 방어 강화

- **대응**  
  - 주간 MDD 한도: **-5%** (config `weekly_mdd_pct: -5.0`, 백테스터에서 주간 누적 -5% 도달 시 해당 주 나머지 거래 중단)  
  - 연속 손실 방어: **3연속 손실** 시 해당일 전체 전략 거래 중단  
  - 전략별 일일 거래 제한: ECHO_ABCD 일 2건 상한 적용  

### 2-C. 전략 다각화 (ALPHA_GAP)

- C1 `gap_min_pct`: 1.0 → **0.5**  
- C1 `volume_ratio_min`: 1.5 → **1.2**  
- config·c1_gap_discovery.py 상수 동기화  

### 2-D. GOLF_REVERSAL 빈도 증가

- C7 RSI_OVERSOLD: 30 → **35**  
- C7 STRENGTH_DROP_BAD_NEWS_PCT: -20 → **-15**  
- GOLF RSI_THRESHOLD: 30 → **35**, VOLUME_SURGE_RATIO: 1.5 → **1.2**  

### 2-E. DELTA_VWAP 재활성화

- VWAP_ENTRY_MAX_RATIO(0.998) **제거**, desk_score ≥ 70으로 진입 품질 관리 (delta_vwap.py에서 70 기준 적용).  

### 2-F. BRAVO_ORB 재활성화

- C2 breakout_threshold_pct: 0.5 → **0.2**  
- BRAVO breakout_pct 하한: 0.3 → **0.2** (bravo_orb.py, config breakout_pct_min 0.2)  

---

## 3. 리스크 관리 강화 내역

- **파일**: `backend/app/services/trading/desk2/tests/desk2_backtester.py`  

| 항목 | 내용 |
|------|------|
| 주간 MDD 방어 | 월요일 `_weekly_start_pnl_pct` 리셋, 매일 종료 후 `_cumulative_pnl_pct` 갱신, 주간 PnL ≤ -5% 시 `_skip_rest_of_week = True` 로 해당 주 나머지 거래 중단 |
| 연속 손실 방어 | 매일 `_consecutive_losses` 리셋, 청산 시 pnl < 0이면 +1, else 0. 3 이상이면 `_skip_rest_of_day = True` 로 해당일 추가 진입 중단 |
| 전략별 일일 제한 | `_daily_strategy_trades` 로 전략별 일일 건수 집계, ECHO_ABCD 일 2건 상한·동시 ECHO 포지션 1건 제한 |

---

## 4. Short/Medium 벤치마크 결과

### 4-A. Short 구간 (2026-02-01 ~ 2026-02-14)

- **실행**: `report/v41/desk2-bt/redesign_short_result.txt`  
- **결과**  

| 지표 | 값 |
|------|-----|
| total_trades | 50 |
| win_rate | 36.0% |
| avg_pnl_pct | -0.17% |
| profit_factor | **0.77** |
| max_drawdown_pct | -10.50% |
| avg_daily_trades | 5.0 |
| 일손실 ≤ -3% | 충족 |
| 거래수 2~5/일 | 충족(5.0) |

전략별: ALPHA_GAP 2건, GOLF_REVERSAL 6건, ECHO_ABCD 15건, DELTA_VWAP 27건, BRAVO_ORB 0건.  
- **목표 대비**: Short PF > 1.2 **미달**(0.77). MDD -10.5%는 -20% 목표 충족. 전략 분산 충족(ECHO 30%, 4개 전략 거래).

### 4-B. Medium 구간 (2025-11-01 ~ 2026-02-14)

- **실행**: `report/v41/desk2-bt/redesign_medium_result.txt`  
- **상태**: 백그라운드 실행 후 결과 파일 확인 필요. 목표 Medium PF > 1.0, MDD < -20%, 전략 분산 유지.

---

## 5. 최적화 전체 추이

| 구간 | 원본/1차 | 2차 | 3차(Short) | full v3 | 재설계 Short |
|------|----------|-----|------------|---------|--------------|
| full 거래수 | - | - | - | 716 | - |
| full 승률 | - | - | - | 46% | - |
| full PF | - | - | - | 0.82 | - |
| full MDD | - | - | - | -52% | - |
| Short PF | - | 0.96 | 1.21 | - | 0.77 |
| ECHO 비중 | - | - | - | 95% | 30% |
| 전략 수 | - | - | - | 1주력 | 4개 |

- 재설계 Short에서 PF는 목표 미달이나, ECHO 비중 감소·전략 다각화·리스크 제한은 적용 완료.

---

## 6. 소스 검수 결과

- **리스크 관리**: 주간 MDD -5%, 연속 3손실 일중단, ECHO 일 2건·동시 1포지션 제한 구현 확인.  
- **파라미터**: desk2_config.yaml, C1/C2/C7 discovery, ECHO/DELTA/BRAVO/GOLF 전략 상수·config 일치 확인.  
- **금지 사항**: strategy_cards/v4_positions 미변경, datetime.now(timezone.utc)/Any/f-string 로깅 미사용 확인.  

---

## 7. full 재실행 상태

- **벤치마크**: Short PF > 1.2 미달(0.77)로 **STEP 5 full 구간 재실행은 보류**.  
- **권고**: PF 목표 달성을 위해 STEP 2 파라미터 재조정(예: ECHO 일 1건·desk_score 85, 또는 손절/타겟 비율 조정) 후 Short/Medium 재벤치마크 권장.  
- **실행 명령(벤치마크 통과 시)**  
  `nohup bash -c 'PYTHONPATH=backend .venv/bin/python backend/app/services/trading/desk2/tests/desk2_backtester.py --start 2025-06-01 --end 2026-02-21 --capital 10000000 --strategy ALL' > report/v41/desk2-bt/full_bt_result_v4.txt 2>&1 &'`

---

## 완료 체크리스트

- [x] 월별/청산유형/desk_score 분석 완료  
- [x] 리스크 관리 3개(주간 MDD, 연속 손실, 전략별 제한) 구현  
- [x] 전략 다각화(최소 3개 전략 거래 발생)  
- [ ] Short PF > 1.2 (미달 0.77)  
- [ ] Medium PF > 1.0 (결과 확인 대기)  
- [x] MDD < -20% (Short -10.5% 충족)  
- [x] 소스 검수 완료  
- [ ] 보고서 push curl 200  
- [ ] full 재실행(벤치마크 통과 시 보류)  
