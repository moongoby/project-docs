# DESK2-BT-REVERSE-ENGINEER-001 보고서

**작업 ID:** DESK2-BT-REVERSE-ENGINEER-001  
**우선순위:** P0-CRITICAL  
**일자:** 2026-02-27  

**배경:** ESSENCE-CHECK-001에서 변동폭 TOP 종목 120개 중 DESK2 발굴 0건·거래 2.5% 수준으로, 현재 C1~C7 gate가 “돈 나는 종목”과 불일치함. 변동폭 TOP 종목이 낸 신호를 역설계해 gate 재교정 수행.

---

## 1. 역설계 결과: 120종목 × C1/C2/C4/C7 gate 통과율

**대상:** 2026-02-19, 02-20, 02-24, 02-25 4일 × 당일 변동폭 TOP 30 = 120종목 (시총 2000억+ 조건은 LEFT JOIN으로 시총 NULL 포함)

**실행:** `/tmp/reverse_engineer.py` → `/tmp/reverse_engineer_output.txt`, `/tmp/reverse_engineer_result.json`

### 1.1 현재 gate 기준 통과율

| Gate | 통과 | 비율 | 탈락 사유 TOP 5 |
|------|------|------|------------------|
| **C1** | 6/120 | 5.0% | mcap<2000억 53건, gap=0.0<3.0 20건, rvol<1.5 다수 |
| **C2** | 19/120 | 15.8% | rvol<1.5 (0.3~0.9) 다수 |
| **C4** | 62/120 | 51.7% | price<3000 10건, surge=1.9<2.0 1건 |
| **C7** | 4/120 | 3.3% | mcap<5000억 77건, drop>-3.5 23건, rsi>30 다수 |

### 1.2 탈락 사유 요약

- **C1:** 갭 3% 미만·시총 2000억 미만·RVOL 1.5 미만이 대부분. 변동폭 큰 종목이 “갭 상승”이 아닌 “저가→고가” 패턴이라 갭 조건과 불일치.
- **C2:** 09:00~09:30 상승률 1.5%·RVOL 1.5 미만 탈락 다수. 동일하게 장 초반 갭이 아닌 이후 상승 패턴.
- **C4:** 10분 급등 2%·시가 3000원 이상은 대부분 충족. 변동폭 TOP과 가장 잘 맞는 gate.
- **C7:** 시총 5000억·하락 3.5%·RSI 30 이하가 동시에 만족되는 경우가 적음.

### 1.3 상위 변동폭 종목 gate 요약

- **유투바이오(221800)** 44.82% 변동: C1·C2·C4 PASS, C7 FAIL (rsi·mcap).
- **현대지에프홀딩스(005440)** 40.65%: C4만 PASS (갭·ORB 미달).
- **링크솔루션(474650)** 34.24%: C4 PASS.
- **스피어(347700)** 33.95%: C4·C7 PASS.

---

## 2. Gate 재교정안: Calibration 결과 및 채택 값

**실행:** `/tmp/gate_calibration.py` → `/tmp/gate_calibration_result.txt`

### 2.1 단일 gate 완화 시뮬레이션

- **C1:** gap≥2.0, rvol≥1.0 → 30/120 (25%). gap≥1.5, rvol≥1.0 → 31/120 (26%).
- **C2:** orb≥1.0, rvol≥1.0 → 53/120 (44%). orb≥0.5, rvol≥1.0 → 54/120 (45%).
- **C4:** surge≥2.0 유지 시 119/120 (99%). 이미 변동폭 TOP과 잘 맞음.
- **C7:** 완화해도 50% 커버 어렵고, pass rate 5~30% 유지 목표에 맞춰 기존 수치 유지.

### 2.2 복합 조건 (C4 OR C2 OR C1)

- C4≥1.5 OR C2≥0.5 OR C1≥1.5 → **120/120 (100%)**  
- C4≥2.0 OR C2≥0.5 OR C1≥2.0 → **119/120 (99%)**

### 2.3 채택 gate 값 및 근거

- **TOP 120의 50%+ 커버** 및 **단일 gate pass rate 5~30%** 근사 충족을 위해 아래 적용.

| 항목 | 기존 | 재교정 | 근거 |
|------|------|--------|------|
| **C1** gap_min_pct | 3.0 | **2.0** | 25% pass, 복합 시 99% 커버 |
| **C1** min_rvol | 1.5 | **1.0** | 동일 |
| **C2** min_gain_pct | 1.5 | **1.0** | ORB 1% 이상 완화, 44% pass |
| **C2** min_rvol | 1.5 | **1.0** | 동일 |
| **C4** | 2.0 유지 | **2.0** | 이미 51.7% pass, 변동폭 TOP과 정합 |
| **C7** | 유지 | **유지** | 30% 이하·품질 유지 |

적용 위치: `desk2_config.yaml` → `discovery_gates` 섹션 추가, C1/C2/C4/C7 discovery 모듈이 config 참조하도록 수정.

---

## 3. 재교정 적용 내용 (Phase 3)

### 3.1 수정 파일

- **desk2_config.yaml**  
  - `discovery_gates` 섹션 추가: C1(gap_min_pct 2.0, min_rvol 1.0), C2(min_gain_pct 1.0, min_rvol 1.0), C4/C7 기존 값 명시.
- **base_condition.py**  
  - `_gate_overrides`, `set_gate_overrides()` 추가.
- **discovery_manager.py**  
  - `__init__(config)`에서 `discovery_gates`를 각 condition에 주입.
- **c1_gap_discovery.py, c2_opening_strong.py, c4_intraday_surge.py, c7_oversold_rebound.py**  
  - gate 수치를 `_gate_overrides`에서 읽고, 없으면 기존 상수 사용.
- **backtest_runner.py**  
  - `DiscoveryManager(self.config)`로 config 전달.

### 3.2 백테스트 세션

- **세션명 규칙:** `REVENG-R1-{YYYYMMDD}-{HHmm}` (실제로는 `BT-REVENG-R1-...` 형태로 저장될 수 있음)
- **테스트 일자:** 2026-02-19, 02-20, 02-24, 02-25 (IN-SAMPLE 4일)
- **실행:**  
  `scripts/backtest/desk2_live_parity_run.py --date <날짜> --capital 10000000 --session-name "REVENG-R1-..."`

### 3.3 재교정 후 매칭률

- **목표:** 거래 대비 변동폭 TOP 30 매칭률 2.5% → 50%+.
- **실측 (REVENG-R1 4일):**
  - 일별: 02-19·02-20·02-24 각 5건 거래, TOP30 매칭 0건(0%); 02-25 5건 중 2건 매칭(40%).
  - **전체: 거래 19건 중 TOP30 매칭 2건 → 10.5%.**
  - **TOP 120 종목 중 거래된 종목 수: 4/120 (3.3%).**
- 재교정으로 02-25에서 매칭 40%로 개선되었으나, 전체 목표 50%+에는 미달. C4 위주 발굴·DELTA_VWAP 위주 진입 구조상 변동폭 TOP과의 정합성을 더 끌어올리려면 C4 시간대·스코어링 추가 조정 또는 C1/C2 추가 완화 검토 필요.

---

## 4. 재교정 후 거래 결과

- **REVENG-R1 4일:** 02-19·02-20 각 5건, 02-24 4건, 02-25 5건 → 총 19건.
- 전략: DELTA_VWAP 다수, ECHO_ABCD 소수. 일별 일일 거래 한도 5건 도달.
- 02-19 final_total≈9,976,766 / 02-20≈10,039,632 / 02-24≈9,925,917.
- TOP 120 대비 매칭 4종목(3.3%), 거래 건수 대비 TOP30 매칭률 10.5%.

---

## 5. 진입/청산 효율

- **캡처율:** 실제 PnL / 당일 저가→고가 최대 수익 × 100. **실측 평균 캡처율: 0.1%** (손실 구간 다수로 인해 평균이 낮음).
- 개별: 02-25 012860 28.7% 최대수익 대비 2.47% PnL → 캡처 8.6%; 000270 13.9% 대비 2.70% → 19.4% 등.
- **타이밍 갭:** entry_time/exit_time이 DB에서 문자열 등으로 저장되어 분 단위 갭은 미집계(스크립트 보강 시 재계산 가능).

---

## 6. 발견된 문제점과 개선점

- 변동폭 TOP 종목의 대부분이 **갭 상승·ORB 강세**가 아니라 **장중 저가→고가** 패턴이며, C4(장중 급등)가 가장 잘 맞음.
- C1·C2는 gate 완화로 일부 커버 가능하나, pass rate 30% 이하 유지가 필요해 과도한 완화는 자제.
- C7은 시총 5000억·RSI 30 이하 조건이 변동폭 TOP과 맞지 않아, 별도 전략(과매도 반등)으로 유지하고 “변동폭 TOP 매칭” 목표에는 C1/C2/C4 재교정에 집중하는 것이 타당.

---

## 7. 다음 단계 권고

1. REVENG-R1 백테스트 4일 완료 후 `/tmp/reveng_validate.py`, `/tmp/reveng_efficiency.py` 실행해 매칭률·캡처율·타이밍 갭 수치 확정.
2. 매칭률 50% 미달 시 C4 surge 1.5% 검토 또는 C2 orb 0.5% 추가 완화 검토(저품질 유입 주의).
3. 실거래 반영 시 `discovery_gates`만 조정해 동일 코드 경로로 라이브와 백테스트 일치 유지.

---

**중간 산출물 보존:**  
- `/tmp/reverse_engineer.py`, `/tmp/reverse_engineer_output.txt`, `/tmp/reverse_engineer_result.json`  
- `/tmp/gate_calibration.py`, `/tmp/gate_calibration_result.txt`  
- `/tmp/reveng_validate.py`, `/tmp/reveng_efficiency.py`
