# CUR-V41-HAV-35VAR-FIRST-RUN-001-20260302
**작성일**: 2026-03-01
**작성자**: Claude Code (Cursor #21)
**상태**: PRE-CHECK COMPLETE / CRON PENDING

[인계 확인]
직전 완료: HAV-DRYRUN-DRIFT-001
현재 단계: HAV 35변수 확장 1차 cron 실행 사전검증
CEO 지시 적용: D-001, D-002, D-003, D-010, D-011
strategy_cards: 60
open_positions: 14

---

## 1. HAV 35변수 확장 개요

### 1.1 배경

| 항목 | 내용 |
|------|------|
| 출발점 | DEV-HAV-001 (2026-02-28) — 27변수, 135K 조합 HAV 개발 완료 |
| 첫 OOS PF | 12.26 (Bayesian 최적화, Walk-Forward 2/2 PASS) |
| 확장 보고서 | HAV-EXTEND-35VAR-001 (2026-03-01) — 8변수 추가 분석 완료 |
| Dry-run | HAV-DRYRUN-DRIFT-001 (2026-03-01) — 종합 판정 GO |
| 예정 실행 | 03-02(일) 06:00 KST 주간 cron (현재 cron 등록 완료) |
| 핵심 구조 | DESK2 변수 탐색 엔진, CTE 파이프라인과 완전 독립 |

### 1.2 현재 상황: 03-01(일) 27변수 run이 진행 중

> **중요**: 오늘 2026-03-01(일) 06:00 KST에 현재 variable_config.yaml(27변수 기준)로
> cron이 자동 실행되어 현재 진행 중이다. 35변수 확장(YAML 추가)은 **아직 적용되지 않았다**.
> 즉, 03-02 06:00 KST cron은 35변수가 아닌 **27변수 기준**으로 실행된다.
> 이 점이 본 보고서의 핵심 사전 확인 결과이다.

```
현재 상태 (2026-03-01 12:02 KST 기준):
  실행 중: run_weekly.py (PID 773029, CPU 99.1%, MEM 2.2%)
  진행: 95,000/135,135 조합 완료 (70.3%)
  경과: 21,671초 (6.01시간)
  예상 완료: ~14:30~15:00 KST (잔여 ~153분)
  변수 수: 27 (Loaded 27 variables, 6 coarse grid keys)
```

### 1.3 Bayesian 유효변수 3개 (HAV-DRYRUN-DRIFT-001에서 식별)

| 순위 | 변수명 | Effect Size | Solo PF 추정 | Bayesian 20회 판정 | 목표 상태 |
|------|--------|------------|-------------|-------------------|----------|
| 1 | precursor_body_size_pct | 0.855 | 2.71 | 유효 (Solo PF >= 2.0) | coarse_grid: true 전환 검토 |
| 2 | precursor_atr_pct | 0.848 | 2.70 | 유효 (Solo PF >= 2.0) | coarse_grid: true 전환 검토 |
| 3 | precursor_bb_width_pct | 0.617 | 2.23 | 유효 (Solo PF >= 2.0) | coarse_grid: true 전환 검토 |

> 현재 이 3개 변수는 variable_config.yaml에 **추가되지 않은 상태**다.
> HAV-EXTEND-35VAR-001에서 YAML 추가 명세(precursor_variables 섹션)가 작성되었으나,
> CEO 승인 대기 상태로 파일 수정이 보류되어 있다.

---

## 2. 사전 점검 결과

### 2.1 Cron 등록 상태

| 항목 | 결과 |
|------|------|
| 일요일 06:00 KST 스케줄 | **확인됨** (`0 6 * * 0`) |
| 평일 15:40 Drift Detector | **확인됨** (`40 15 * * 1-5`) |
| 스크립트 경로 (weekly) | `/root/kis-autotrade-v4/backend/hav/run_weekly.py` |
| 스크립트 경로 (drift) | `/root/kis-autotrade-v4/backend/hav/run_drift.py` |
| venv Python 경로 | `/root/kis-autotrade-v4/venv/bin/python` |
| 로그 경로 (weekly) | `/var/log/hav_weekly.log` |
| 로그 경로 (drift) | `/var/log/hav_drift.log` |
| cron 등록 위치 | `crontab -l` 섹션 `[HAV] DESK2 Hypothesis Auto-Validator` |

**cron 등록 원문**:
```cron
# ── [HAV] DESK2 Hypothesis Auto-Validator ──────────────────
# 주간 HAV 전체 탐색: 일요일 06:00
0 6 * * 0   /root/kis-autotrade-v4/venv/bin/python /root/kis-autotrade-v4/backend/hav/run_weekly.py >> /var/log/hav_weekly.log 2>&1
# 일일 Drift Detector: 평일 15:40
40 15 * * 1-5 /root/kis-autotrade-v4/venv/bin/python /root/kis-autotrade-v4/backend/hav/run_drift.py >> /var/log/hav_drift.log 2>&1
```

### 2.2 variable_config.yaml 현황

| 항목 | 값 |
|------|------|
| 파일 경로 | `/root/kis-autotrade-v4/backend/hav/variable_config.yaml` |
| 백업 경로 | `/root/kis-autotrade-v4/backend/hav/variable_config.yaml.bak.20260301` |
| 현재 파일 상태 | 백업과 동일 (변경 없음) |
| 그룹 수 | 6개 (wave_structure, entry_exit, stoploss, moving_average, capital_allocation, filters) |
| 총 변수 수 | **27개** (Python 파싱 결과: `Loaded 27 variables, 6 coarse grid keys`) |
| Coarse Grid 변수 수 | **6개** (zigzag_threshold, transition_threshold, w1_partial_exit_pct, stoploss_mode, exit_timeframe, vol_exhaust_warning) |

**현재 Coarse Grid 6변수 탐색 규모**:
```
13 × 11 × 9 × 3 × 5 × 7 = 135,135 조합
```

**precursor_variables 섹션 추가 여부**: 미추가 (CEO 승인 대기)
- 추가 예정 8변수: precursor_vol_anomaly_sigma, precursor_news_d5_count, precursor_ma_convergence_pct, precursor_surge_threshold_pct, precursor_bb_width_pct, precursor_atr_pct, precursor_body_size_pct, precursor_vol_ratio

### 2.3 03-01 진행 중인 Weekly Run 현황

| 항목 | 값 |
|------|------|
| 시작 시각 | 2026-03-01 06:00:01 KST |
| 현재 진행 | 95,000/135,135 (70.3%) |
| 처리 속도 | 약 4.38 조합/초 |
| 예상 완료 | 2026-03-01 ~14:35 KST |
| 변수 수 | 27개 (35변수 미적용) |
| 오류 건수 | 0건 (로그 확인) |

**03-01 log 확인**:
```
06:00:01 HAV Weekly Pipeline Start: 2026-03-01
06:00:02 Loaded 27 variables, 6 coarse grid keys
06:00:25 Coarse Grid Precomputing: 5991 pairs
06:00:45 Precomputed 5963 pairs
06:00:45 Coarse grid raw: 135135 combos (13 × 11 × 9 × 3 × 5 × 7)
12:01:57 Progress: 95000/135135 (21671s, ETA 152.6min)
```

### 2.4 DB 상태

| 항목 | 값 |
|------|------|
| v4_hav_hypotheses 테이블 | 존재, 2건 (HAV-20260228-00001, 00002) |
| v4_hav_validation_runs | 존재 |
| v4_hav_drift_events | 존재, 0건 (Drift 미발생) |
| v4_evolution_candidates | 미확인 (별도 테이블) |

**저장된 가설 (03-01 run 이전 기준)**:

| hypothesis_id | stage | coarse_pf | 생성일 |
|---------------|-------|-----------|--------|
| HAV-20260228-00001 | coarse | 11.6529 | 2026-02-28 |
| HAV-20260228-00002 | coarse | 11.0463 | 2026-02-28 |

### 2.5 Drift Detector 4지표 확인

HAV-DRYRUN-DRIFT-001에서 실제 코드 점검 결과:

| 지표 | 임계값 | 감시 방식 | 35변수 호환 |
|------|--------|----------|------------|
| transition_prob | 5.0pp | 최근5일 σ vs 기준20일 σ | **완전 독립** |
| ma_support | 10.0pp | 15분봉 MA5 지지율 변화 | **완전 독립** |
| relay_pf | 0.2 | 전주 대비 릴레이 PF 변화 | **완전 독립** |
| vol_exhaust | 10.0pp | 거래대금 50% 소진 시점 중앙값 | **완전 독립** |

```python
THRESHOLDS = {
    "transition_prob": 5.0,   # 표준편차 > 5pp
    "ma_support": 10.0,       # 절대값 > 10pp
    "relay_pf": 0.2,          # 전주 대비 -0.2
    "vol_exhaust": 10.0,      # 중앙값 시프트 > 10pp
}
```

**핵심 확인**: drift_detector.py는 변수 목록을 하드코딩하지 않음.
4개 시장 구조 지표만 모니터링하며, 35변수 확장과 무관하게 동작 → **코드 수정 불필요**.

### 2.6 W09 주간 보고서 (2026-02-28 E2E 테스트 결과)

| 항목 | 값 |
|------|------|
| 최고 OOS PF | 12.26 (Bayesian) |
| Walk-Forward | 2/2 PASS (Fold1: PF 19.41, Fold2: PF 14.30) |
| 현행 대비 개선폭 | PF 1.34 → 12.26 (+10.92) |
| Drift 이벤트 | 0건 |

---

## 3. 35변수 확장 계획 상세

### 3.1 variable_config.yaml 추가 명세 (CEO 승인 후 실행)

**현재 상태**: 백업 완료, YAML 수정 보류 중 (CEO 승인 대기)

추가 예정 섹션:
```yaml
precursor_variables:
  description: "DESK5 발굴 조건 변수 (S06~S12 기반)"
  precursor_body_size_pct:
    name: "캔들 몸통 크기 (%)"
    type: continuous
    range: [1.0, 5.0]
    step: 0.5
    default: 2.75
    search_center: 2.75
    research_source: "S06"
    note: "effect_size=0.855, Solo PF 2.71, t-stat 74.75"
    coarse_grid: false   # Bayesian 전용 → 첫 실행 후 true 전환 검토
  precursor_atr_pct:
    name: "ATR 비율 (%)"
    type: continuous
    range: [2.0, 8.0]
    step: 1.0
    default: 5.8
    search_center: 5.8
    research_source: "S06"
    note: "effect_size=0.848, Solo PF 2.70, t-stat 84.01"
    coarse_grid: false
  precursor_bb_width_pct:
    name: "볼린저밴드 폭 (%)"
    type: continuous
    range: [2.0, 8.0]
    step: 1.0
    default: 6.17
    search_center: 6.17
    research_source: "S06"
    note: "effect_size=0.617, Solo PF 2.23, t-stat 52.86"
    coarse_grid: false
  precursor_ma_convergence_pct:
    name: "이평선 수렴도 (%)"
    type: continuous
    range: [0.5, 3.0]
    step: 0.5
    default: 2.0
    research_source: "S10"
    note: "effect_size=0.529"
    coarse_grid: false
  precursor_vol_ratio:
    name: "거래량 비율 (당일/20일평균)"
    type: continuous
    range: [1.0, 5.0]
    step: 0.5
    default: 1.5
    research_source: "S06"
    note: "effect_size=0.285"
    coarse_grid: false
  precursor_vol_anomaly_sigma:
    name: "전조구간 거래량 이상치 (σ 단위)"
    type: continuous
    range: [1.5, 3.0]
    step: 0.5
    default: 2.0
    research_source: "S09"
    coarse_grid: false
  precursor_news_d5_count:
    name: "D-5 이내 뉴스 건수"
    type: discrete
    range: [1, 5]
    step: 1
    default: 3
    research_source: "S07"
    coarse_grid: false
  precursor_surge_threshold_pct:
    name: "급등 임계값 (%)"
    type: continuous
    range: [3.0, 10.0]
    step: 1.0
    default: 5.0
    research_source: "base"
    coarse_grid: false
```

### 3.2 활성화 근거

| 근거 | 내용 |
|------|------|
| S06 (daily_precursor_profile) | effect_size 기반 유효성 사전 검증 완료 |
| HAV-DRYRUN-DRIFT-001 | Bayesian 20회 시뮬에서 3개 유효 변수 통계적 확인 |
| Coarse Grid 영향 | 기존 6변수 coarse grid 유지 → 기존 OOS PF 12.26 보존 |
| 파싱 테스트 | 35변수 YAML 파싱 오류 0건 확인 |

---

## 4. 03-02(일) 첫 실행 계획 (35변수 미적용 시)

> **중요**: 35변수 YAML이 03-02 이전에 추가되지 않으면,
> 03-02 06:00 KST cron은 27변수 기준으로 실행된다.
> 이는 2주 연속 27변수 run으로, 35변수 확장이 1주 지연된다.

### 4.1 시나리오 A: 27변수로 03-02 실행 (현재 상태 유지)

| 단계 | 내용 |
|------|------|
| 03-01 ~14:35 KST | 현재 진행 중인 27변수 run 완료 |
| 03-01 ~14:35 이후 | 결과 확인 후 YAML 수정 (CEO 승인 조건) |
| 03-02 06:00 KST | YAML 수정 완료 시 35변수, 미완료 시 27변수 |

### 4.2 시나리오 B: 35변수로 03-02 실행 (YAML 수정 후)

| 조건 | 내용 |
|------|------|
| 선행 조건 | CEO 승인 + 03-01 현재 run 완료 후 YAML 수정 |
| 수정 타이밍 | 03-01 15:00 KST 이후 (현재 run 완료 후) |
| 03-02 06:00 | 35변수 run 시작 → 27변수 대비 ~5% 탐색 시간 추가 예상 |

### 4.3 로그 확인 위치

```bash
# 실시간 로그 확인
tail -f /var/log/hav_weekly.log

# 완료 확인
grep -E "Pipeline|PASS|FAIL|OOS PF" /var/log/hav_weekly.log | tail -20

# Drift Detector 확인
tail -30 /var/log/hav_drift.log
```

### 4.4 검증 체크리스트 (03-02 실행 후)

- [ ] 06:00 KST cron 실행 확인 (`/var/log/hav_weekly.log` 타임스탬프)
- [ ] 오류 0건 검증 (`grep -i error /var/log/hav_weekly.log | wc -l`)
- [ ] 변수 수 확인 (`grep "Loaded.*variables" /var/log/hav_weekly.log`)
- [ ] Coarse Grid 조합 수 확인
- [ ] Bayesian 단계 진입 확인
- [ ] Walk-Forward 결과 확인
- [ ] 새 hypothesis INSERT 확인 (`SELECT * FROM v4_hav_hypotheses ORDER BY created_at DESC LIMIT 3;`)
- [ ] PF 변화 측정 (기준: 현행 OOS PF 12.26)
- [ ] Drift Detector 4지표 정상 동작 확인 (평일 15:40)

### 4.5 PF 변화 측정 계획

| 항목 | 값 |
|------|------|
| 기준 PF | 12.26 (W09 Bayesian 최적화 결과) |
| 기준 Walk-Forward | 2/2 PASS (Fold1: PF 19.41, Fold2: PF 14.30) |
| 임계값 (경보) | OOS PF < 10.0 또는 W-F 실패 |
| 임계값 (유지) | OOS PF >= 12.0 → 정상 범위 |
| 측정 명령어 | `SELECT hypothesis_id, fine_pf, wf_results FROM v4_hav_hypotheses ORDER BY created_at DESC LIMIT 3;` |

---

## 5. 위험 요소 및 대응

### 5.1 주요 위험

| 위험 | 수준 | 대응 |
|------|------|------|
| 03-02 전 YAML 수정 미완료 | 낮음 | 27변수로 실행 → 정상 동작, 35변수는 03-09로 연기 |
| YAML 형식 오류 | 낮음 | 백업 존재(`variable_config.yaml.bak.20260301`), 복구 가능 |
| 03-01 run이 03-02 전 미완료 | 낮음 | ETA ~14:35 KST, 충분한 여유 |
| Drift Detector 오작동 | 낮음 | 코드 점검 완료, 수정 불필요 확인 |
| DB 저장 실패 | 낮음 | 로그에서 INSERT 확인 가능 |

### 5.2 03-01 현재 Run 완료 후 즉시 확인 사항

```bash
# 1) 완료 확인
grep -E "Pipeline Complete|완료" /var/log/hav_weekly.log

# 2) OOS PF 확인
grep "OOS PF\|fine_pf\|best_pf" /var/log/hav_weekly.log | tail -5

# 3) DB hypothesis 확인
sudo -u postgres psql -d kisautotrade -c \
  "SELECT hypothesis_id, stage, coarse_pf, fine_pf, verdict, created_at \
   FROM v4_hav_hypotheses \
   ORDER BY created_at DESC LIMIT 5;"

# 4) W10 주간 보고서 확인
ls /root/project-docs/kis-autotrade-v4/reports/weekly/2026-W10-HAV.md 2>/dev/null
```

---

## 6. 35변수 확장 타임라인

```
2026-02-28 (수)  DEV-HAV-001: 27변수 HAV 개발, E2E PASS, OOS PF=12.26
2026-03-01 (일)  HAV-EXTEND-35VAR-001: 8변수 분석, 백업 완료, CEO 승인 대기
2026-03-01 (일)  HAV-DRYRUN-DRIFT-001: 35변수 dry-run PASS, Bayesian 3유효변수
2026-03-01 (일)  06:00 KST — 27변수 weekly run 자동 시작 (현재 진행 중)
2026-03-01 (일)  ~14:35 KST — 27변수 run 완료 예상
2026-03-01 (일)  ~15:00 KST — CEO 승인 시 YAML 수정 가능
2026-03-02 (일)  06:00 KST — 35변수 or 27변수 weekly run (승인 여부에 따라)
2026-03-02 (월)  15:40 KST — Drift Detector 첫 실행 (평일)
2026-03-09 (일)  06:00 KST — 2회차 weekly run (35변수 확정 적용 예정)
```

---

## 7. 참조 문서

| 문서 | 경로 | 핵심 내용 |
|------|------|---------|
| DEV-HAV-001 | `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-DEV-HAV-001-20260228.md` | HAV 4-Layer 개발, 27변수, E2E PASS |
| HAV-EXTEND-35VAR-001 | `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-HAV-EXTEND-35VAR-001-20260301.md` | 8변수 분석, YAML 추가 명세 |
| HAV-DRYRUN-DRIFT-001 | `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-HAV-DRYRUN-DRIFT-001-20260301.md` | dry-run PASS, 3유효변수, GO 판정 |
| HANDOVER.md | `/root/project-docs/kis-autotrade-v4/HANDOVER.md` | 프로젝트 전체 인계 |
| W09-HAV | `/root/project-docs/kis-autotrade-v4/reports/weekly/2026-W09-HAV.md` | 첫 주간 보고서 |

---

## 8. 사전검증 종합 판정

| 항목 | 결과 |
|------|------|
| Cron 등록 (`0 6 * * 0`) | **확인됨** |
| 스크립트 파일 존재 | **확인됨** (run_weekly.py, run_drift.py) |
| variable_config.yaml | **27변수 (백업과 동일)** |
| 백업 존재 | **확인됨** (variable_config.yaml.bak.20260301) |
| 35변수 YAML 추가 | **미완료 (CEO 승인 대기)** |
| Drift Detector 코드 | **수정 불필요 (35변수 자동 호환)** |
| DB 테이블 | **3개 존재 (hypotheses, validation_runs, drift_events)** |
| 03-01 run 진행 상황 | **정상 진행 (오류 0건, 70.3% 완료)** |
| 03-02 06:00 실행 가능 여부 | **가능 (단, 27변수 기준으로 실행될 가능성 높음)** |

**종합 판정**: 인프라 정상. 35변수 YAML 추가는 CEO 승인 후 03-01 현재 run 완료 시점에 진행.

---

*다음 업데이트: 2026-03-01 ~15:00 KST (현재 run 완료 후 결과 반영) 또는 2026-03-02 (cron 첫 실행 후)*
