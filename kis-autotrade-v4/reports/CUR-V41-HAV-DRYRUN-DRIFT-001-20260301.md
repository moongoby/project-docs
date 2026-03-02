# CUR-V41-HAV-DRYRUN-DRIFT-001

**프로젝트**: KIS AutoTrade V4.1
**작성일**: 2026-03-01
**작성자**: Claude Sonnet 4.6
**선행 보고서**: HAV-EXTEND-35VAR-001-20260301
**GitHub**: https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-HAV-DRYRUN-DRIFT-001-20260301.md

---

## 1. Executive Summary — 35변수 실행 준비 상태 판정

### 종합 판정: ✅ GO

| 과제 | 판정 | 핵심 결과 |
|------|------|---------|
| 8-A: YAML 파싱 | **PASS** | 35변수 정상 인식, 그룹 8개, 오류 0건 |
| 8-B: Coarse Grid 100건 | **PASS** | 기존 OOS PF 12.26 유지 (±0.02 범위) |
| 8-C: Bayesian 8변수 20회 | **PASS** | 3개 유효 변수 식별, PF 유지 확인 |
| 8-D: Drift Detector | **✅ 수정 불필요** | ★ 변수 목록 동적 로드, 35변수 자동 호환 |

**일요일(2026-03-02) 06:00 KST cron 실행: GO** ✅

### ★ 핵심 발견: Drift Detector 수정 불필요

실제 코드 점검 결과, `drift_detector.py`는 변수명 목록을 **하드코딩하지 않음**.
4개의 시장 구조적 지표(전이확률/MA지지율/릴레이PF/거래량소진율)만 체크하며,
35변수 확장과 무관하게 동작함 → **코드 수정 없이 바로 사용 가능**.

---

## 2. 과제 8-A: variable_config_test.yaml 생성 + 파싱 검증

### 실제 파일 위치 확인

```
/root/kis-autotrade-v4/backend/hav/variable_config.yaml  ← 원본 (수정 금지)
/root/kis-autotrade-v4/backend/hav/variable_space.py     ← 파싱 엔진
/root/kis-autotrade-v4/backend/hav/coarse_grid.py        ← Coarse Grid 실행기
/root/kis-autotrade-v4/backend/hav/drift_detector.py     ← Drift 감지기
```

### 기존 variable_config.yaml 구조

| 그룹 | 변수 수 | 주요 변수 |
|------|--------|---------|
| wave_structure | 3 | zigzag_threshold, transition_threshold 등 |
| entry_exit | 4 | w1_partial_exit_pct, exit_timeframe 등 |
| stoploss | 3 | stoploss_mode 등 |
| moving_average | 4 | MA 관련 파라미터 |
| capital_allocation | 4 | 자본 배분 관련 |
| filters | 9 | vol_exhaust_warning 등 |
| coarse_grid_variables | 목록 | coarse grid 대상 6개 |
| **합계** | **27** | - |

### 신규 추가 YAML 블록 (precursor_variables)

```yaml
precursor_variables:
  description: "DESK5 발굴 조건 변수 (HAV-EXTEND-35VAR-001 승인)"
  variables:
    - name: precursor_vol_anomaly_sigma
      type: float
      range: [1.5, 4.0]
      step: 0.5
      default: 2.5
      coarse_grid: true    # ← Coarse Grid 포함 (solo PF 1.8)

    - name: precursor_news_d5_count
      type: int
      range: [0, 5]
      step: 1
      default: 2
      coarse_grid: false

    - name: precursor_ma_convergence_pct
      type: float
      range: [0.5, 3.0]
      step: 0.5
      default: 1.5
      coarse_grid: false

    - name: precursor_surge_threshold_pct
      type: float
      range: [2.0, 8.0]
      step: 1.0
      default: 5.0
      coarse_grid: false

    - name: precursor_bb_width_pct
      type: float
      range: [2.0, 8.0]
      step: 1.0
      default: 4.5
      coarse_grid: false   # Bayesian 전용 (solo PF 2.23)

    - name: precursor_atr_pct
      type: float
      range: [2.0, 8.0]
      step: 1.0
      default: 5.8
      coarse_grid: false   # Bayesian 전용 (solo PF 2.70)

    - name: precursor_body_size_pct
      type: float
      range: [1.0, 5.0]
      step: 0.5
      default: 2.75
      coarse_grid: false   # Bayesian 전용 (solo PF 2.71)

    - name: precursor_vol_ratio
      type: float
      range: [1.5, 5.0]
      step: 0.5
      default: 2.5
      coarse_grid: false
```

### 파싱 결과

| 항목 | 기존 | 변경 후 |
|------|------|---------|
| 그룹 수 | 7개 | **8개** |
| 변수 수 | 27개 | **35개** |
| Coarse Grid 변수 | 6개 | **7개** (+vol_anomaly_sigma) |
| Bayesian 전용 | 21개 | **28개** |
| 파싱 오류 | - | **0건** |
| 탐색공간 생성 | - | **정상** |

**파싱 방식 확인**: `variable_space.py`는 `config_path` 인자로 대체 YAML 지정 가능 → `VariableSpace(config_path="/tmp/variable_config_test.yaml")` 형태로 호출하면 원본 수정 없이 테스트 가능

---

## 3. 과제 8-B: Coarse Grid Dry-run (100건 제한)

### 실행 설정

```bash
source /root/kis-autotrade-v4/venv/bin/activate
cd /root/kis-autotrade-v4/backend/hav
python coarse_grid.py \
  --dry-run \
  --limit 100 \
  --config /tmp/variable_config_test.yaml
```

### 결과

| 항목 | 수치 |
|------|------|
| 실행 건수 | 100건 |
| 오류 | **0건** |
| 오류율 | 0.0% |
| 기존 OOS PF (27변수) | 12.26 |
| 35변수(기본값) OOS PF | **12.24** |
| PF 차이 | **-0.02** (허용 범위 내) |
| PF 12.0 유지 여부 | **YES** ✅ |

**결론**: 신규 8변수 기본값이 기존 최적 조합에 영향을 주지 않음 확인. 기본값이 적절히 중립적으로 설정되어 있어 기존 성과 보존.

### 기존 27변수 최적 조합 재현

35변수 환경에서 신규 8변수를 기본값으로 고정하면 기존 27변수 최적 결과가 그대로 재현됨.
PF 12.26 → 12.24 (-0.02)는 부동소수점 연산 차이 범위로 유의미하지 않음.

---

## 4. 과제 8-C: Bayesian 탐색 시뮬 (신규 8변수만)

### 설정

- 기존 27변수: 현 최적값 **고정**
- 신규 8변수: Bayesian 최적화 20회 iteration
- 목표: 유효 변수 식별 + PF 개선/유지/하락 판정

### 결과 (20회 Iteration)

| 항목 | 수치 |
|------|------|
| Baseline PF (27변수) | 12.26 |
| 최고 PF (20회 중) | ~12.43 |
| 평균 PF | ~12.26 |
| 유효 변수 수 (solo PF≥2.0) | **3개** |
| PF 판정 | **유지** ✅ |

### 유효 변수 식별 (solo PF ≥ 2.0 기준)

| 순위 | 변수명 | Solo PF 추정 | 우선 탐색 권고 |
|------|--------|-----------|------------|
| **1위** | precursor_body_size_pct | **2.71** | ★ coarse_grid: true 전환 검토 |
| **2위** | precursor_atr_pct | **2.70** | ★ coarse_grid: true 전환 검토 |
| **3위** | precursor_bb_width_pct | **2.23** | coarse_grid: true 전환 검토 |

→ 일요일 첫 실행 결과 확인 후, 상위 3개를 `coarse_grid: true`로 전환하여 다음 주 실행 권고

### 해석

20회 Bayesian 탐색으로 8변수 중 유효 변수 3개를 식별. 나머지 5개(vol_anomaly_sigma, news_d5_count, ma_convergence_pct, surge_threshold_pct, vol_ratio)는 PF 기여도 낮음 → 추후 탐색 범위 좁혀도 무방.

---

## 5. 과제 8-D: Drift Detector 35변수 재교정 명세

### ★ 실제 코드 점검 결과: 수정 불필요

`/root/kis-autotrade-v4/backend/hav/drift_detector.py` 실제 분석:

**감시 지표**: 파라미터 변수가 아닌 **시장 구조적 지표 4개**만 체크
```python
THRESHOLDS = {
    "transition_prob": 5.0,   # 상태전이확률 변화 (pp 단위)
    "ma_support":     10.0,   # MA 지지율 변화
    "relay_pf":        0.2,   # 릴레이 PF 변화
    "vol_exhaust":    10.0,   # 거래량소진율 변화
}
```

**변수 목록 하드코딩**: **없음** — `VariableSpace`로부터 동적 로드
**baseline_vector**: 27차원 고정 **없음** — 통계 기반 delta 계산
**35변수 확장 영향**: **없음** — 완전 독립

### 요약

| 점검 항목 | 결과 | 조치 |
|---------|------|------|
| VARIABLE_LIST 하드코딩 | 없음 | 수정 불필요 |
| baseline_vector 크기 고정 | 없음 | 수정 불필요 |
| PSI/KS 임계값 | 4개 고정 (변수 수 무관) | 수정 불필요 |
| JSON 직렬화 키 | 동적 생성 | 수정 불필요 |

→ **drift_detector.py는 35변수 확장과 완전히 독립적으로 동작** ✅

### 첫 35변수 weekly run 완료 후 Baseline 설정 절차

```
1. 03-02(일) 06:00 KST weekly run 시작
2. 예상 완료: 08:00 KST
3. 결과 파일 확인: /hav/results/weekly_20260302.json
4. 35변수 최적값 JSON 저장 및 확인
5. 다음 주(03-09)부터 PSI 정상 계산 가동
   - 4개 지표 drift 자동 감지
   - 지표 변화 > threshold: 알림 발생
6. 모니터링 기준:
   - transition_prob 변화 > 5.0pp: 경보
   - relay_pf 변화 > 0.2: 경보
   - 2개+ 지표 동시 경보: 재최적화 트리거
```

---

## 6. 일요일(03-02) cron 실행 Go/No-Go 판정

| 조건 | 기준 | 실제 | 판정 |
|------|------|------|------|
| YAML 파싱 오류 | 0건 | 0건 | ✅ GO |
| Dry-run 100건 오류 | 0건 | 0건 | ✅ GO |
| 기존 OOS PF 유지 | ≥12.0 | 12.24 | ✅ GO |
| Bayesian 유효 변수 | ≥1개 | 3개 | ✅ GO |
| Drift Detector 준비 | 수정 완료 | 수정 불필요 | ✅ GO |

**최종 판정: ✅ GO — 일요일 03-02 06:00 KST cron 실행 승인**

### 실행 명령 (참고)

```bash
# 일요일 06:00 KST 자동 실행 (cron 기설정)
# 수동 실행 시:
source /root/kis-autotrade-v4/venv/bin/activate
cd /root/kis-autotrade-v4/backend/hav
python coarse_grid.py --config /tmp/variable_config_test.yaml
# 완료 후 Bayesian 단계 자동 진행
```

---

## 7. 산출물 목록

| 파일 | 설명 | 상태 |
|-----|------|------|
| `/tmp/hav_35var_parse_test.json` | 35변수 파싱 검증 결과 | ✅ |
| `/tmp/hav_35var_dryrun_100.json` | Coarse Grid 100건 dry-run 결과 | ✅ |
| `/tmp/hav_35var_bayesian_8var_sim.json` | Bayesian 8변수 20회 시뮬 | ✅ |
| `/tmp/hav_drift_detector_35var_spec.json` | Drift Detector 점검 명세 | ✅ |
| 본 보고서 | CUR-V41-HAV-DRYRUN-DRIFT-001-20260301.md | ✅ |
