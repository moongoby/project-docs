---
project: KIS-V41
task_id: T-188
completed_at: 2026-03-06T20:30:00+09:00
---

# T-188 실행 결과: FunnelScore 0.4 하드코딩 잔존 제거

## 1. 현황 확인 — grep 전수 조사

### 실행 명령
```
grep -rn "0\.4" /root/kis-autotrade-v4/backend/ --include="*.py" | grep -iE "funnel|score|threshold|min_score|entry" | grep -v ".bak" | grep -v "__pycache__"
```

### 실행 결과 (전체 원문)
```
/root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py:34:        "min_score_for_entry": 0.35,  # T-163: 0.40→0.35 (원래값: 0.40; config/funnel_score.yaml 동기화)
/root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py:660:        # 최종 점수: growth × 0.4 + quality × 0.3 + peg × 0.15 + op_trend × 0.15 + scq_bonus + bj_bonus + kjh_bonus + v3_ai_bonus
/root/kis-autotrade-v4/backend/app/services/go100/ai/ai_scorer.py:439:        cs_ai     = int(np.clip(round(0.6 * norm_mfe60 + 0.4 * norm_mfe3d), 0, 100))
/root/kis-autotrade-v4/backend/app/services/go100/ai/ai_scorer.py:465:              "gap_d1_raw": 1.23, "up_5d_prob": 0.48,
/root/kis-autotrade-v4/backend/app/services/go100/ai/feature_engine.py:311:        theme_cycle_score = round(score_100b * 0.6 + score_ul * 0.4, 4)
/root/kis-autotrade-v4/backend/app/services/go100/agents/news_agent.py:287:                    "sentiment_score": 0.45,
/root/kis-autotrade-v4/backend/app/services/desk2_conditions/c_s1_volume_pullback.py:511:            "entry_signal": triggered and confidence >= 0.40,
/root/kis-autotrade-v4/backend/app/services/desk2_conditions/c3_open_strength.py:109:                vol_score = min(actual_vol_ratio / (volume_ratio_min * 2.0), 1.0) * 0.4
/root/kis-autotrade-v4/backend/app/services/trading/cte/execution_quality_score.py:306:        elif bid_ratio >= 0.40:
/root/kis-autotrade-v4/backend/app/services/trading/cte/test_vwap_atr.py:8:  TestATREntryBlock   (3): NetR:R <2.0 진입차단, 비용 반영(0.015%), 전략별 SL_MAX 차등  # T-163: 0.47→0.015
/root/kis-autotrade-v4/backend/app/services/strategy/desk2_commander.py:478:                score += 0.4
/root/kis-autotrade-v4/backend/app/services/strategy/desk4_commander.py:191:                    entry_score += 0.4
/root/kis-autotrade-v4/backend/app/services/scoring/volume_scorer.py:72:        return max(0.0, 0.3 + (ratio / self.threshold_ratio) * 0.4)
/root/kis-autotrade-v4/backend/app/services/desk_filters/desk3.py:135:            ma_score * self.p("l1_weight_ma", 0.40) +
/root/kis-autotrade-v4/backend/app/services/desk_filters/desk3.py:161:                vol_score = 0.4
/root/kis-autotrade-v4/backend/app/services/desk_filters/desk5.py:74:            bottom_score += 0.4
/root/kis-autotrade-v4/backend/app/services/desk_filters/desk5.py:107:                ma_conv_score = 0.4
/root/kis-autotrade-v4/backend/app/services/desk_filters/desk5.py:114:        cond_conv_flag = ma_conv_score >= 0.4
/root/kis-autotrade-v4/backend/app/services/desk3_node_reentry.py:150:            score += 0.40
/root/kis-autotrade-v4/backend/app/services/feature_engine.py:11:  SCORE = min(1.0, (THEME_CYCLE_100B_COUNT * 0.6 + THEME_CYCLE_UL_COUNT * 0.4) / 10)
/root/kis-autotrade-v4/backend/app/services/feature_engine.py:43:_SCORE_WEIGHT_UL = 0.4
/root/kis-autotrade-v4/backend/app/services/feature_engine.py:353:    SCORE = convergence×0.4 + min(surge_count/3, 1)×0.3 + gap×0.3
/root/kis-autotrade-v4/backend/app/services/feature_engine.py:548:        SCORE = convergence×0.4 + min(surge_count/3, 1)×0.3 + gap×0.3
/root/kis-autotrade-v4/backend/app/services/feature_engine.py:614:    leader_score = (rs > 80) * 0.4 + (rank == 1) * 0.3 + (first_breakout) * 0.3
/root/kis-autotrade-v4/backend/app/services/feature_engine.py:624:        self._w_rs: float = float(score_weights.get("rs", 0.4))
/root/kis-autotrade-v4/backend/app/services/feature_engine.py:2946:      score = supply * 0.4 + low_rise * 0.3 + volume * 0.3
/root/kis-autotrade-v4/backend/tests/test_desk_filters.py:272:            new_score=0.35, old_score=0.40,
/root/kis-autotrade-v4/backend/tests/test_desk_filters.py:279:            new_score=0.35, old_score=0.40,
/root/kis-autotrade-v4/backend/tests/test_go100_optimizer.py:192:        c["score"] = c["sharpe_ratio"] * 0.4 + c["profit_factor"] * 0.3 + c["total_return"] / 100 * 0.3
/root/kis-autotrade-v4/backend/tests/test_hypothesis_scorer.py:103:        "win_rate": 0.40,
```

### 분석
- `funnel_score_engine.py:34`: `"min_score_for_entry": 0.35` — T-163에서 0.40→0.35로 이미 수정됨. 코멘트 명시.
- `funnel_score_engine.py:660`: 점수 공식 가중치 (FunnelScore 엔트리 임계값 무관)
- 나머지 0.4 모두: 서브스코어 가중치, 내부 조건값 (FunnelScore min_score_for_entry 아님)
- **FunnelScore 엔트리 임계값 0.4 하드코딩: 0건**

---

## 2. VIRTUAL 경로별 확인

### 실행 명령
```
grep -rn "VIRTUAL_KIS_MOCK\|VIRTUAL_NXT_AM\|VIRTUAL_NXT_PM\|VIRTUAL_NXT_NIGHT" /root/kis-autotrade-v4/backend/ --include="*.py" -A3 | grep -i "0\.\|score\|threshold"
```

### 결과
```
(출력 없음)
```

→ VIRTUAL_KIS_MOCK/VIRTUAL_NXT_AM/VIRTUAL_NXT_PM 리터럴 상수 없음.
→ V4.1은 cte_pipeline.py 단일 파이프라인 경로 사용. 3개 가상계좌 모두 동일 경로 통과.

---

## 3. config/funnel_score.yaml 확인

### 실행 명령
```
grep -A2 "min_score_for_entry\|entry_threshold" /root/kis-autotrade-v4/config/funnel_score.yaml
```

### 결과
```
    min_score_for_entry: 0.35  # T-163: 0.55→0.35 (원래값: 0.55)
    premium_score: 0.70
```

→ `min_score_for_entry: 0.35`. 0.4 아님. ✅

---

## 4. cte_pipeline.py T-178 이후 config 참조 확인

### grep 결과
```
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:490:            # min_score_for_entry: funnel_score.yaml에서 동적 로드 (T-178: 하드코딩 제거)
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:492:                _get_funnel_engine()._cfg.get("thresholds", {}).get("min_score_for_entry", 0.35)
/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py:498:                    f"FunnelScore 미달: {fs_val:.3f} < {_min_funnel} (min_score_for_entry)"
```

### 해당 코드 (490-500줄)
```python
            # min_score_for_entry: funnel_score.yaml에서 동적 로드 (T-178: 하드코딩 제거)
            _min_funnel = float(
                _get_funnel_engine()._cfg.get("thresholds", {}).get("min_score_for_entry", 0.35)
            )
            if fs_val < _min_funnel:
                result.funnel_score_label = "BLOCK"
                result.blocking_layer = "L3.1_FUNNEL"
                result.blocking_reason = (
                    f"FunnelScore 미달: {fs_val:.3f} < {_min_funnel} (min_score_for_entry)"
                )
                return result
            result.funnel_score_label = "PASS"
```

→ config 동적 참조. 기본값 fallback 0.35. ✅

---

## 5. funnel_score_engine.py _DEFAULT_CONFIG 확인

```
grep -n "min_score_for_entry\|0\.40\|0\.4\b" /root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py
```

결과:
```
34:        "min_score_for_entry": 0.35,  # T-163: 0.40→0.35 (원래값: 0.40; config/funnel_score.yaml 동기화)
660:        # 최종 점수: growth × 0.4 + quality × 0.3 + peg × 0.15 + op_trend × 0.15 + scq_bonus + bj_bonus + kjh_bonus + v3_ai_bonus
```

→ _DEFAULT_CONFIG fallback: `min_score_for_entry: 0.35`. ✅

---

## 6. DB FunnelScore 분포 조회 시도

### 실행 명령
```sql
SELECT
  CASE
    WHEN funnel_score >= 0.4 THEN '>=0.4'
    WHEN funnel_score >= 0.35 THEN '0.35-0.4'
    WHEN funnel_score >= 0.30 THEN '0.30-0.35'
    WHEN funnel_score >= 0.25 THEN '0.25-0.30'
    ELSE '<0.25'
  END as range,
  count(*) as cnt
FROM v4_mock_trades WHERE created_at >= '2026-02-28'
GROUP BY 1 ORDER BY 1;
```

### 결과
```
ERROR:  column "funnel_score" does not exist
LINE 4:     WHEN funnel_score >= 0.4 THEN '>=0.4'
```

### 테이블 스키마 확인
```
sudo /usr/bin/psql -h localhost -U kis_admin -d kisautotrade -c "\d v4_mock_trades"
```
결과:
```
                                         Table "public.v4_mock_trades"
    Column    |            Type             | Collation | Nullable |                  Default
--------------+-----------------------------+-----------+----------+--------------------------------------------
 id           | integer                     |           | not null | nextval('v4_mock_trades_id_seq'::regclass)
 trade_date   | date                        |           | not null |
 ticker       | character varying(20)       |           | not null |
 strategy_id  | character varying(20)       |           | not null |
 direction    | character varying(4)        |           | not null | 'BUY'::character varying
 quantity     | integer                     |           |          |
 entry_price  | numeric                     |           |          |
 exit_price   | numeric                     |           |          |
 pnl_pct      | numeric                     |           |          |
 cost_pct     | numeric                     |           |          | 0.47
 slippage_pct | numeric                     |           |          |
 kis_order_id | character varying(50)       |           |          |
 notes        | text                        |           |          |
 created_at   | timestamp without time zone |           |          | now()
```

### funnel_score 컬럼 전체 테이블 탐색
```
SELECT table_name, column_name FROM information_schema.columns WHERE column_name = 'funnel_score' AND table_schema = 'public';
```
결과:
```
 table_name | column_name
------------+-------------
(0 rows)
```

→ DB에 funnel_score 컬럼 없음. FunnelScore는 런타임 계산값으로 저장하지 않음.
→ DB 분포 조회: 해당 없음 (선택사항 항목, 컬럼 미존재).

---

## 7. 낮은 FunnelScore(0.36) 진입 허용 여부 로직 트레이스

시나리오: `fs_val = 0.36`, `min_score_for_entry = 0.35`

```
_min_funnel = float(0.35)  # funnel_score.yaml에서 로드
if 0.36 < 0.35:  → False
    # BLOCK 미발동
result.funnel_score_label = "PASS"  # ← 실행됨
```

결론: 0.36 종목 → **진입 허용 (PASS)** ✅

---

## 8. 코드 수정 사항

없음. T-163 및 T-178에서 이미 완전 제거 완료.

---

## 9. git 커밋 결과

```
git add report/v41/CUR-V41-FUNNELSCORE-HARDCODE-FIX-001-20260306.md
git commit -m "[V4.1] fix: FunnelScore 0.4 하드코딩 잔존 제거 (T-188)"
```

결과:
```
[phase-2c-command-center b93b43f5] [V4.1] fix: FunnelScore 0.4 하드코딩 잔존 제거 (T-188)
 1 file changed, 170 insertions(+)
 create mode 100644 report/v41/CUR-V41-FUNNELSCORE-HARDCODE-FIX-001-20260306.md
```

---

## 10. project-docs push 결과

```
sudo /usr/bin/git -C /root/project-docs add kis-autotrade-v4/reports/CUR-V41-FUNNELSCORE-HARDCODE-FIX-001-20260306.md
sudo /usr/bin/git -C /root/project-docs commit -m "docs: T-188 FunnelScore 0.4 하드코딩 잔존 제거 보고서 push (20260306)"
sudo /usr/bin/git -C /root/project-docs push origin master
```

결과:
```
[master f329241] docs: T-188 FunnelScore 0.4 하드코딩 잔존 제거 보고서 push (20260306)
 1 file changed, 170 insertions(+)
 create mode 100644 kis-autotrade-v4/reports/CUR-V41-FUNNELSCORE-HARDCODE-FIX-001-20260306.md
To github.com:moongoby/project-docs.git
   0986343..f329241  master -> master
```

---

## 11. GitHub raw URL 200 확인

```
curl -s -o /dev/null -w "%{http_code}" "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-FUNNELSCORE-HARDCODE-FIX-001-20260306.md"
```

결과: **200** ✅

---

## 12. 최종 성공 기준 체크

| 항목 | 기준 | 결과 |
|------|------|------|
| grep 결과 FunnelScore 하드코딩 | 0건 | ✅ 0건 |
| 3경로 모두 config 참조 | config 참조 확인 | ✅ cte_pipeline.py config 동적 로드 |
| 커밋 메시지 | [V4.1] fix: FunnelScore 0.4 하드코딩 잔존 제거 (T-188) | ✅ b93b43f5 |

## 체크포인트

- [x] 코드 레포 커밋 완료 (kis-autotrade-v4: b93b43f5)
- [x] project-docs 보고서 push 완료 (GitHub raw URL 200 확인: f329241)
