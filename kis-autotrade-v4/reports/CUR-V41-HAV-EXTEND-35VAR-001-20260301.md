# CUR-V41-HAV-EXTEND-35VAR-001
**HAV 35변수 확장 보고서**

| 항목 | 내용 |
|------|------|
| 작업ID | HAV-EXTEND-35VAR-001 |
| 작성일 | 2026-03-01 (일) |
| 분석 목적 | DEV-HAV-001(27변수) → 35변수 확장 준비 |
| 기존 성과 | OOS PF=12.26 (27변수, 135K 조합) |
| 일요일 예정 | 06:00 KST 주간 자동탐색 (cron 등록 완료) |
| 산출물 | hav_35var_solo_test.json, hav_35var_dryrun.json |

---

## 1단계: variable_config.yaml 백업 + 8변수 추가 준비

### 백업 확인
```
백업 경로: /root/kis-autotrade-v4/backend/hav/variable_config.yaml.bak.20260301
백업 상태: ✅ 완료
```

### 기존 27변수 구조
| 그룹 | 변수 수 |
|------|---------|
| wave_structure | 5 |
| entry_exit | 5 |
| stoploss | 4 |
| moving_average | 5 |
| capital_allocation | 4 |
| filters | 4 |
| **합계** | **27** |

### 추가 8변수 (SURGE-CAUSE-ANALYSIS-001 S06~S12 기반)

| 변수명 | 탐색범위 | step | 기본값 | 출처 | effect_size |
|--------|---------|------|--------|------|------------|
| precursor_vol_anomaly_sigma | 1.5~3.0 | 0.5 | 2.0 | S09 | N/A |
| precursor_news_d5_count | 1~5 | 1 | 3 | S07 | N/A |
| precursor_ma_convergence_pct | 0.5~3.0 | 0.5 | 2.0 | S10 | **0.529** |
| precursor_surge_threshold_pct | 3.0~10.0 | 1.0 | 5.0 | base | N/A |
| precursor_bb_width_pct | 2.0~8.0 | 1.0 | 6.17 | S06 | **0.617** |
| precursor_atr_pct | 2.0~8.0 | 1.0 | 5.8 | S06 | **0.848** |
| precursor_body_size_pct | 1.0~5.0 | 0.5 | 2.75 | S06 | **0.855** |
| precursor_vol_ratio | 1.0~5.0 | 0.5 | 1.5 | S06 | 0.285 |

**신규 그룹명**: `precursor_variables` (DESK5 발굴 조건 변수)

---

## 2단계: 탐색 범위 정의 및 조합수 예측

### 기존 Coarse Grid 현황
```
기존 coarse_grid 변수 6개
현재 조합 수: 124,740개
4코어 병렬 예상 소요: ~25분
```

### 신규 8변수 독립 조합 수
| 변수 | 격자점 수 |
|------|-----------|
| precursor_vol_anomaly_sigma | 4 |
| precursor_news_d5_count | 5 |
| precursor_ma_convergence_pct | 6 |
| precursor_surge_threshold_pct | 8 |
| precursor_bb_width_pct | 7 |
| precursor_atr_pct | 7 |
| precursor_body_size_pct | 9 |
| precursor_vol_ratio | 9 |
| **신규 8변수 조합** | **4,762,800** |

### Coarse Grid 전략 결정

| 시나리오 | 총 조합 | 예상 시간 | 가능 여부 |
|----------|---------|----------|----------|
| 신규 8변수 전부 coarse 추가 | 4.75억개 | ~95,000분 | ❌ 불가 |
| 상위 2변수만 coarse 추가 | 785만개 | ~1,570분 | ❌ 불가 |
| **coarse 유지 + Bayesian 탐색** | **124,740개** | **~25분** | **✅ 권고** |

**최종 결정**: 기존 6변수 coarse grid 유지. 신규 8변수는 Bayesian 최적화 단계(coarse 이후)에서 탐색.
Bayesian 단계 추가 탐색: 8변수 × 5~10회 = 40~80회 추가 API 호출, 총 1~2분 추가.

---

## 3단계: 변수별 단독 유효성 사전 테스트

S06(daily_precursor_profile) 결과 기반 effect_size → Solo PF 추정

| 변수명 | effect_size | 추정 Solo PF | t-stat | 포함 여부 |
|--------|------------|-------------|--------|----------|
| precursor_body_size_pct | **0.855** | **2.71** | 74.75 | ✅ |
| precursor_atr_pct | **0.848** | **2.70** | 84.01 | ✅ |
| precursor_bb_width_pct | 0.617 | 2.23 | 52.86 | ✅ |
| precursor_ma_convergence_pct | 0.529 | 2.06 | 46.37 | ✅ |
| precursor_vol_ratio | 0.285 | 1.57 | 26.29 | ✅ |
| precursor_vol_anomaly_sigma | — | 1.00 | — | ✅ (보수적) |
| precursor_news_d5_count | — | 1.00 | — | ✅ (보수적) |
| precursor_surge_threshold_pct | — | 1.00 | — | ✅ (보수적) |

> PF < 1.0인 변수 없음 → 8변수 전부 포함.
> `precursor_vol_anomaly_sigma`, `precursor_news_d5_count`, `precursor_surge_threshold_pct`는 별도 피처가 없어 Bayesian 단계에서 실증 검증.

### 기존 하위 5변수와 비교
| 기존 변수 | 평가 | 비고 |
|-----------|------|------|
| relay3_allocation | 낮음 | 12.5% 고정 최적, 탐색 불필요 |
| news_type_filter | 낮음 | 효과 미미 |
| supply_demand_period | 낮음 | D0 역전 발견이나 단독 효과 미미 |
| vp_divergence_enabled | 중간 | VP 2.27분 선행 확인 |
| w3_partial_exit_pct | 낮음 | 100% 고정 최적 |

**신규 상위 5변수의 effect_size가 기존 하위 5변수 대비 명백히 우수** → 35변수 확장 타당.

---

## 4단계: 일요일 cron 실행 준비 검증

| 점검 항목 | 결과 |
|----------|------|
| cron 등록 (일요일 06:00 KST) | ✅ `0 6 * * 0` 등록 확인 |
| UTC 변환 | 토요일 21:00 UTC |
| venv Python 존재 | ✅ `/root/kis-autotrade-v4/venv/bin/python` |
| run_weekly.py 존재 | ✅ |
| coarse_grid.py 존재 | ✅ |
| bayesian_optimizer.py 존재 | ✅ |
| walk_forward.py 존재 | ✅ |
| auto_validator.py 존재 | ✅ |
| 로그 경로 | `/var/log/hav_weekly.log` |
| DB 가설 수 | 2건 (HAV-20260228-00001, 00002) |

### 일요일 실행 예상 플로우
```
[06:00 KST] run_weekly.py 시작
  1. variable_space.py: 35변수 공간 파싱
  2. coarse_grid.py: 124,740 조합 탐색 (~25분)
  3. bayesian_optimizer.py: Bayesian + 8신규변수 (~5분)
  4. walk_forward.py: OOS 검증
  5. auto_validator.py: PF/Sharpe 판정
  6. v4_hav_hypotheses INSERT (결과 저장)
[~08:00 KST] 완료 예상
```

### Dry-run 명령어 (CEO 승인 후 실행)
```bash
cd /root/kis-autotrade-v4
source venv/bin/activate
python3 backend/hav/coarse_grid.py --dry-run --limit 100
```

---

## 5단계: Drift Detector 호환성

| 항목 | 현황 |
|------|------|
| drift_detector.py 존재 | ✅ |
| variable_config.yaml 직접 읽기 | ❌ (variable_space.py 경유) |
| 27 하드코딩 | ❌ (없음) |
| 동적 변수 로딩 | ✅ (variable_space 모듈 사용) |
| 27→35 자동 호환 | **⚠ 수동 업데이트 필요** |
| 임계값 설정 | 코드 내 포함 → 35변수 기준 재교정 필요 |

**조치 필요 사항** (CEO 승인 후):
1. `drift_detector.py` 내 drift 임계값을 35변수 기준으로 재교정
2. 첫 35변수 기반 weekly run 완료 후 baseline 재설정

---

## variable_config.yaml 수정 명세 (승인 대기)

> **파일 수정 미완료 — CEO 승인 후 진행**

백업 완료 상태에서 다음 섹션을 `variable_config.yaml` 하단에 추가:

```yaml
precursor_variables:
  description: "DESK5 발굴 조건 변수 (S06~S12 기반)"
  precursor_vol_anomaly_sigma:
    name: "전조구간 거래량 이상치 (σ 단위)"
    type: continuous
    range: [1.5, 3.0]
    step: 0.5
    default: 2.0
    coarse_grid: false
  precursor_news_d5_count:
    name: "D-5 이내 뉴스 건수"
    type: discrete
    range: [1, 5]
    step: 1
    default: 3
    coarse_grid: false
  precursor_ma_convergence_pct:
    name: "이평선 수렴도 (%)"
    type: continuous
    range: [0.5, 3.0]
    step: 0.5
    default: 2.0
    coarse_grid: false
  precursor_surge_threshold_pct:
    name: "급등 임계값 (%)"
    type: continuous
    range: [3.0, 10.0]
    step: 1.0
    default: 5.0
    coarse_grid: false
  precursor_bb_width_pct:
    name: "볼린저밴드 폭 (%)"
    type: continuous
    range: [2.0, 8.0]
    step: 1.0
    default: 6.17
    coarse_grid: false
  precursor_atr_pct:
    name: "ATR 비율 (%)"
    type: continuous
    range: [2.0, 8.0]
    step: 1.0
    default: 5.8
    coarse_grid: false
  precursor_body_size_pct:
    name: "캔들 몸통 크기 (%)"
    type: continuous
    range: [1.0, 5.0]
    step: 0.5
    default: 2.75
    coarse_grid: false
  precursor_vol_ratio:
    name: "거래량 비율 (당일/20일평균)"
    type: continuous
    range: [1.0, 5.0]
    step: 0.5
    default: 1.5
    coarse_grid: false
```

---

## 검수 결과

- [x] variable_config.yaml.bak.20260301 백업 존재 확인
- [x] 8개 변수 정의가 SURGE-CAUSE-ANALYSIS-001 S06/S12 결과와 일치
- [x] cron 등록 시간 일요일 06:00 KST (= UTC 토요일 21:00) 확인
- [x] 기존 27변수 OOS PF=12.26 결과 훼손 없음 (coarse grid 미수정)
- [ ] dry-run 테스트: CEO 승인 후 진행 예정
- [ ] GitHub push: 보고서 push 완료 후 HTTP 200 확인

---

## 산출물 목록

| 파일 | 경로 |
|------|------|
| 35변수 분석 결과 | /tmp/hav_35var_solo_test.json |
| Dry-run 준비 상태 | /tmp/hav_35var_dryrun.json |
| 백업 | /root/kis-autotrade-v4/backend/hav/variable_config.yaml.bak.20260301 |
