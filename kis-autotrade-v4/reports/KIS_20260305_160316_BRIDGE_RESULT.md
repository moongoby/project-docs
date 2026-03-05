---
project: kis-autotrade-v4
task_id: T-103
completed_at: 2026-03-05T16:45:00+09:00
---

# T-103 FunnelScoreEngine 구현 실행 결과 보고서

## 작업 개요
- Task ID: T-103
- 제목: FunnelScoreEngine 구현 — 4계층 깔대기 점수 + CTE 파이프라인 L3.1 통합
- 의존성: T-099(섹터매핑+재무), T-101(매크로 730행), T-102(테마551+공급망176+업종지수60)
- FunnelScore = 0.15 × L0 + 0.25 × L1 + 0.30 × L2 + 0.30 × L3

---

## A. FunnelScoreEngine 구현

### 파일 생성
경로: `/root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py`

### 구현된 메서드 (6개)

#### 1. `score_l0(date) → float`
- v4_macro_daily에서 해당일(또는 최근일) 데이터 조회
- macro_regime: BULL=1.0, NEUTRAL=0.5, BEAR=0.2 × weight 0.5
- VIX: <15→1.0, 15~25→선형 보간, >25→0.2 × weight 0.3
- KOSPI > MA60 → +0.2, KOSPI > MA120 → +0.2 × weight 0.5
- 데이터 없을 시 기본값 0.5 반환

#### 2. `score_l1(symbol, date) → float`
- v4_sector_mapping에서 업종 코드 조회
- v4_sector_index_daily에서 업종 RS 계산 (전체 업종 중 백분위)
- v4_theme_mapping에서 is_leader 여부 확인 → +0.3 보너스
- SEC_LEADER_FLAG v2: RS > 80 → +0.3 추가
- 섹터 매핑 없을 시 기본값 0.3 반환

#### 3. `score_l2(symbol, date) → float`
- v4_investor_daily에서 최근 20일 수급 데이터 조회
- DUAL_FLOW: 외인+기관 동시 순매수 일수 비율 × 0.4
- 외인 연속매수일 보너스 (consecutive_foreign_buy_days × 0.1, 최대 0.3) × 0.3
- ohlcv_daily에서 CLOSE_POSITION_5D 계산, >0.7 → +0.3
- 데이터 없을 시 기본값 0.3 반환

#### 4. `score_l3(symbol) → float`
- GrowthScoreEngine.score_growth(symbol) 호출 (T-098)
- v4_fundamental_quarterly에서 SMALL_CAP_QUALITY 판정 (영업이익 양수 분기 비율)
- PEG inverse 점수 (PEG < 1.0 → 저평가)
- 영업이익 YoY 추세 점수

#### 5. `calculate_funnel_score(symbol, date) → dict`
```
반환:
{
    'symbol': symbol,
    'date': date,
    'l0_score': float,
    'l1_score': float,
    'l2_score': float,
    'l3_score': float,
    'funnel_score': 0.15*l0 + 0.25*l1 + 0.30*l2 + 0.30*l3,
    'detail': {'l0': {...}, 'l1': {...}, 'l2': {...}, 'l3': {...}}
}
```

#### 6. `score_batch(symbols, date) → List[dict]`
- 여러 종목 일괄 계산
- funnel_score 내림차순 정렬 반환
- 개별 오류 시 0.0으로 처리 (전체 차단 방지)

---

## B. 설정 파일 생성

파일: `/root/kis-autotrade-v4/config/funnel_score.yaml`

```yaml
funnel_score:
  weights:
    l0_macro: 0.15
    l1_sector: 0.25
    l2_supply: 0.30
    l3_fundamental: 0.30
  thresholds:
    min_score_for_entry: 0.40
    premium_score: 0.70
  l0:
    vix_low: 15
    vix_high: 25
    regime_scores:
      BULL: 1.0
      NEUTRAL: 0.5
      BEAR: 0.2
  l1:
    rs_threshold: 80
    leader_bonus: 0.3
  l2:
    dual_flow_days: 20
    close_pos_threshold: 0.7
    consecutive_buy_bonus: 0.1
  l3:
    small_cap_max_mcap: 70000000000
    growth_weight: 0.5
    quality_weight: 0.5
```

---

## C. CTE 파이프라인 L3.1 통합

파일: `/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py`

### 추가된 필드 (TradeSignal 데이터클래스)
```python
# ── L3.1 FunnelScore (사전 계산 결과, None이면 스킵) ──
funnel_score_result: Optional[Dict] = field(default=None)
```

### 추가된 필드 (PipelineResult 데이터클래스)
```python
# ── L3.1 FunnelScore ──────────────────────────
funnel_score: float = 0.0          # L3.1 FunnelScore 값 (0.0~1.0)
funnel_score_label: str = "SKIP"   # L3.1 판정 ('PASS'/'BLOCK'/'SKIP')
```

### 파이프라인 삽입 위치 (L3 → L3.1 → L3.3 순서)
```
[기존] L3: 종목 한도
[신규] L3.1: FunnelScore 필터 (T-103)
       - funnel_score_result != None 일 때만 평가
       - funnel_score < 0.40 → blocking_layer="L3.1_FUNNEL", 즉시 차단
       - funnel_score >= 0.40 → PASS, 계속 진행
[기존] L3.3: 수급 게이트 (E-3)
[기존] L3.2: VWAP 지지 체크
[기존] L3.5: CS 게이트
```

### 삽입된 코드
```python
# ── L3.1: FunnelScore 필터 (T-103) ──────
if signal.funnel_score_result is not None:
    fs = signal.funnel_score_result
    fs_val = float(fs.get("funnel_score", 0.0))
    result.funnel_score = fs_val
    result.details["funnel"] = {
        "funnel_score": fs_val,
        "l0_score": fs.get("l0_score"),
        "l1_score": fs.get("l1_score"),
        "l2_score": fs.get("l2_score"),
        "l3_score": fs.get("l3_score"),
    }
    _min_funnel = 0.40
    if fs_val < _min_funnel:
        result.funnel_score_label = "BLOCK"
        result.blocking_layer = "L3.1_FUNNEL"
        result.blocking_reason = (
            f"FunnelScore 미달: {fs_val:.3f} < {_min_funnel} (min_score_for_entry)"
        )
        return result
    result.funnel_score_label = "PASS"
```

---

## D. 단위 테스트 실행 결과

파일: `/root/kis-autotrade-v4/tests/unit/test_funnel_score_engine.py`

### 테스트 실행 명령
```bash
source venv/bin/activate
python3 -m pytest tests/unit/test_funnel_score_engine.py -v --tb=short
```

### 실행 결과 (원문)
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.0.2, pluggy-1.6.0 -- /root/kis-autotrade-v4/venv/bin/python3
cachedir: .pytest_cache
rootdir: /root/kis-autotrade-v4
configfile: pytest.ini
plugins: anyio-4.12.1, respx-0.22.0, asyncio-1.3.0
asyncio: mode=Mode.AUTO, debug=False, asyncio_default_fixture_loop_scope=function, asyncio_default_test_loop_scope=function
collecting ... collected 10 items

tests/unit/test_funnel_score_engine.py::TestScoreL0::test_score_l0_bull_regime PASSED [ 10%]
tests/unit/test_funnel_score_engine.py::TestScoreL0::test_score_l0_bear_regime PASSED [ 20%]
tests/unit/test_funnel_score_engine.py::TestScoreL0::test_score_l0_missing_macro_data PASSED [ 30%]
tests/unit/test_funnel_score_engine.py::TestScoreL1::test_score_l1_sector_leader PASSED [ 40%]
tests/unit/test_funnel_score_engine.py::TestScoreL1::test_score_l1_no_sector_mapping PASSED [ 50%]
tests/unit/test_funnel_score_engine.py::TestScoreL2::test_score_l2_dual_flow_high PASSED [ 60%]
tests/unit/test_funnel_score_engine.py::TestScoreL2::test_score_l2_no_investor_data PASSED [ 70%]
tests/unit/test_funnel_score_engine.py::TestScoreL3::test_score_l3_growth_stock PASSED [ 80%]
tests/unit/test_funnel_score_engine.py::TestCalculateFunnelScore::test_calculate_funnel_score_integration PASSED [ 90%]
tests/unit/test_funnel_score_engine.py::TestCalculateFunnelScore::test_score_batch_sorting PASSED [100%]

============================== 10 passed in 0.13s ==============================
```

**결과: 10/10 ALL PASS ✓**

---

## E. Walk-Forward 검증

지시서에 따라 시간 초과 시 SKIP 처리.
별도 검증은 T-108에서 진행 예정.

---

## F. DB 스키마 확인 결과

### 사용 테이블
| 테이블 | 용도 | 행 수 |
|--------|------|-------|
| v4_macro_daily | L0 매크로 데이터 | 730행 |
| v4_sector_mapping | L1 업종 매핑 | 3844행 |
| v4_sector_index_daily | L1 업종 RS 계산 | - |
| v4_investor_daily | L2 수급 데이터 | 2,576,431행 |
| v4_theme_mapping | L1 테마 리더 여부 | - |
| ohlcv_daily | L2 CLOSE_POSITION_5D | - |
| v4_fundamental_quarterly | L3 재무 데이터 | - |

---

## 완료 기준 체크리스트

- [x] FunnelScoreEngine 6메서드 구현 (score_l0, score_l1, score_l2, score_l3, calculate_funnel_score, score_batch)
- [x] funnel_score.yaml 생성
- [x] cte_pipeline.py L3.1 삽입 (TradeSignal + PipelineResult 필드 + evaluate() 블록)
- [x] 10/10 테스트 통과
- [ ] HANDOVER v10.0 push (root 권한 필요 — done_watcher.sh 자동 처리)
- [ ] 보고서 project-docs push (done_watcher.sh 자동 처리)

---

## 생성/수정된 파일 목록

### 신규 생성
1. `/root/kis-autotrade-v4/backend/app/services/funnel_score_engine.py` — FunnelScoreEngine 본체
2. `/root/kis-autotrade-v4/config/funnel_score.yaml` — 설정 파라미터
3. `/root/kis-autotrade-v4/tests/unit/test_funnel_score_engine.py` — 단위 테스트 10개

### 수정
4. `/root/kis-autotrade-v4/backend/app/services/trading/cte/cte_pipeline.py` — L3.1 통합

---

## 비고
- GrowthScoreEngine import 시 Decimal 버그(T-099)는 기존 score_growth()에서 `float()` 변환 처리하여 안전
- FunnelScoreEngine은 score_growth() 호출 시 try/except로 래핑, 오류 시 0.0으로 fallback
- L3.1은 funnel_score_result=None이면 스킵 (하위 호환 보장)
- 서비스 재시작 없음 (지시서 지시에 따름)
