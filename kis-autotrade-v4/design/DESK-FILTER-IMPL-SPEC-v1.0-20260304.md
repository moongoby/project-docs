# DESK 필터 구현 설계서 v1.0

**문서 ID**: DESK-FILTER-IMPL-SPEC-v1.0
**작성일**: 2026-03-04
**승인자**: CEO
**상태**: 확정
**참조**: DESK-FRACTAL-ARCHITECTURE-v3.0-20260301.md, CEO-DIRECTIVES.md

---

## 섹션 1 — 목적 및 범위

본 설계서는 DESK5/4/3/2/1 파이프라인에서 사용되는 **필터 파라미터의 파라미터화 구현**을 정의한다.

### 1.1 핵심 원칙
- 모든 숫자값(임계치, 가중치, 카운트)은 `config/param_search_space.yaml`에서 로드
- 기존 로직은 그대로 유지하고 하드코딩만 YAML로 교체
- 백테스트 결과는 `v4_desk_backtest_results` 테이블에 저장
- kis-v41-* 서비스 재시작 금지

---

## 섹션 2 — DESK5 필터 설계

### 2.1 시드 스캐너 (desk5_seed_scanner)

#### 스캔 조건
| 조건 | 파라미터 | 기본값 |
|------|---------|--------|
| 바닥탈출: 52주저가 대비 | `desk5.bottom_escape_ratio` | 1.20 |
| 바닥탈출 점수 임계값 | `desk5.bottom_escape_score_threshold` | 0.60 |
| 슬로우매집 월간 증가율 범위 | `desk5.slow_acc_monthly_min/max` | 0.05~0.15 |
| 슬로우매집 부분 점수 범위 | `desk5.slow_acc_partial_min/max` | 0.03~0.05 |
| MA수렴 임계값 (tight/mid/wide) | `desk5.ma_conv_spread_tight/mid/wide` | 0.03/0.05/0.08 |
| 뉴스 30일 임계값 | `desk5.news_30d_threshold` | 3 |
| 조건 충족 최소 수 | `desk5.min_conditions_met` | 2 |
| 풀 크기 | `desk5.pool_size` | 20 |
| 거래일 조회 수 | `desk5.trading_days_lookback` | 252 |

#### 스코어 가중치
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| 바닥탈출 | `desk5.score_weight_bottom` | 0.20 |
| 슬로우매집 | `desk5.score_weight_slow_acc` | 0.15 |
| MA수렴 | `desk5.score_weight_ma_conv` | 0.15 |
| 뉴스 | `desk5.score_weight_news` | 0.25 |
| 기관외인 | `desk5.score_weight_inst` | 0.25 |
| 기관외인 정규화 기준 (원) | `desk5.inst_normalization_amt` | 1_000_000_000 |
| 뉴스 점수 정규화 분모 | `desk5.news_score_divisor` | 5.0 |

#### 트리거
| 트리거 | 조건 | 파라미터 |
|--------|------|---------|
| T5-1 | 주봉MA20돌파+거래량2배 | `desk5.t5_1_vol_multiplier: 2.0` |
| T5-2 | 120일박스상단돌파 | `desk5.t5_2_box_days: 120` |
| T5-3 | 섹터대장주동반+정배열 | (정배열 체크) |
| 최소 트리거 수 | 진입 조건 | `desk5.min_triggers_met: 2` |

#### THEME_ALIVE_FLAG
| 상태 | 뉴스 수 | 파라미터 |
|------|---------|---------|
| ALIVE | >=5 | `desk5.theme_alive_threshold: 5` |
| WARNING | 1~4 | `desk5.theme_warning_threshold: 1` |
| DEAD | 0 | - |

### 2.2 주간 모니터 (desk5_weekly_monitor)

#### 청산 조건
| 조건 | 파라미터 | 기본값 |
|------|---------|--------|
| MA20 이탈 주수 | `desk5.exit_ma20_below_weeks` | 2 |
| 세력이탈 거래량 배수 | `desk5.exit_force_vol_multiplier` | 3.0 |
| 세력이탈 주봉평균 기간 | `desk5.exit_force_avg_weeks` | 20 |
| 거래일 조회 수 | `desk5.weekly_monitor_trading_days` | 140 |

#### 익절 곡선
| 이벤트 | 파라미터 | 기본값 |
|--------|---------|--------|
| +100% 부분익절 비율 | `desk5.profit_100pct_partial_exit_pct` | 50.0 |
| +300%+MA10이탈 시 청산 비율 | `desk5.profit_300pct_exit_trigger_pct` | 100.0 |
| +500% 트레일링 임계값 | `desk5.profit_500pct_trail_threshold` | 500.0 |

---

## 섹션 3 — DESK4 필터 설계

### 3.1 노드 스캐너 (desk4_node_scanner)

#### FULL 모드 스캔 조건
| 조건 | 파라미터 | 기본값 |
|------|---------|--------|
| 거래일 조회 (full) | `desk4.full_trading_days` | 60 |
| 거래일 조회 (monitor) | `desk4.monitor_trading_days` | 40 |
| BB 하위 퍼센타일 | `desk4.bb_width_percentile` | 0.20 |
| BB 계산 기간 | `desk4.bb_period` | 20 |
| 투자자 데이터 일수 | `desk4.investor_days` | 10 |
| 뉴스 최소 건수 | `desk4.news_min_count` | 5 |
| 연속 순매수 최소 일수 | `desk4.consecutive_buy_min_days` | 10 |
| 스캔 조건 최소 충족 수 | `desk4.min_scan_conditions` | 2 |
| 최소 데이터 기간 | `desk4.min_bars_required` | 25 |

#### 계단식 상승 조건
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| 분석 기간 | `desk4.staircase_lookback_days` | 10 |
| 상승일 최소 수 | `desk4.staircase_min_up_count` | 6 |

#### 눌림목 조건
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| 눌림목 분석 기간 | `desk4.pullback_lookback_days` | 5 |
| 하락일 최소 수 | `desk4.pullback_min_down_days` | 3 |

#### 트리거
| 트리거 | 조건 | 파라미터 |
|--------|------|---------|
| T4-1 | MA20돌파+거래량2배 | `desk4.t4_1_vol_ratio: 2.0` |
| T4-4 | DESK5보유+단기모멘텀 | `desk4.t4_4_vol_ratio_5d: 1.3` |
| 최소 트리거 수 | 진입 조건 | `desk4.min_triggers_met: 2` |

#### DESK3 승격 조건
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| 거래량 배수 (D-5 평균 대비) | `desk4.desk3_promote_vol_ratio` | 3.0 |
| BB 상단 돌파 필요 | `desk4.desk3_promote_bb_upper_break` | true |

#### 스코어 가중치
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| MA 성장 | `desk4.score_weight_ma` | 0.25 |
| BB 수축 | `desk4.score_weight_box` | 0.15 |
| 계단식 | `desk4.score_weight_staircase` | 0.15 |
| 수급 | `desk4.score_weight_supply` | 0.25 |
| 촉매 | `desk4.score_weight_catalyst` | 0.20 |
| 수급 점수 정규화 분모 | `desk4.supply_score_divisor` | 20.0 |
| 촉매 점수 정규화 분모 | `desk4.catalyst_score_divisor` | 5.0 |

#### 모니터 청산 조건
| 조건 | 파라미터 | 기본값 |
|------|---------|--------|
| 손절 비율 | `desk4.stop_loss_pct` | 0.93 (-7%) |
| MA20 연속 이탈 일수 | `desk4.ma20_break_consecutive_days` | 3 |

---

## 섹션 4 — DESK3 필터 설계

### 4.1 풀 스캔 (desk3_pool_scan)

#### Layer 가중치
| Layer | 항목 | 파라미터 | 기본값 |
|-------|------|---------|--------|
| L1 | 구조 | `desk3.weight_l1` | 0.15 |
| L2 | 수급 | `desk3.weight_l2` | 0.25 |
| L3 | 시장주목 | `desk3.weight_l3` | 0.10 |
| L4 | 반복패턴 | `desk3.weight_l4` | 0.35 |
| L5 | 시퀀스 | `desk3.weight_l5` | 0.15 |

#### 풀 관리
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| 상위 N 종목 | `desk3.top_n` | 100 |
| 연속 하회 일수 (EXPIRED) | `desk3.consecutive_below_threshold` | 3 |
| 최대 체류 일수 (TIMEOUT) | `desk3.max_dwell_days` | 10 |
| 점수 하위 임계값 | `desk3.score_threshold` | 0.30 |
| 거래일 조회 수 | `desk3.trading_days_lookback` | 60 |

#### Layer 1 세부 (구조)
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| MA 점수 가중치 | `desk3.l1_weight_ma` | 0.40 |
| 박스수축 가중치 | `desk3.l1_weight_box` | 0.20 |
| 52주위치 가중치 | `desk3.l1_weight_high52` | 0.20 |
| 거래량추세 가중치 | `desk3.l1_weight_vol_trend` | 0.20 |
| 박스수축 tight 임계값 | `desk3.l1_box_ratio_tight` | 0.70 |
| 박스수축 medium 임계값 | `desk3.l1_box_ratio_medium` | 0.85 |
| 52주 위치 high | `desk3.l1_pos_52w_high` | 0.80 |
| 52주 위치 medium | `desk3.l1_pos_52w_medium` | 0.60 |
| 거래량추세 high | `desk3.l1_vol_trend_high` | 1.20 |
| 거래량추세 medium | `desk3.l1_vol_trend_medium` | 1.00 |

#### Layer 2 세부 (수급)
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| 거래량변화 가중치 | `desk3.l2_weight_vol` | 0.35 |
| DUAL_FLOW 가중치 | `desk3.l2_weight_dual` | 0.35 |
| 3주체 가중치 | `desk3.l2_weight_three` | 0.30 |
| 거래량 high 임계값 | `desk3.l2_vol_ratio_high` | 2.0 |
| 거래량 medium1 임계값 | `desk3.l2_vol_ratio_med1` | 1.5 |
| 거래량 medium2 임계값 | `desk3.l2_vol_ratio_med2` | 1.2 |
| DUAL_FLOW 정규화 분모 | `desk3.l2_dual_flow_divisor` | 3.0 |
| 3주체 정규화 분모 | `desk3.l2_three_body_divisor` | 3.0 |

#### Layer 3 세부 (시장주목)
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| 연속뉴스 가중치 | `desk3.l3_weight_consec` | 0.50 |
| 뉴스건수 가중치 | `desk3.l3_weight_news` | 0.50 |

#### Layer 4 세부 (반복패턴)
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| 뉴스 TOP-N 가중치 | `desk3.l4_weight_top_news` | 0.30 |
| 수급 TOP-N 가중치 | `desk3.l4_weight_top_supply` | 0.30 |
| 섹터동조 가중치 | `desk3.l4_weight_sector_sync` | 0.20 |
| THEME_CYCLE 가중치 | `desk3.l4_weight_theme_cycle` | 0.20 |
| 뉴스 TOP-N 크기 | `desk3.l4_top_news_n` | 20 |
| 수급 TOP-N 크기 | `desk3.l4_top_supply_n` | 20 |
| 섹터동조 임계 배수 | `desk3.l4_sector_sync_multiplier` | 1.20 |
| THEME_CYCLE 배수 | `desk3.l4_theme_cycle_multiplier` | 2.0 |
| 뉴스 30일 기간 | `desk3.l4_news_days` | 30 |

#### Layer 5 세부 (시퀀스)
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| 눌림목 가중치 | `desk3.l5_weight_pullback` | 0.30 |
| 갭지지 가중치 | `desk3.l5_weight_gap` | 0.20 |
| 신고가접근 가중치 | `desk3.l5_weight_near_high` | 0.25 |
| FORCE_ACC 가중치 | `desk3.l5_weight_force_acc` | 0.25 |
| 신고가접근 임계값 | `desk3.l5_near_high_threshold` | 0.95 |
| 눌림목 하한 | `desk3.l5_pullback_min` | -0.20 |
| 눌림목 상한 | `desk3.l5_pullback_max` | -0.05 |
| FORCE_ACC 거래량 배수 | `desk3.l5_force_acc_vol_multiplier` | 2.0 |
| 갭지지 갭상승 임계값 | `desk3.l5_gap_open_threshold` | 1.01 |
| 갭지지 지지 임계값 | `desk3.l5_gap_support_threshold` | 0.99 |

---

## 섹션 5 — DESK2 필터 설계

### 5.1 프리스코어링 (desk2_prescoring)

#### 컨디션 파라미터
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| C2 외인기관 순매수 HIGH (원) | `desk2.c2_investor_high_amt` | 5_000_000_000 |
| C2 외인기관 순매수 MEDIUM (원) | `desk2.c2_investor_medium_amt` | 1_000_000_000 |
| C3 시초가 갭상승 임계값 (%) | `desk2.c3_gap_open_threshold_pct` | 3.0 |
| C4 장중 급등 HIGH (%) | `desk2.c4_intra_surge_high_pct` | 5.0 |
| C4 장중 급등 MEDIUM (%) | `desk2.c4_intra_surge_medium_pct` | 3.0 |
| C6 전일 상한가 배수 | `desk2.c6_limit_up_ratio` | 1.29 |
| C7 신고가 임계값 | `desk2.c7_near_high_threshold` | 1.00 |
| C7 신고가 근접값 | `desk2.c7_near_high_close_threshold` | 0.97 |
| C7 fallback 5일 임계값 | `desk2.c7_fallback_period_threshold` | 0.98 |

#### 보너스 가중치
| 항목 | 파라미터 | 기본값 |
|------|---------|--------|
| C2 외인기관 | `desk2.bonus_weight_c2` | 0.25 |
| C3 시초가강세 | `desk2.bonus_weight_c3` | 0.20 |
| C4 장중급등 | `desk2.bonus_weight_c4` | 0.15 |
| C6 전일상한가 | `desk2.bonus_weight_c6` | 0.30 |
| C7 신고가 | `desk2.bonus_weight_c7` | 0.15 |

### 5.2 DESK345 신뢰도 부스트 (desk2_pool_link)

| DESK 레벨 | 파라미터 | 기본값 |
|---------|---------|--------|
| DESK3 ACTIVE → boost | `desk2.desk3_boost` | 0.5 |
| DESK4 OPEN → boost | `desk2.desk4_boost` | 0.8 |
| DESK5 OPEN → boost | `desk2.desk5_boost` | 1.0 |

---

## 섹션 6 — 파라미터 탐색 공간

백테스트를 통한 최적화 범위:

```yaml
param_search_space:
  desk5.bottom_escape_ratio:    {min: 1.10, max: 1.40, step: 0.05}
  desk5.slow_acc_monthly_min:   {min: 0.02, max: 0.08, step: 0.01}
  desk5.slow_acc_monthly_max:   {min: 0.10, max: 0.25, step: 0.05}
  desk3.weight_l4:              {min: 0.25, max: 0.50, step: 0.05}
  desk3.score_threshold:        {min: 0.20, max: 0.50, step: 0.05}
  desk4.t4_1_vol_ratio:        {min: 1.5, max: 3.0, step: 0.5}
  desk2.c2_investor_high_amt:  {min: 3e9, max: 1e10, step: 1e9}
```

---

## 섹션 7 — desk_filters 패키지 구조

```
backend/app/services/desk_filters/
├── __init__.py
├── base.py           # DeskFilterBase 추상 클래스
├── desk5.py          # DESK5 필터 (시드 + 주간 모니터)
├── desk4.py          # DESK4 필터 (노드 스캐너)
├── desk3.py          # DESK3 필터 (풀 스캔)
├── desk2.py          # DESK2 필터 (프리스코어링 + 부스트)
├── desk1.py          # DESK1 필터 (실시간 탐지 stub)
├── pipeline.py       # DeskPipeline (5→4→3→2 순서 실행)
└── backtest_runner.py # DeskBacktestRunner (파라미터 그리드 탐색)
```

---

## 섹션 8 — v4_desk_backtest_results 테이블

```sql
CREATE TABLE IF NOT EXISTS v4_desk_backtest_results (
    id SERIAL PRIMARY KEY,
    run_id UUID NOT NULL DEFAULT gen_random_uuid(),
    desk_level VARCHAR(10) NOT NULL,          -- 'DESK5', 'DESK4', 'DESK3', 'DESK2'
    param_key VARCHAR(100) NOT NULL,          -- 파라미터 이름
    param_value NUMERIC(15,6) NOT NULL,       -- 파라미터 값
    param_snapshot JSONB NOT NULL DEFAULT '{}', -- 전체 파라미터 스냅샷
    backtest_start DATE NOT NULL,
    backtest_end DATE NOT NULL,
    total_signals INT DEFAULT 0,
    triggered_signals INT DEFAULT 0,
    win_rate NUMERIC(5,2),
    profit_factor NUMERIC(8,4),
    avg_pnl_pct NUMERIC(8,4),
    max_drawdown_pct NUMERIC(8,4),
    sharpe_ratio NUMERIC(8,4),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_desk_bt_run_id ON v4_desk_backtest_results(run_id);
CREATE INDEX IF NOT EXISTS idx_desk_bt_desk_level ON v4_desk_backtest_results(desk_level);
CREATE INDEX IF NOT EXISTS idx_desk_bt_created ON v4_desk_backtest_results(created_at);
```

---

## 섹션 9 — 백테스트 실행 기준

### 9.1 PASS 기준 (v3.0 기준)
| DESK | 기준 |
|------|------|
| DESK5 | 손익비 ≥3:1, +100% 도달 ≥10% |
| DESK4 | 마디당 평균 수익 ≥8%, 월 2회 이상 |
| DESK3 | D+5 승률 ≥55%, D+5 평균 수익 ≥5% |
| DESK2 | PF ≥1.3 |

---

## 섹션 10 — 구현 제약

1. **금지**: 숫자 하드코딩 (모든 임계치/가중치/카운트 → YAML)
2. **금지**: kis-v41-* 서비스 재시작
3. **금지**: strategy_cards 변경
4. **금지**: 기존 크론 변경
5. **금지**: 기존 DB 테이블 스키마 변경 (새 테이블만 추가 허용)
6. **필수**: 기존 로직 유지 (설계서에 있고 기존에 없는 것만 신규 추가)

---

## 섹션 11 — 파라미터 로드 패턴

```python
from pathlib import Path
import yaml

_CONFIG_PATH = Path(__file__).resolve().parents[4] / "config" / "param_search_space.yaml"

def _load_params() -> dict:
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
```

---

## 섹션 12 — 완료 기준

1. `config/param_search_space.yaml` 생성 완료
2. `backend/app/services/desk_filters/` 패키지 (8파일) 생성 완료
3. desk3/4/5 스크립트 YAML 로드 전환 완료
4. `v4_desk_backtest_results` 마이그레이션 파일 생성 완료
5. 신규 테스트 작성 + 기존 테스트 ALL PASS
6. HANDOVER.md v8.6 갱신
7. 보고서 GitHub push + HTTP 200 확인

---

**저장 경로**: `/root/project-docs/kis-autotrade-v4/design/DESK-FILTER-IMPL-SPEC-v1.0-20260304.md`
