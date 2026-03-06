---
project: kis-autotrade-v4
task_id: T-163C
completed_at: 2026-03-06T10:50:00+09:00
---

# T-163C FunnelScore threshold 0.35 통일 — 실행 결과

## 1. 현재 임계값 확인

### grep 실행 결과
```
grep -rn "min_score\|0\.40\|0\.55\|funnel.*threshold\|FUNNEL.*THRESH" /root/kis-autotrade-v4/config/ /root/kis-autotrade-v4/backend/ 2>/dev/null | head -20
```

결과:
```
/root/kis-autotrade-v4/config/param_search_space.yaml.bak.T137:154:  l1_weight_ma: 0.40                  # 이평선 가중치
/root/kis-autotrade-v4/config/param_search_space.yaml.bak.T137:348:    M1_seed_survival_rate: 0.40       # 씨앗생존율 목표 ≥ 40%
/root/kis-autotrade-v4/config/param_search_space.yaml.bak.T137:358:      bq1_decline_ratio: 0.40         # 최적: M1=42.78% 달성 ✓
/root/kis-autotrade-v4/config/param_search_space.yaml.bak.T137:378:    max_sector_ratio: 0.40            # 단일 섹터 최대 40%
... (이하 모두 .bak 파일 내 무관한 0.40 값들)
```

### 핵심 파일 상태 확인

#### config/funnel_score.yaml
```yaml
funnel_score:
  weights:
    l0_macro: 0.15
    l1_sector: 0.25
    l2_supply: 0.30
    l3_fundamental: 0.30
  thresholds:
    min_score_for_entry: 0.35  # T-163: 0.55→0.35 (원래값: 0.55)
    premium_score: 0.70
```
→ **이미 0.35** (이전 T-163에서 적용 완료)

#### backend/app/services/funnel_score_engine.py (line 34)
```python
    "thresholds": {
        "min_score_for_entry": 0.35,  # T-163: 0.40→0.35 (원래값: 0.40; config/funnel_score.yaml 동기화)
        "premium_score": 0.70,
    },
```
→ **이미 0.35** (이전 T-163에서 적용 완료)

#### backend/app/services/trading/cte/cte_pipeline.py (line 489-490) ← 문제 발견
```python
            # min_score_for_entry: funnel_score.yaml 기본 0.40   ← 구버전
            _min_funnel = 0.40   ← 하드코딩 0.40, 미동기화 상태
```

## 2. 변경 내용

### cte_pipeline.py 수정 (라인 489-490)

**변경 전:**
```python
            # min_score_for_entry: funnel_score.yaml 기본 0.40
            _min_funnel = 0.40
```

**변경 후:**
```python
            # min_score_for_entry: funnel_score.yaml 기준 0.35 (T-163C 통일)
            _min_funnel = 0.35
```

## 3. 변경 확인

```
grep -rn "min_score_for_entry\|_min_funnel" /root/kis-autotrade-v4/backend/ 2>/dev/null | grep -v ".pyc" | grep -v ".bak"
```

결과:
```
/root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py:34:        "min_score_for_entry": 0.35,  # T-163: 0.40→0.35 (원래값: 0.40; config/funnel_score.yaml 동기화)
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:489:            # min_score_for_entry: funnel_score.yaml 기준 0.35 (T-163C 통일)
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:490:            _min_funnel = 0.35
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:491:            if fs_val < _min_funnel:
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:495:                    f"FunnelScore 미달: {fs_val:.3f} < {_min_funnel} (min_score_for_entry)"
```

→ **모든 활성 파일 0.35 통일 완료**

## 4. git commit

```
git add backend/app/services/trading/cte/cte_pipeline.py
git commit -m "[V4.1] T-163C FunnelScore threshold 0.35"
```

결과:
```
[phase-2c-command-center 92a0ac62] [V4.1] T-163C FunnelScore threshold 0.35
 1 file changed, 2 insertions(+), 2 deletions(-))
```

## 5. 최종 상태 요약

| 파일 | 이전 값 | 현재 값 | 상태 |
|------|---------|---------|------|
| config/funnel_score.yaml | 0.35 | 0.35 | 이미 적용됨 (T-163) |
| backend/app/services/funnel_score_engine.py | 0.35 | 0.35 | 이미 적용됨 (T-163) |
| backend/app/services/trading/cte/cte_pipeline.py | 0.40 | **0.35** | T-163C 수정 완료 |

## 6. 금지 사항 준수

- ✅ 서비스 재시작 미수행 (지시서 금지 조항 준수)
- ✅ FunnelScore 가중치 변경 없음 (임계값만 수정)

## 7. 체크포인트

- [x] 코드 레포 커밋 완료: `92a0ac62` [V4.1] T-163C FunnelScore threshold 0.35
- [ ] project-docs 보고서 push (root 권한 필요 — done_watcher.sh 자동 처리 예정)
