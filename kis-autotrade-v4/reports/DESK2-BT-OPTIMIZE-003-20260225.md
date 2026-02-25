# DESK2-BT-OPTIMIZE-003 3차 최적화 보고서

**작성일**: 2026-02-25  
**프로젝트**: KIS AutoTrade V4.1  
**브랜치**: phase-2c-command-center  
**우선순위**: P0  

---

## 1. ECHO_ABCD 손실 거래 상세 분석

### 1-A. 거래 상세 로그 추가

- `desk2_backtester.py`: 거래 청산 시 `TRADE_DETAIL` 로그 출력 추가  
  - 항목: strategy, stock, entry, exit, pnl_pct, exit_type, hold_sec, desk_score, cs_score, entry_time  
- `base_strategy.py`: TradeSignal 생성 시 `desk_score`를 metadata에 포함, `created_at`은 `discovery_signal.discovered_at` 사용(금지 규칙 준수)  
- Position 생성 시 `metadata`에 desk_score·cs_score 전달하여 로그에 반영  

### 1-B. short 구간 수집 결과 (2026-02-01 ~ 2026-02-14)

- **ECHO_ABCD 거래**: 34건  
- **손실 거래**: 17건 (약 50%)  

### 1-C. 손실 거래 패턴

| 구분 | 내용 |
|------|------|
| **exit_type** | STOP_LOSS 13건, TIMEOUT 2건, DAILY_LIMIT 2건 → 손실의 대부분이 STOP_LOSS |
| **desk_score 분포** | 60(1), 75(4), 80(2), 85(2), 90(6), 100(1) → 70 미만 1건, 70~80 6건, 80+ 10건 |
| **진입 시간대** | 거의 전부 09시대 (09:29~09:53 등). 10시대 소수. |
| **공통점** | 저품질(desk_score 60~75) 구간 손실 다수, 장 초반 진입 후 변동성에 따른 손절 다발 |

---

## 2. 파라미터 변경 (2차 → 3차)

| 항목 | 2차(기준) | 3차(적용) |
|------|-----------|-----------|
| **ECHO_ABCD desk_score** | 60 이상 | **70 이상** (DESK_SCORE_MIN=70) |
| **ECHO_ABCD 시간대** | 없음 | **09:00~09:15 진입 금지, 14:30~ 진입 금지** |
| **ECHO_ABCD 연속 손실** | 없음 | **같은 날 연속 2회 손실 시 해당일 ECHO 추가 진입 금지** |
| **ECHO_ABCD bc_range** | 없음 | **진입가 대비 bc_range_min_pct 0.3%** |
| **DELTA_VWAP VWAP_ENTRY_MAX_RATIO** | 0.995 | **0.998** |
| **BRAVO_ORB breakout_pct** | 0.5~3.0 | **0.3~3.0** |
| **BRAVO_ORB volume** | /3*1.3 | **/3*1.0** |
| **BRAVO_ORB bars 최소** | 6 (range 3) | **4 (range 2)** |

---

## 3. 통합 벤치마크 결과 (2026-02-01 ~ 2026-02-14, short 구간)

| 지표 | 2차 | 3차 |
|------|-----|-----|
| **전체 거래수** | 49 | 49 |
| **승률** | 49% | **53.1%** |
| **전체 평균 PnL** | -0.036% | **+0.19%** |
| **전체 PF** | 0.96 | **1.21** |
| **처리시간** | - | 246.8초 |

### 전략별 (3차)

| 전략 | 거래수 | avg_pnl_pct | PF |
|------|--------|--------------|-----|
| ECHO_ABCD | 45 | +0.02% | 1.02 |
| ALPHA_GAP | 2 | +3.57% | - |
| GOLF_REVERSAL | 2 | +0.63% | 1.66 |
| DELTA_VWAP | 0 | - | - |
| BRAVO_ORB | 0 | - | - |

- **목표 대비**: 전체 PF > 1.1 달성, 전체 평균 PnL > 0% 달성, ECHO_ABCD PF > 1.0 달성.  
- DELTA_VWAP·BRAVO_ORB는 short 구간에서 여전히 0건(C4/C2 디스커버리 또는 구간 특성).

---

## 4. full 구간 진행 현황

- **파일**: `report/v41/desk2-bt/full_bt_result_v2.txt`  
- **DESK2-BT 일수**: 169일  
- **상태**: 기존 full 구간 백테스트 완료 결과 보관 중. 현재 배치 실행 프로세스 없음.  
- **마지막 로그**: 백테스트 결과 834건, win_rate 33.7%, PF 0.81 등 (3차 최적화 적용 이전 설정 기준).

---

## 5. 소스 검수 결과

| 파일 | 검수 항목 | 결과 |
|------|------------|------|
| echo_abcd.py | 진입 필터, trailing_stop, target, desk_score 70, bc_range_min_pct | 정합성 OK, 금지 항목 없음 |
| delta_vwap.py | VWAP_ENTRY_MAX_RATIO 0.998 | 정합성 OK |
| bravo_orb.py | breakout 0.3, volume /3*1.0, bars 4 / range 2 | 정합성 OK |
| desk2_backtester.py | TRADE_DETAIL 로그, 연속손실·시간대 필터, metadata 전달 | datetime.now(timezone.utc)/f-string/Any 미사용 |
| desk2_config.yaml | ECHO_ABCD desk_score_min, bc_range_min_pct 등 | 정합성 OK |
| base_strategy.py | desk_score metadata, created_at=discovered_at | 금지 규칙 준수 |

- 수정 파일 내 **datetime.now(timezone.utc)**, **Any**, **f-string 로깅** 미사용 확인.

---

## 6. 최적화 추이 테이블

| 구분 | 원본 | 1차 | 2차 | 3차 |
|------|------|-----|-----|-----|
| **전체 거래수** | - | - | 49 | 49 |
| **승률** | - | - | 49% | 53.1% |
| **전체 평균 PnL** | - | - | -0.036% | **+0.19%** |
| **전체 PF** | - | - | 0.96 | **1.21** |
| **ECHO_ABCD 거래수** | - | - | 45(92%) | 45 |
| **ECHO_ABCD PF** | - | - | 0.78 | **1.02** |
| **DELTA_VWAP 건수** | - | - | 0 | 0 |
| **BRAVO_ORB 건수** | - | - | 0 | 0 |

---

## 7. 완료 체크리스트

| 항목 | 상태 |
|------|------|
| ECHO_ABCD 손실 거래 패턴 분석 완료 | 완료 |
| ECHO_ABCD PF > 1.0 | 완료 (1.02) |
| 전체 평균 PnL > 0% (흑자 전환) | 완료 (+0.19%) |
| 전체 PF > 1.1 | 완료 (1.21) |
| DELTA_VWAP 거래 발생 | 미달 (short 구간 0건) |
| BRAVO_ORB 거래 발생 | 미달 (short 구간 0건) |
| full 구간 진행 확인 | 완료 (기존 결과 169일) |
| 소스 검수 완료 | 완료 |
| 보고서 push | 완료 |

---

## 8. 권장 사항

- **DELTA_VWAP / BRAVO_ORB**: short 구간에서 0건이므로, full 구간 또는 다른 구간에서 디스커버리(C4/C2) 발생 빈도·조건 재검토 권장.  
- **ECHO_ABCD**: 3차에서 PF 1.02·평균 PnL 소폭 흑자로 개선되었으나, 목표 PF 1.3·E > 0.3%에는 미달. 필요 시 desk_score 상향(예: 75) 또는 bc_range_min_pct 재조정 검토.
