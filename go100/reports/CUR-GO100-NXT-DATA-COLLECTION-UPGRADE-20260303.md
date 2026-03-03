# CUR-GO100-NXT-DATA-COLLECTION-UPGRADE-20260303 — NXT 데이터 수집 고도화 보고서

**작성일시**: 2026-03-03 20:00 KST
**작업자**: Claude Code
**우선순위**: P1
**상태**: 완료

---

## 1. 작업 요약

대표님 지시: NXT 운영시간 기준 실시간 데이터 수집 + 전종목 확대 + 과거 데이터 수집 조사

| 항목 | 이전 | 이후 |
|------|------|------|
| NXT 수집 시간 (오후) | 18:00~02:00 (다음날) | **15:40~20:00** |
| NXT 수집 시간 (오전) | 미수집 | **08:00~08:50** (신규) |
| 수집 종목 수 | 30종목 (ws_stock_list.json) | **643종목** (stock_universe.is_nxt=true) |
| WS 배치 | 단일 연결 | **5배치 × 130종목** (최대 5 WS 연결) |
| 1분봉 수집 | 정규장만 | **NXT 운영시간 포함** |

---

## 2. NXT 운영시간 확인

```
NXT 오전 시간외 단일가: 08:00 ~ 08:50  (H0STCNT0/H0STASP0)
NXT 오후 시간외 + 야간: 15:40 ~ 20:00  (N0STCNT0/N0STASP0)
```

- 오전(NXT_AM): 정규장 개장 전 시간외 단일가 — 기존 KRX WebSocket TR_ID 사용
- 오후(NXT_PM): 15:40~18:00 장후 + 18:00~20:00 NXT 야간장 — N0STCNT0 사용

---

## 3. 코드 수정 내역

### 3-1. `kis_ws_collector.py` 수정

**추가된 세션 타입:**

```python
MARKET_SESSIONS = {
    "KRX":    {"start": "08:55", "end": "15:35"},
    "NXT_AM": {"start": "08:00", "end": "08:50"},   # ← 신규
    "NXT_PM": {"start": "15:40", "end": "20:00"},   # ← 신규
    "NXT":    {"start": "18:00", "end_next_day": "02:00"},  # legacy
}

TR_IDS = {
    "NXT_AM": {"tick": "H0STCNT0", "orderbook": "H0STASP0"},  # KRX TR (시간외 오전)
    "NXT_PM": {"tick": "N0STCNT0", "orderbook": "N0STASP0"},  # NXT TR (야간장)
    ...
}
```

**전종목 멀티배치 지원 (`run_collector` 개선):**

```python
# NXT 세션: stock_universe.is_nxt=true 전종목 쿼리
# 130종목 단위 배치 분할 → asyncio.gather() 병렬 실행
batches = [stocks[i:i+130] for i in range(0, len(stocks), 130)]
await asyncio.gather(*[run_batch(i, b) for i, b in enumerate(batches)])
```

### 3-2. 서비스 파일 수정

| 서비스 | 세션 | 종목 | 배치크기 |
|--------|------|------|----------|
| `go100-ws-nxt.service` (기존) | NXT → **NXT_PM** | 40 → **700 (DB 조회)** | 40 → **130** |
| `go100-ws-nxt-am.service` (신규) | **NXT_AM** | **700 (DB 조회)** | **130** |

---

## 4. 크론 등록

| 시간 | 명령 | 설명 |
|------|------|------|
| `0 8 * * 1-5` | start go100-ws-nxt-am | NXT 오전 세션 시작 |
| `50 8 * * 1-5` | stop go100-ws-nxt-am | NXT 오전 세션 종료 |
| `40 15 * * 1-5` | start go100-ws-nxt | NXT 오후 세션 시작 |
| `0 20 * * 1-5` | stop go100-ws-nxt | NXT 오후 세션 종료 |
| `30 3 * * 6 ` | collect_nxt_stocks.py | 주간 NXT 종목 갱신 |

---

## 5. NXT 과거 데이터 조사 결과

### 5-1. 과거 일봉 (OHLCV daily) — **미지원**

| API | TR_ID | 결과 |
|-----|-------|------|
| `inquire-overtime-daily-price` | FHKST11010100 | **HTTP 404** (미지원) |
| `inquire-daily-itemchartprice` (N 마켓) | FHKST03010100 | `OPSQ2001 INVALID FID_COND_MRKT_DIV_CODE` |

**결론**: KIS REST API에서 NXT 과거 일봉 조회 불가. 오늘부터 WS 실시간 수집만 가능.

### 5-2. 과거 분봉 — **오늘 데이터만 조회 가능**

| API | TR_ID | 결과 |
|-----|-------|------|
| `inquire-time-itemchartprice` | FHKST03010200 | ✅ 정상 (당일 NXT 분봉 조회 가능) |

- 19:50 기준 테스트: 30개 1분봉 정상 반환 (NXT 야간장 시간 포함)
- **단, 전일 이전 분봉은 조회 불가** — 실시간 WS 수집분만 축적 가능

### 5-3. 대안 — 일봉 집계

WS로 수집되는 분봉(v4_ohlcv_minute)을 일 단위로 집계하여 NXT 일봉 생성:
```sql
SELECT stock_code, trade_date,
  (array_agg(open_price ORDER BY trade_time))[1] AS open_price,
  max(high_price) AS high_price,
  min(low_price) AS low_price,
  (array_agg(close_price ORDER BY trade_time DESC))[1] AS close_price,
  sum(volume) AS volume
FROM v4_ohlcv_minute
WHERE trade_date = 'YYYYMMDD'
GROUP BY stock_code, trade_date;
```

---

## 6. 현재 수집 현황

| 항목 | 상태 |
|------|------|
| NXT 거래 가능 종목 | **643개** (collect_nxt_stocks.py 완료, 2026-03-03 19:25) |
| go100-ws-nxt (오후) | ✅ 운영 중 (NXT_PM, 15:40~20:00, 5배치×130종목) |
| go100-ws-nxt-am (오전) | ✅ 등록 완료 (내일 08:00 첫 실행) |
| 기존 WS 연결 (NXT 야간) | 변경됨 → NXT_PM (15:40 시작) |

---

## 7. 잔여 확인 사항 (내일)

| 항목 | 일시 | 확인 방법 |
|------|------|----------|
| NXT_AM 세션 WS 연결 | 내일 08:00 | `journalctl -u go100-ws-nxt-am -f` |
| NXT_PM 세션 WS 연결 | 내일 15:40 | `journalctl -u go100-ws-nxt -f` |
| v4_ohlcv_minute NXT 분봉 적재 | 내일 장후 | `SELECT ... FROM v4_ohlcv_minute WHERE trade_time >= '15:40:00'` |
| KIS 동시 연결 제한 확인 | 내일 | 5배치×130 = 5 WS 연결, 초과 시 배치크기 조정 |

---

## 8. 연결 구조

```
크론 15:40 → go100-ws-nxt 시작
  └── NXT_PM 세션 (N0STCNT0/N0STASP0)
        ├── Batch 0: 000070 ~ 005220 (130종목) ← WS 연결 #1
        ├── Batch 1: 005250 ~ 013000 (130종목) ← WS 연결 #2
        ├── Batch 2: 013200 ~ 025350 (130종목) ← WS 연결 #3
        ├── Batch 3: 025360 ~ 051100 (130종목) ← WS 연결 #4
        └── Batch 4: 051200 ~ 950250 (123종목) ← WS 연결 #5
              ↓ 실시간 틱 → v4_tick_data
              ↓ 1분봉 집계 → v4_ohlcv_minute
              ↓ 호가 스냅샷 → v4_orderbook_realtime

크론 20:00 → go100-ws-nxt 종료

크론 08:00 → go100-ws-nxt-am 시작
  └── NXT_AM 세션 (H0STCNT0/H0STASP0)
        └── 동일 5배치 구조 (643종목)
크론 08:50 → go100-ws-nxt-am 종료
```
