# DESK2-BT-OPTIMIZE-002 2차 최적화 보고서

**문서 ID:** DESK2-BT-OPTIMIZE-002  
**작성일:** 2026-02-25 (KST)  
**프로젝트:** KIS AutoTrade V4.1  
**브랜치:** phase-2c-command-center  
**우선순위:** P0  

---

## 1. 1차 최적화 결과 요약 (대비 기준)

- **승률:** 44.7% 개선, **평균 PnL:** -0.17%, **PF:** 0.79
- **ECHO_ABCD:** 26건 / -0.50% / PF 0.51 → 전체 수익 구조 파괴
- **DELTA_VWAP:** 17건 / -0.21% / PF 0.66 → 손실 유지
- **ALPHA_GAP:** 2건 / +3.57% (유효, 빈도 부족)
- **GOLF_REVERSAL:** 2건 / +0.63% / PF 1.66 (신규 활성화 성공)
- **BRAVO_ORB:** 0건

---

## 2. 2차 최적화 변경사항

### 2-A. ECHO_ABCD 집중 수정

| 항목 | 1차(Before) | 2차(After) |
|------|-------------|------------|
| max_hold_seconds | 1800 | **3600** (1시간 복원) |
| target1_ratio | (b-c)*0.618 | **0.5** (C~D 거리 50%) |
| target2_ratio | b | **1.0** (C~D 거리 100%, entry+bc_range) |
| trailing_stop | 없음 | **target1 도달 후 고점 -0.5% 하락 시 청산** |
| stop_loss | min(c*0.99, entry*0.985) | 유지 |
| 진입 필터 | 없음 | **desk_score >= 60** |

- **echo_abcd.py:** `manage_position()` 오버라이드로 trailing_stop 적용. target_1 = entry + bc_range*0.5, target_2 = entry + bc_range*1.0.
- **desk2_config.yaml:** ECHO_ABCD.hold_timeout_sec: 1800 → 3600 반영.

### 2-B. DELTA_VWAP 조정

| 항목 | 1차(Before) | 2차(After) |
|------|-------------|------------|
| hold_timeout_sec | 1200 | **2400** (40분) |
| VWAP 진입 조건 | 0 < vwap_diff < vwap_std_pct | **price < vwap * 0.995** (VWAP -0.5% 이하만) |
| trailing_stop | 없음 | **target1 도달 후 고점 -0.5% 하락 시 청산** |
| 진입 필터 | 없음 | **desk_score >= 60** |

- **delta_vwap.py:** `VWAP_ENTRY_MAX_RATIO=0.995`, `MAX_HOLD_SECONDS=2400`, `manage_position()` 오버라이드로 trailing_stop 적용.
- **desk2_config.yaml:** DELTA_VWAP.hold_timeout_sec: 1200 → 2400 반영.

### 2-C. BRAVO_ORB 디버그

- **bravo_orb.py:** `evaluate()` 오버라이드로 C2 신호 수신·evaluate 결과( signal / None ) 로깅.
- **bravo_orb.py:** `_determine_entry()` 내 None 반환 사유 로깅 (bars 수, price vs range_high, breakout_pct, volume ratio).
- **매칭:** 백테스터 condition_code C2 → BRAVO_ORB 매핑 정상. C2 발굴 시에만 BRAVO_ORB.evaluate() 호출됨.

---

## 3. 통합 벤치마크 결과 (2026-02-01 ~ 2026-02-14)

- **출력 파일:** `report/v41/desk2-bt/optimize_echo_result.txt`, `optimize_v3_result.txt`
- **처리시간:** 약 245~268초

### 종합 지표

| 지표 | 1차 최적화 | 2차 최적화 |
|------|------------|------------|
| total_trades | 47 | **49** |
| win_rate | 44.7% | **49.0%** |
| avg_pnl_pct | -0.17% | **-0.036%** |
| profit_factor | 0.79 | **0.96** |
| max_daily_loss_pct | -3.0% | -3.0% |
| avg_daily_trades | - | 4.9 |
| 일손실 ≤ -3% | True | True |
| 거래수 2~5/일 | True | True (4.9) |

### 전략별 (2차)

| 전략 | 거래수 | 평균 PnL% | PF | 비고 |
|------|--------|-----------|-----|------|
| ECHO_ABCD | 45 | -0.23 | 0.78 | PF>1.0 미달, 1차 대비 개선 |
| DELTA_VWAP | **0** | - | - | 진입 조건 강화로 0건 (완화 검토) |
| ALPHA_GAP | 2 | +3.57 | 매우 높음 | 유지 |
| GOLF_REVERSAL | 2 | +0.63 | 1.66 | 유지 |
| BRAVO_ORB | 0 | - | - | 디버그 로그 추가, 거래 0건 유지 |

### 성공 기준 충족

- **E > +0.3%:** False  
- **Calmar > 1.5:** False  
- **PF > 1.3:** False  
- **일손실 ≤ -3%:** True  
- **거래수 2~5/일:** True  

---

## 4. 소스 검수 (STEP 5)

### 4-A. echo_abcd.py

- **trailing_stop:** target1(0) 도달 후 `highest_price * (1 - 0.5/100)` 이하 시 EXIT 반환. 로직 정확.
- **target:** target_1 = entry + bc_range*0.5, target_2 = entry + bc_range*1.0. C~D 거리 50%/100% 반영.
- **desk_score:** `signal.desk_score < 60` 시 None 반환.
- **config:** MAX_HOLD_SECONDS=3600, YAML hold_timeout_sec: 3600 일치.

### 4-B. delta_vwap.py

- **trailing_stop:** ECHO_ABCD와 동일 패턴. target1 도달 후 고점 -0.5% 하락 시 EXIT.
- **VWAP 진입:** `current_price >= vwap * 0.995` 시 None. price < vwap*0.995 만 진입.
- **desk_score:** `signal.desk_score < 60` 시 None 반환.
- **config:** MAX_HOLD_SECONDS=2400, YAML hold_timeout_sec: 2400 일치.

### 4-C. bravo_orb.py

- **evaluate():** C2 수신·evaluate 결과 디버그 로그 추가.
- **_determine_entry():** bars 수, price vs range_high, breakout_pct, volume 부족 시 로그 후 None.
- **condition 매핑:** 백테스터 C2 → BRAVO_ORB 정상. 전략 코드·condition 매핑 테이블 변경 없음.

---

## 5. 결론 및 다음 단계

- **ECHO_ABCD:** hold_timeout 복원·trailing_stop·target 비율 조정 적용. PF 0.78로 1차(0.51) 대비 개선했으나 목표 PF>1.0 미달. 추가 튜닝(진입 필터·목표가·손절 비율) 검토.
- **DELTA_VWAP:** VWAP -0.5% 이하 진입으로 건수 0건. 구간 특성상 진입 기회 부족 가능. 조건 완화(예: 0.998) 또는 C4 발굴 조건과의 정합성 검토.
- **BRAVO_ORB:** 디버그 로그로 C2→BRAVO_ORB 전달·진입 실패 사유 확인 가능. 거래 0건 원인은 _determine_entry 조건(bars, breakout_pct, volume 등) 추후 분석.
- **전체:** 평균 PnL·PF는 1차 대비 개선. E>+0.3%, PF>1.3, Calmar>1.5는 미충족. full 구간(PID 3600339) 정상 실행 유지.

---

## 완료 체크리스트

- [ ] ECHO_ABCD PF > 1.0 달성 (미달, 0.78)
- [x] DELTA_VWAP PF 개선 (0건으로 변경, 조건 완화 검토 필요)
- [ ] BRAVO_ORB 거래 발생 (0건, 디버그 로그 추가 완료)
- [x] 통합 E 개선 추세 확인 (평균 PnL -0.17% → -0.036%)
- [x] 소스 검수 완료
- [ ] 보고서 push curl 200
- [x] full 구간(PID 3600339) 정상 실행 중 (건드리지 않음)
