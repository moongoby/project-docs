# DESK2-BT-TIMEFRAME-AUDIT-001 분봉·시간 흐름 검증 보고서

**일자**: 2026-02-26 | **우선순위**: P0 | **선행**: DESK2-BT-SIMLOOP-VERIFY-001

---

## 확인 1 — 분봉 단위 확인

### 쿼리 (v4_ohlcv_minute: trade_date, trade_time 사용)

```sql
-- 004060 2026-02-20 분봉 30건
SELECT trade_date, trade_time, open_price, high_price, low_price, close_price, volume
FROM v4_ohlcv_minute
WHERE stock_code = '004060' AND trade_date = '2026-02-20'
ORDER BY trade_date, trade_time
LIMIT 30;

-- 분봉 간격(interval) 확인
SELECT (trade_date + trade_time) AS dt,
       (trade_date + trade_time) - LAG(trade_date + trade_time) OVER (ORDER BY trade_date, trade_time) AS interval
FROM v4_ohlcv_minute
WHERE stock_code = '004060' AND trade_date = '2026-02-20'
ORDER BY trade_date, trade_time
LIMIT 30;
```

### 실행 결과 (scripts/backtest/timeframe_audit_001_queries.py)

- 09:00 → 09:01 → … → 09:29 순차 1분 간격 확인.
- **interval**: `0:01:00` (60초) 일관.

**판정**: **1분봉**. (3분/혼재 아님.)

---

## 확인 2 — 백테스터가 사용한 봉 단위

### 코드 위치

- `backend/app/services/trading/desk2/tests/desk2_backtester.py`
- `_load_minute_bars()`: `v4_ohlcv_minute`에서 `trade_date`, `trade_time`, `open_price` 등 SELECT 후 `datetime.combine(trade_date, trade_time)`으로 Bar 생성.
- **리샘플링 없음**: 3T/5T/1min/3min 변환 코드 없음.
- Bar 생성 시 `interval="5m"` **하드코딩** (L268): 실제 데이터는 1분 간격이지만 메타만 5m.

**판정**: **1분봉 원본** 사용. (리샘플링 없음. Bar.interval 라벨만 5m.)

---

## 확인 3 — 004060 진입 전후 시간 흐름 검증

### 12:55~13:05 분봉 (DB)

| trade_time | O   | H   | L   | C   | V      |
|------------|-----|-----|-----|-----|--------|
| 12:55:00   | 568 | 577 | 566 | 576 | 1409206 |
| 12:56:00   | 576 | 579 | 574 | 579 | 735773  |
| 12:57:00   | 579 | 583 | 575 | 580 | 991728  |
| **12:58:00** | **579** | **591** | **577** | **587** | 3985336 |
| 12:59:00   | 587 | 591 | 585 | 591 | 3537255 |
| 13:00~13:05 | … | … | … | … | … |

- **12:58 봉 OHLC**: O=579, H=591, L=577, C=587. (open=587·low=448 아님.)
- 12:57→12:58→12:59 **1분 간격** 확인.

### 진입가·청산가 해석

- **진입가 587**: 12:58 봉의 **종가(C)** 또는 시그널의 entry_price(돌파가)와 일치.
- **청산가 448**: 12:55~13:05 구간 **분봉에는 없음**. BRAVO_ORB는 `stop_loss = range_low`(박스 하단). 당일 09:20 봉 L=448 → 일중 최저 448. 캐시의 `ind.low_price`(일중 최저)가 448이고, 진입 직후 `ind.low_price <= pos.stop_loss(448)` 조건으로 **같은 봉(12:58)에서** 손절 처리되어 exit_price=448로 기록됨.
- **결론**: 12:58 봉 자체의 low(577)가 아닌 **일중 최저(448)** 기준으로 손절 판단하고 있어, “진입 봉 이후” 구간만 보는 로직으로 수정 필요(추가 이슈로 정리 권장).

---

## 확인 4 — 시뮬레이션 루프의 시간 진행 로그

### 코드

- `all_times = sorted(time_to_bars.keys())` (L668)
- 루프: `for bar_dt in all_times:` (L675), `bar_dt`가 봉 시각.
- 로그 추가: `all_times first=… last=… count=…` (L671~675 부근).

### 실행 결과 (2026-02-20 1회 실행)

```
all_times first=2026-02-20 09:00:00+09:00 last=2026-02-20 15:30:00+09:00 count=381
```

**판정**: 09:00 → … → 15:30 **순차 진행**, 381개 봉. (건너뛰는 봉 없음.)

---

## 확인 5 — 전체 시간 흐름 요약

| 항목 | 결과 |
|------|------|
| DB 분봉 간격 | **1분** |
| 백테스터 사용 단위 | **1분봉 원본** (리샘플링 없음, Bar.interval="5m" 하드코딩만) |
| all_times 첫 봉 시각 | 2026-02-20 09:00:00+09:00 |
| all_times 마지막 봉 시각 | 2026-02-20 15:30:00+09:00 |
| all_times 총 봉 수 | **381** |
| 004060 발굴 시각 (C4) | **11:34** |
| 004060 watchlist 등록 시각 | **11:34** (발굴 bar_dt) |
| 004060 stalk 첫 호출 시각 | **11:35** (다음 봉) |
| 004060 진입 시각 | **12:58** |
| 004060 진입가 | **587** |
| 004060 12:58 봉 OHLC | O=**579** H=**591** L=**577** C=**587** |
| 004060 손절가 (전략 설정) | **448** (BRAVO_ORB: stop_loss=range_low, 당일 09:00~09:15 구간 저가) |
| 004060 청산 시각 | **12:58** |
| 004060 청산가 | **448** |
| 진입~청산 경과 봉 수 | **0** (같은 봉에서 진입 후 즉시 손절; hold_sec=0) |

---

## 결론 및 권장 사항

1. **분봉 단위**: DB·백테스터 모두 **1분봉** 기준으로 일관됨.
2. **시간 진행**: all_times 09:00~15:30, 381봉 순차 처리 확인.
3. **004060 동작**: 12:58 진입(587) → 같은 봉에서 `ind.low_price`(일중 최저 448) ≤ `stop_loss`(448)로 청산(448). 12:58 봉의 low(577)와 무관하게 **진입 전 일중 최저**로 손절 판단하는 구조로 보임.
4. **권장**: 손절 판단 시 **진입 시점 이후** low만 사용하도록 수정 검토(진입 봉/이후 봉의 low 또는 “진입 이후 최저가” 기준).

---

## 문서 레포 푸시 및 경로

- 본 보고서 경로: **`report/v41/DESK2-BT-TIMEFRAME-AUDIT-001-20260226.md`** (메인 레포 `kis-autotrade-v4` 내).
- 별도 문서 레포(예: project-docs)에 푸시 정책이 있으면 해당 레포로 복사·푸시 후 최종 문서 URL/경로를 운영 측에서 보고할 것.

---

## 부록 — 실행/쿼리

- DB 쿼리 실행: `scripts/backtest/timeframe_audit_001_queries.py`
- all_times 로그: `desk2_backtester.py` 내 `all_times first=… last=… count=…` (INFO)
