# CUR-GO100-REGIME-SOURCE-AUDIT-001 — GO100 레짐 소스 통일 조사

- **작업일**: 2026-02-23 21:30 KST  
- **서버**: root@211.188.51.113  
- **코드 repo**: /root/kis-autotrade-v4 (branch: phase-2c-command-center)  
- **문서 repo**: /root/project-docs (branch: master)  
- **작업 유형**: 읽기 전용 조사 (SELECT only, 코드/DB 변경 없음)

---

## 1. 배경

- **GO100**: `advanced_filters.py`에서 자체 레짐 계산  
  - 명칭: STRONG_BULL / MILD_TREND_UP / SIDEWAYS / MILD_TREND_DOWN / STRONG_BEAR  
- **V4.1**: `regime_detector.py` → `v4_market_regime_daily` 테이블  
  - 명칭: STRONG_TREND_UP / MILD_TREND_UP / SIDEWAYS / MILD_TREND_DOWN / STRONG_TREND_DOWN  
- 명칭·데이터 소스 불일치. CEO 결정 필요: **통일 vs 독립**.

**참조 보고서**: [CUR-GO100-REGIME-STRATEGY-RESEARCH-001-20260223](https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-REGIME-STRATEGY-RESEARCH-001-20260223.md)

---

## 2. GO100 자체 레짐 계산 로직 요약

### 2.1 함수 위치

- **파일**: `backend/app/services/go100/universe/advanced_filters.py`  
- **함수**: `get_market_regime(self, db, ref_date=None)` (L353~437)

### 2.2 데이터 소스

| 소스 | 용도 |
|------|------|
| `index_daily` (index_code='0001', KOSPI) | 90일 구간 date/close → MA5/20/60, 20일 수익률 |
| `v4_vkospi_daily` | 최근 1건 close → 변동성 보정 |
| `v4_market_investor_daily` (market='KSP') | 최근 30일 `SUM(foreign_net_amount)` → 수급 |

- **참고**: 코드 주석에는 "v4_market_regime_daily가 2건뿐이므로 자체 계산"으로 되어 있으나, **현재 v4_market_regime_daily는 59건**(2025-11-20~2026-02-13)으로 갱신되어 있음.

### 2.3 점수 계산 (0~100)

- 기준점 50에서 가감:
  - **20일 수익률**: >5% +15, >0% +8, <-5% -15, <0% -8  
  - **MA 배열**: BULL_ALIGNED +10, BEAR_ALIGNED -10  
  - **VKOSPI**: <18 +5, >28 -10, >22 -5  
  - **외국인 30일 순매수**: >0 +5, <-5억 -5  
- 최종 `score = max(0, min(100, score))`

### 2.4 점수 → 레짐 매핑 (GO100 명칭)

| 점수 구간 | 레짐 |
|-----------|------|
| 80 이상 | STRONG_BULL |
| 60 이상 | MILD_TREND_UP |
| 40 이상 | SIDEWAYS |
| 20 이상 | MILD_TREND_DOWN |
| 그 미만 | STRONG_BEAR |

- **히스테리시스**: 없음 (당일 지표만으로 즉시 판정).

---

## 3. V4.1 regime_detector 로직 요약

### 3.1 파일 및 진입점

- **파일**: `backend/app/services/market/regime_detector.py`  
- **메인**: `detect_regime(save=True)` → PRE_MARKET에서 Orchestrator 호출, `v4_market_regime_daily`에 저장.

### 3.2 데이터 소스

| 소스 | 용도 |
|------|------|
| `index_daily` (0001 KOSPI, 1001 KOSDAQ) | 20/60일 수익률, MA 5/20/60, 양봉 비율(20일), 거래대금 추이 |
| `v4_investor_daily` | 20일 구간 `SUM(foreign_net_qty)` (주식 수) |
| `ohlcv_daily` | 최근 5일 상한가/하한가 비율 |
| `v4_vkospi_daily` | 최근 1건 (선택, 없으면 90점 만점으로 스케일) |

### 3.3 점수 계산 (0~100)

- **가중치**: KOSPI 20일 수익률 25점, MA 배열 20점, 양봉 비율 15점, 거래대금 10점, 외국인 15점, 상한/하한가 5점, VKOSPI 10점 (없으면 90점 기준으로 100 스케일).

### 3.4 점수 → 레짐 매핑 (V4.1 명칭)

| 점수 구간 | 레짐 |
|-----------|------|
| 81 이상 | STRONG_TREND_UP |
| 61 이상 | MILD_TREND_UP |
| 41 이상 | SIDEWAYS |
| 21 이상 | MILD_TREND_DOWN |
| 그 미만 | STRONG_TREND_DOWN |

### 3.5 히스테리시스 (Phase 2-C)

- 상승 전환: **3일 연속** 충족 시 전환 허용.  
- 하락 전환: **2일 연속** 충족 시 전환 허용.  
- 2단계 이상 점프 시 **1단계만** 이동.  
- STRONG_TREND_DOWN 탈출 시 **3일 연속 score 개선** 추가 확인.

---

## 4. 차이점 비교표

| 항목 | GO100 (advanced_filters) | V4.1 (regime_detector) |
|------|---------------------------|--------------------------|
| **명칭 상단** | STRONG_BULL / STRONG_BEAR | STRONG_TREND_UP / STRONG_TREND_DOWN |
| **명칭 하단** | MILD_TREND_UP/DOWN, SIDEWAYS 동일 | 동일 |
| **임계값** | 80/60/40/20 | 81/61/41/21 (1점 차이) |
| **지표 구성** | KOSPI close, MA, 20일 수익률, VKOSPI, 외국인 30일 금액 | KOSPI+KOSDAQ 수익률, MA, 양봉비율, 거래대금, 외국인 20일 수량, 상한/하한가, VKOSPI |
| **외국인 소스** | v4_market_investor_daily (금액) | v4_investor_daily (수량) |
| **히스테리시스** | 없음 | 상승 3일/하락 2일, 2단계 제한, STRONG_DOWN 탈출 조건 |
| **저장** | 없음 (매 호출 재계산) | v4_market_regime_daily UPSERT |
| **실행 시점** | GO100 유니버스/AI 툴 호출 시 | PRE_MARKET (장전) |

---

## 5. v4_market_regime_daily 현황

- **총 건수**: 59  
- **기간**: 2025-11-20 ~ 2026-02-13  
- **최근 5건 예시**:

| date       | regime       | regime_score | previous_regime |
|------------|--------------|--------------|-----------------|
| 2026-02-13 | MILD_TREND_UP | 75.00        | MILD_TREND_UP   |
| 2026-02-12 | MILD_TREND_UP | 75.00        | (null)          |
| 2026-02-11 | SIDEWAYS     | 41.00        | SIDEWAYS        |
| 2026-02-10 | SIDEWAYS     | 42.00        | SIDEWAYS        |
| 2026-02-09 | SIDEWAYS     | 42.00        | SIDEWAYS        |

- **참고**: `index_daily`(KOSPI) 최근 일부 행에서 close=0인 경우 있음(재수집 이슈). `v4_vkospi_daily`는 정상 갱신됨.

---

## 6. 통일 시 영향 분석

### 6.1 get_market_regime() 호출처

- **정의**: `advanced_filters.py` 내 `get_market_regime()`  
- **문서화**: `ai/prompts.py` — AI 툴 설명 "시장 레짐 판정" (자체계산, index_daily + vkospi + market_investor)  
- **직접 호출**: `build_universe()` 파이프라인에는 **포함되지 않음**. AI가 툴로 호출할 수 있는 수준으로만 노출.  
- **동일 클래스 사용처**: `fit_engine.py`, `backtest_service.py`, `base_orchestrator.py` — 주로 `build_universe()` / `filter_*` 사용. `get_market_regime`은 툴 목록에만 존재.

### 6.2 V4.1 레짐을 GO100에서 쓰려면 필요한 변경

- **옵션 1**: `get_market_regime()` 내부에서 자체 계산 대신 **v4_market_regime_daily**의 `ref_date`(또는 최신) 1건 조회로 대체.  
- **옵션 2**: `regime_detector.py`를 import해 동일 로직 호출 (save=False).  
- **명칭 매핑**: GO100 기대값이 STRONG_BULL/STRONG_BEAR이면  
  - STRONG_TREND_UP → STRONG_BULL, STRONG_TREND_DOWN → STRONG_BEAR 로 반환 시 매핑 필요.

### 6.3 V4.1 레짐 데이터의 GO100 시간대 사용 가능 여부

- **v4_market_regime_daily**: PRE_MARKET에서 생성되므로 **당일 장전** 이미 당일 레짐 1건 존재.  
- **GO100 스케줄러**: `go100_scheduler.py` — "장 마감 후" 하루 1회 `run_all_live` / `run_all_paper` 실행. 즉, GO100 일괄 실행 시점에는 **당일 V4.1 레짐이 이미 적재된 상태**.  
- **결론**: GO100이 "전일" 또는 "당일" 기준으로 레짐을 쓸 경우, V4.1 테이블 조회만으로도 시간대 문제 없음.

---

## 7. 통일 방안 A/B 비교표

| 항목 | A: V4.1 테이블 통일 | B: 독립 유지 |
|------|---------------------|--------------|
| **코드 변경** | advanced_filters.py에서 get_market_regime을 v4_market_regime_daily 조회(+ 명칭 매핑)로 변경 | 변경 없음 |
| **데이터 정합성** | V4.1·GO100 동일 레짐 사용 | GO100과 V4.1 레짐 불일치 가능 |
| **장점** | 일관된 분석/보고, 단일 소스, 히스테리시스 반영 | GO100 자율성, V4.1 의존성 없음 |
| **단점** | V4.1 의존성 증가, PRE_MARKET 미실행 시 전일 레짐만 사용 | 크로스 분석·대시보드와 불일치 |
| **명칭 통일** | 필수 (STRONG_BULL/STRONG_BEAR ↔ STRONG_TREND_UP/DOWN 매핑) | 불필요 |

---

## 8. CEO 결정 권고

- **통일(A) 권고** 조건:  
  - 단일 "시장 레짐" 정의로 리스크/어댑티브/대시보드/GO100을 맞추고 싶을 때.  
  - v4_market_regime_daily가 이미 59건 이상 유지·갱신되고, GO100 실행 시점에 당일 레짐 사용 가능.  
- **독립(B) 유지** 조건:  
  - GO100만의 레짐 정의(지표/임계값)를 실험·유지하려 할 때.  
  - 단, 크로스 분석·리포트에서는 "GO100 레짐"과 "V4.1 레짐"을 구분해 기재 필요.

---

## 9. 결론 및 유의사항

- 본 조사는 **읽기 전용**으로 수행됨.  
- **DB/코드 변경 없음.**  
- **kis-v41-*** 서비스 재시작 없음.  
- **strategy_cards DDL** 없음.  
- **.env / .bak** 커밋 없음.

---

## GitHub URL

- 보고서: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-REGIME-SOURCE-AUDIT-001-20260223.md
