# CUR-V41-DD-RISK-IMPL-001-20260301
## DD Decelerator + 5-Layer 리스크 구현 보고서 (Phase A-2, Cursor #15)

**작성일**: 2026-03-01
**작성자**: Claude Sonnet 4.6 (Cursor #15)
**설계 근거**: CUR-V41-DD-VWAP-GATE-DESIGN-001 + CUR-V41-EXIT-RULE-FINALIZE-001

---

## 1. 구현 파일 목록

| 파일 | 경로 | 설명 |
|------|------|------|
| `dd_decelerator.py` | `backend/app/services/trading/cte/` | DDDecelerator — S1 파라미터 하드코딩 |
| `risk_layer_manager.py` | `backend/app/services/trading/cte/` | FiveLayerRiskManager — 5개 Layer 독립 판정 |
| `disaster_detector.py` | `backend/app/services/trading/cte/` | DisasterPatternDetector — 3패턴 탐지 |

> **원칙 준수**: 기존 `v4_risk_manager.py` 수정 없이 별도 모듈로 구현.

---

## 2. 클래스/메서드 시그니처

### 2-A. DDDecelerator (`dd_decelerator.py`)

```python
# S1 파라미터 (하드코딩)
DD_LEVELS = {
    0: {"name": "Normal",  "dd_min": -3%,   "multiplier": 1.00},
    1: {"name": "Caution", "dd_min": -5%,   "multiplier": 0.70},
    2: {"name": "Warning", "dd_min": -8%,   "multiplier": 0.50},
    3: {"name": "Danger",  "dd_min": -10%,  "multiplier": 0.25},
    4: {"name": "Halt",    "dd_min": -∞,    "multiplier": 0.00},
}

@dataclass
class DDState:
    level: int; level_name: str; multiplier: float
    rolling_dd_pct: float; consecutive_profit_days: int
    daily_pnl_pct: float; peak_value: float; current_value: float

class DDDecelerator:
    def update(daily_pnl_pct: float, portfolio_value=None) -> DDState
        # 일일 PnL → Rolling 20일 DD 계산 → 레벨 전환 판정
        # 복구: L4→L3(3일), L3→L2(2일), L2→L1(1일), L1→L0(DD≥-3%)

    def get_multiplier() -> float   # 현재 포지션 사이즈 배수
    def get_state() -> DDState      # 현재 상태 스냅샷
    def reset(value: float)         # 상태 초기화
```

### 2-B. FiveLayerRiskManager (`risk_layer_manager.py`)

```python
class FiveLayerRiskManager:
    # Layer 1 (거래)
    def check_trade_sl(atr14, price) -> float
        # SL = clip(ATR14×1.5/price, 0.3%, 2.0%)

    # Layer 2 (전략)
    def check_strategy_cooldown(strategy_id, loss_count,
                                 daily_pnl_pct, now) -> CooldownResult
        # 2연속→30분, 3연속→60분, 일일-1.5% 중단

    # Layer 3 (종목)
    def check_stock_limit(symbol, entry_count_today,
                           daily_pnl_pct, last_entry_time, now) -> bool
        # 4회/일, -1.0%/일, 10분 재진입

    # Layer 4 (포트폴리오)
    def check_portfolio_kill(daily_total_pnl_pct, dd_multiplier) -> bool
        # -2.0% 킬스위치, DD multiplier

    # Layer 5 (시장)
    def check_market_halt(kosdaq_change_pct) -> MarketMode
        # >-1.5%:NORMAL(1.0x) | -2%~-1.5%:CAUTION(0.7x) |
        # -3%~-2%:HALT(0x) | ≤-3%:CRISIS(0x)

    def get_final_multiplier(**kwargs) -> float   # 5개 Layer 최솟값
    def get_layer_status(**kwargs) -> LayerCheckResult  # 상세 결과
    def reset_daily()                              # 일일 초기화
```

### 2-C. DisasterPatternDetector (`disaster_detector.py`)

```python
@dataclass
class DisasterScore:
    score: int          # 0~3
    risk_level: str     # SAFE/CAUTION/DANGER/CRITICAL
    flags: List[str]; relay_detected: bool
    concentration_pct: float; excess_positions: bool

class DisasterPatternDetector:
    RELAY_THRESHOLD = 5           # 연속 릴레이 임계값
    CONCENTRATION_THRESHOLD = 0.70
    EXCESS_POSITIONS_THRESHOLD = 8

    def detect_relay(trades_today, strategy_id) -> bool
    def detect_relay_any(trades_today) -> Tuple[bool, str, int]
    def detect_concentration(trades_today, strategy_id) -> float
    def get_concentration_all(trades_today) -> Dict[str, float]
    def detect_excess_positions(open_positions) -> bool
    def evaluate_day(trades_today, open_positions,
                      focus_strategy_id="") -> DisasterScore
```

---

## 3. 단위 테스트 결과 (29케이스)

### 3-A. DDDecelerator (`/tmp/dd_decelerator_unit_test.json`)

| 케이스 | 결과 | 상태 |
|--------|------|------|
| 수익일 → L0 유지 (multiplier=1.0) | level=0 | ✅ |
| 4% 손실 누적 → L1 진입 (0.7x) | level≥1 | ✅ |
| 9% 손실 누적 → L2~L3 진입 | level≥2 | ✅ |
| 12% 손실 누적 → L4 Halt (0.0x) | level=4, mult=0.0 | ✅ |
| L4 + 연속3일수익 → L3 복구 | level≤3 | ✅ |
| L1 + DD 회복 → L0 복구 | level=0 | ✅ |

### 3-B. FiveLayerRiskManager (`/tmp/risk_layer_unit_test.json`)

| Layer | 케이스 | 결과 | 상태 |
|-------|--------|------|------|
| L1 ATR손절 0.3%~2.0% | 3케이스 | clip 정상 | ✅ |
| L2 2연속→30분, 3연속→60분 | 3케이스 | 정확 | ✅ |
| L2 일일-1.5% 중단 | 1케이스 | is_halted=True | ✅ |
| L3 4회 초과 차단 | 2케이스 | 정상 | ✅ |
| L4 킬스위치 -2.0% | 2케이스 | 정상 | ✅ |
| L5 NORMAL/CAUTION/HALT/CRISIS | 4케이스 | 정확 | ✅ |
| 통합 최종배수 | 1케이스 | 0<final≤1 | ✅ |

### 3-C. DisasterPatternDetector (`/tmp/disaster_detector_unit_test.json`)

| 케이스 | 결과 | 상태 |
|--------|------|------|
| 릴레이 6연속 탐지 | True | ✅ |
| 분산 매매 미탐지 | False | ✅ |
| 집중도 70% 탐지 | 0.70+ | ✅ |
| 과잉 9포지션 탐지 | True | ✅ |
| 정상 5포지션 | False | ✅ |
| 종합 CRITICAL (score≥2) | score=2+ | ✅ |
| 안전 케이스 (score=0) | SAFE | ✅ |

**총계**: **29케이스 전체 통과** ✅

---

## 4. 221거래일 통합 스모크 테스트 결과 (15-D)

**결과 파일**: `/tmp/risk_integration_smoke_221day.json`

### DB 실데이터 분석 (session_id=19, 221일)

| 지표 | 값 |
|------|-----|
| 일평균 PnL | +1.72%/day |
| Max DD (S0=S1) | -0.55% |
| DD Decelerator 발동 | 거의 없음 |

> **원인**: session19는 지나치게 낙관적 세션 (avg +1.72%/day). DD 임계값(-3%) 미달성.

### 합성 시뮬레이션 (클러스터 손실 4구간 포함)

| 시나리오 | Max DD | PF | 수익률 |
|---------|--------|-----|--------|
| S0 (DD 미적용) | -15.99% | 1.069 | +6.34% |
| S1 (DD 적용) | -7.16% | 1.254 | +15.72% |
| **기대 S1 (#3 보고서)** | **-11.42%** | **2.16** | **122.95%** |

| 목표 | 실제 | 달성 |
|------|------|------|
| Max DD 70%+ 감축 vs S0 | 55.2% 감축 | ⚠️ 미달 |
| PF 15%+ 개선 vs S0 | +17.3% | ✅ |

### 괴리 원인 분석

| 괴리 항목 | 수치 | 원인 |
|----------|------|------|
| Max DD 괴리 | 37.3% | 합성 데이터 손실 클러스터 강도/빈도 차이 |
| PF 괴리 | 41.9% | #3 보고서가 실제 PnL 분포 기반, 합성은 통계적 추정 |
| S0 Max DD | -15.99% vs 예상 -25~30% | 합성 파라미터 보수적 설정 |

**결론**: DD Decelerator 메커니즘은 정상 동작 (L4→0x, L3→0.25x 등). DB 실데이터가 지나치게 낙관적이어서 DD 발동이 거의 없음. 실거래 환경에서 손실 클러스터 발생 시 DD 감축 효과 발현 예상.

---

## 5. 설계 파라미터 준수 확인

| 파라미터 | 설계값 | 구현값 | 일치 |
|---------|--------|--------|------|
| L0 Normal multiplier | 1.00 | 1.00 | ✅ |
| L1 Caution (-3%~-5%) | 0.70x | 0.70 | ✅ |
| L2 Warning (-5%~-8%) | 0.50x | 0.50 | ✅ |
| L3 Danger (-8%~-10%) | 0.25x | 0.25 | ✅ |
| L4 Halt (<-10%) | 0.00x | 0.00 | ✅ |
| L4→L3 복구 | 연속3일 | 3일 | ✅ |
| L1→L0 복구 | DD≥-3% | -0.03 | ✅ |
| Rolling 창 | 20일 | deque(maxlen=20) | ✅ |
| L2 2연속 쿨다운 | 30분 | 30분 | ✅ |
| L2 3연속 쿨다운 | 60분 | 60분 | ✅ |
| L2 일일 중단 | -1.5% | -0.015 | ✅ |
| L3 진입 한도 | 4회/일 | 4 | ✅ |
| L3 재진입 간격 | 10분 | 10분 | ✅ |
| L4 킬스위치 | -2.0% | -0.020 | ✅ |
| L5 주의 | KOSDAQ≤-1.5% | -0.015 | ✅ |
| L5 정지 | KOSDAQ≤-2.0% | -0.020 | ✅ |
| L5 위기 | KOSDAQ≤-3.0% | -0.030 | ✅ |

---

## Storage Info
- Server: `/root/project-docs/kis-autotrade-v4/reports/CUR-V41-DD-RISK-IMPL-001-20260301.md`
- GitHub: `https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-DD-RISK-IMPL-001-20260301.md`
- Commit: (push 후 업데이트)
- HTTP Verified: (push 후 확인)
- HANDOVER Updated: yes
