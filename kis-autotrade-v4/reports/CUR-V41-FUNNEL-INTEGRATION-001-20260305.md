# T-099 — 깔대기 데이터 실 수집 + FunnelScore 통합 백테스트 보고서

**작성일**: 2026-03-05
**Task ID**: T-099
**우선순위**: P0-CRITICAL
**의존성**: T-098 (완료)

---

[인계 확인]
직전 완료: T-098 (펀더멘탈 Growth Score 엔진)
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001, D-002, D-003, D-008
strategy_cards: 60
open_positions: 14

---

## 1. 작업 목표
T-098에서 구현된 `v4_fundamental_quarterly` 테이블과 `GrowthScoreEngine`을 실제 데이터로 채우고 검증한다.
깔대기 4레이어 중 Layer 0(매크로), Layer 1(섹터), Layer 2(펀더멘탈) DB 구축.

---

## 2. 작업 2: DB 마이그레이션 062

**파일**: `backend/migrations/062_v4_sector_macro_tables.sql`

```sql
CREATE TABLE IF NOT EXISTS v4_sector_mapping (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(100),
    market VARCHAR(10),
    krx_sector_code VARCHAR(10),
    krx_sector_name VARCHAR(50),
    theme_tags TEXT[],
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sector_symbol ON v4_sector_mapping(symbol);
CREATE INDEX IF NOT EXISTS idx_sector_krx ON v4_sector_mapping(krx_sector_code);

CREATE TABLE IF NOT EXISTS v4_macro_daily (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    us_fed_rate NUMERIC(6,4),
    us_10y_yield NUMERIC(6,4),
    us_vix NUMERIC(8,2),
    kr_base_rate NUMERIC(6,4),
    kr_usd_krw NUMERIC(10,2),
    kr_kospi NUMERIC(10,2),
    kr_kosdaq NUMERIC(10,2),
    macro_regime VARCHAR(20),
    collected_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_macro_date ON v4_macro_daily(date);
```

**실행 결과**:
- `v4_sector_mapping` 테이블 생성 완료 ✅
- `v4_macro_daily` 테이블 생성 완료 ✅
- 총 DB 객체수: 254 + 2 = 256

---

## 3. 작업 3: 업종 분류 수집기 (sector_collector.py)

**파일**: `backend/app/services/collectors/sector_collector.py`

**구현 방식**: KIS API 대신 `stock_universe` 테이블 (3,844행) 데이터 활용
- `collect_from_stock_universe()`: stock_universe → v4_sector_mapping UPSERT
- `collect_from_ohlcv_symbols()`: ohlcv_daily에만 있는 종목 추가
- `collect_all()`: 두 메서드 통합 실행

**수집 결과**:
```
v4_sector_mapping 총 행수: 3,844 (목표 ≥ 2,000 → ✅ 초과 달성)
```

---

## 4. 작업 1: 재무 데이터 실 수집

**시도한 방법**:
1. KIS API FHKST66430100 (가상계좌 토큰) → 토큰 만료
2. KIS API 토큰 재발급 후 실서버 호출 → output2: [] (가상 계정 권한 제한)
3. `stock_fundamentals` 테이블 (33,831행) 활용 → **채택**

**데이터 소스**: `stock_fundamentals` 테이블
- 날짜: 20210630 ~ 20260224 (반기/연간 스냅샷)
- 컬럼: per, eps, pbr, roe (revenue, operating_profit은 NULL)

**수집 결과**:
```
v4_fundamental_quarterly 종목수: 149 (목표 ≥ 100 → ✅)
v4_fundamental_quarterly 행수: 787
revenue_growth_yoy 있는 행 (EPS YoY proxy): 387
data_source: STOCK_FUNDAMENTALS
```

**DESK3 pool 기준 샘플**:
| symbol | fiscal_year | fiscal_quarter | per | eps | pbr |
|--------|------------|----------------|-----|-----|-----|
| 000720 | 2024 | Q4 | 5.33 | 4767 | 0.35 |
| 011200 | 2026 | Q1 | 4.16 | 5055 | 0.67 |
| 013520 | 2026 | Q1 | 5.08 | 533 | 0.57 |

---

## 5. GrowthScoreEngine 버그 수정

**발견된 버그**: `growth_score_engine.py:199` - DB에서 반환되는 `Decimal` 타입과 `float` 연산 시 `TypeError`

**수정 내용**:
```python
# 수정 전 (라인 154-155)
revenue_yoy = latest.get("revenue_growth_yoy")
op_yoy = latest.get("op_growth_yoy")

# 수정 후
revenue_yoy = float(latest["revenue_growth_yoy"]) if latest.get("revenue_growth_yoy") is not None else None
op_yoy = float(latest["op_growth_yoy"]) if latest.get("op_growth_yoy") is not None else None
```

또한 `eps_growth` Decimal 캐스팅 추가 (라인 197-198).

---

## 6. 작업 4: GrowthScore 기반 DESK 풀 필터링 시뮬레이션

### DESK3 축 분류 (166 활성 종목)

```
AXIS1 (기대가치): 0종목 (0.0%)
AXIS2 (실현가치): 4종목 (2.4%)
NONE:            162종목 (97.6%)
```

**AXIS2 종목 상세**:
| symbol | axis | growth_score | revenue_yoy | PEG |
|--------|------|-------------|------------|-----|
| 181710 | AXIS2_REALIZATION | 0.717 | +191.0% | 0.055 |
| 092220 | AXIS2_REALIZATION | 0.689 | +75.0%  | 0.239 |
| 002360 | AXIS2_REALIZATION | 0.681 | +183.3% | 0.296 |
| 006650 | AXIS2_REALIZATION | 0.380 | +17.8%  | 0.354 |

### DESK5 NONE 종목 식별

- DESK5 활성 종목: 0개 (ACTIVE 상태 없음)
- v4_desk5_watchlist 전체 조회(20종목): ALL NONE (PEG/EPS 데이터 부족)

### 해석

NONE 비율 97.6%는 예상 범위:
1. **KIS API revenue/operating_profit 데이터 미수집** (가상계좌 권한 제한)
2. 현재 data_source = STOCK_FUNDAMENTALS (EPS/PER 기반 proxy)
3. 실 서버 재무 API 활성화 시 AXIS2 비율 크게 상승 예상

---

## 7. 작업 5: 단위테스트 4건

**파일**: `tests/test_funnel_integration.py`

```
테스트 1: v4_sector_mapping 테이블 존재 + ≥ 2000행  → PASS ✅
테스트 2: v4_macro_daily 테이블 존재               → PASS ✅
테스트 3: v4_fundamental_quarterly ≥ 100종목       → PASS ✅
테스트 4: GrowthScoreEngine.classify_stock axis 반환 → PASS ✅

4 passed in 0.24s — ALL PASS
```

---

## 8. 완료 기준 체크

| 기준 | 결과 | 상태 |
|------|------|------|
| v4_fundamental_quarterly ≥ 100종목 | 149종목, 787행 | ✅ |
| v4_sector_mapping ≥ 2,000종목 | 3,844종목 | ✅ |
| v4_macro_daily 테이블 생성 | 생성 완료 | ✅ |
| DESK5 NONE 종목 리스트 식별 | 20종목 ALL NONE | ✅ |
| DESK3 축별 분류 분포 보고 | AXIS2=4, NONE=162 | ✅ |
| 4건 단위테스트 ALL PASS | 4/4 PASS | ✅ |
| HANDOVER.md v9.8 push | 완료 | ✅ |

---

## 9. 생성된 파일 목록

| 파일 | 유형 | 설명 |
|------|------|------|
| `backend/migrations/062_v4_sector_macro_tables.sql` | 신규 | v4_sector_mapping + v4_macro_daily |
| `backend/app/services/collectors/sector_collector.py` | 신규 | 업종 분류 수집기 |
| `tests/test_funnel_integration.py` | 신규 | 깔대기 통합 단위테스트 4건 |
| `backend/app/services/growth_score_engine.py` | 수정 | Decimal TypeError 버그 수정 |

---

## 10. 후속 작업 권장 (T-100)

1. **실 서버 KIS API 재무 수집**: 프로덕션 계정(74032243) 토큰 갱신 후 FHKST66430100/66430200 호출
2. **v4_macro_daily 매크로 데이터 수집**: FRED API 또는 Yahoo Finance 연동
3. **AXIS2 종목 우선 진입 로직**: node_detector_desk3에 AXIS2 종목 가중치 강화
4. **DESK5 활성화**: AXIS1 종목 발굴 후 v4_desk5_watchlist 재구성

HANDOVER.md 업데이트 완료: (아래 커밋 해시 참조)
