# T-110 SMALL_CAP_QUALITY 필터 구현 결과

[인계 확인]
직전 완료: T-109 (THEME_CYCLE 피처)
현재 단계: Phase 2C Command Center
CEO 지시 적용: D-008-KR §2-2

---

## 개요

- **Task ID**: T-110
- **제목**: SMALL_CAP_QUALITY 필터 구현 — 소형주 품질 필터 (시총 ≤700억, 3년 흑자, 자본건전성)
- **날짜**: 2026-03-05
- **브랜치**: phase-2c-command-center
- **커밋**: 38034c2c

---

## 구현 내용

### A. SmallCapQualityFilter 클래스 (`universe_builder.py`)

파일: `backend/app/services/discovery/universe_builder.py`

`SmallCapQualityFilter` 클래스 신규 추가:

```python
def evaluate_small_cap_quality(self, symbol: str) -> dict:
    """
    통과 조건 (5대):
      1. 시총 ≤ 700억
      2. 3년 연속 영업이익 흑자 (v4_fundamental_quarterly)
      3. 자본잠식 없음 (자본총계 > 0)
      4. 대주주 지분 < 30% OR > 70% OR 경영 10년+
      5. 최근 분기 매출 YoY > 0
    배제 조건 (6대):
      1. 3년 이상 연속 적자
      2. 자본잠식률 50%+
      3. 관리종목/투자경고
      4. 최근 1년 유상증자 2회+
      5. 대주주 지분 감소 추세
      6. 감사의견 비적정
    Returns: {'passed': bool, 'score': float 0~1, 'flags': list, 'disqualify': list}
    """
```

**설계 결정사항**:
- 조건4 (대주주 지분): 현재 DB에 지분 데이터 없음 → Optimistic default (통과 간주)
- 배제3~6 (관리종목/유상증자/지분감소/감사의견): DB 데이터 없어 현재 skip
- 자본잠식률 50%+ 프록시: ROE < -50% 로 판단
- DB 연결: `stock_universe.market_cap` + `v4_fundamental_quarterly`

### B. YAML 파라미터 (`param_search_space.yaml`)

```yaml
small_cap_quality:
  max_market_cap: 70000000000         # 700억 (원)
  min_consecutive_profit_years: 3     # 연속 영업이익 흑자 최소 년수
  max_capital_erosion_pct: 50         # 자본잠식률 배제 기준 (ROE < -50%)
  major_shareholder_low: 30           # 대주주 지분 하한 (30% 미만 조건)
  major_shareholder_high: 70          # 대주주 지분 상한 (70% 초과 조건)
```

### C. FunnelScore L3 연동 (`funnel_score_engine.py`)

`score_l3()` 메서드에 SMALL_CAP_QUALITY 연동 추가:
- `_get_scq_filter()` 지연 임포트 메서드 추가
- SMALL_CAP_QUALITY 통과 시 +0.2 가산 (clamp 1.0)
- 실패 또는 예외 발생 시 0.0 (서비스 영향 없음)

```python
scq_bonus = 0.0
try:
    scq_filter = self._get_scq_filter()
    scq_result = scq_filter.evaluate_small_cap_quality(symbol)
    if scq_result.get("passed"):
        scq_bonus = 0.2
except Exception as e:
    logger.warning("L3[%s]: SMALL_CAP_QUALITY 판정 실패: %s", symbol, e)
```

---

## 테스트 결과

파일: `tests/unit/test_small_cap_quality.py`

```
tests/unit/test_small_cap_quality.py::TestSmallCapPasses::test_small_cap_passes PASSED
tests/unit/test_small_cap_quality.py::TestLargeCapFails::test_large_cap_fails PASSED
tests/unit/test_small_cap_quality.py::TestConsecutiveLossDisqualified::test_consecutive_loss_disqualified PASSED
tests/unit/test_small_cap_quality.py::TestCapitalErosionDisqualified::test_capital_erosion_disqualified PASSED
tests/unit/test_small_cap_quality.py::TestPartialPassScore::test_partial_pass_score PASSED
tests/unit/test_small_cap_quality.py::TestNoFinancialData::test_no_financial_data PASSED
tests/unit/test_small_cap_quality.py::TestYamlParamsLoaded::test_yaml_params_loaded PASSED

7 passed in 0.27s
```

**결과: 7/7 ALL PASS** ✅

---

## 완료 기준 체크

- [x] evaluate_small_cap_quality 구현 (SmallCapQualityFilter 클래스)
- [x] YAML 파라미터 (small_cap_quality 섹션)
- [x] FunnelScore L3 연동 (+0.2 가산)
- [x] 7/7 테스트 통과
- [x] 코드 커밋 (38034c2c) — push 권한 제한으로 로컬 커밋 (root에서 push 필요)
- [ ] 보고서 push HTTP 200 (project-docs push 후 확인)
- [ ] HANDOVER 갱신

---

## 저장 정보
- 서버 경로: /root/project-docs/kis-autotrade-v4/reports/CUR-V41-SMALL-CAP-QUALITY-001-20260305.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-SMALL-CAP-QUALITY-001-20260305.md
- 코드 커밋: 38034c2c
- 브랜치: phase-2c-command-center
- 테스트: 7/7 ALL PASS
- push: claudebot SSH 권한 없음 → done_watcher.sh 통해 처리 또는 root에서 수동 push

HANDOVER.md 업데이트 완료: (project-docs push 후 확인)
