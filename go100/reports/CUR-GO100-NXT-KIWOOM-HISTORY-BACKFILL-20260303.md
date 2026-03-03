# CUR-GO100-NXT-KIWOOM-HISTORY-BACKFILL-20260303 — NXT 과거 데이터 키움 API 백필

**작성일시**: 2026-03-03 20:21 KST
**작업자**: Claude Code
**우선순위**: P1
**상태**: 완료 (백필 실행 중)

---

## 1. 작업 요약

대표님 지시: "키움 API에서 제공되는지 확인하고 보고하라" + "API문서 API폴더에서 확인하고 적용 보고하라" + "과거 데이터(일봉, 분봉) 수집하라"

| 항목 | 결과 |
|------|------|
| 키움 NXT 일봉 API | **ka10081** 지원 ✅ (`stk_cd: "005930_NX"`) |
| 키움 NXT 분봉 API | **ka10080** 지원 ✅ (`stk_cd: "005930_NX"`) |
| KIS REST API NXT 과거 데이터 | ❌ 미지원 (HTTP 404) |
| 일봉 수집 테이블 | `go100_nxt_ohlcv_daily` (신규 생성) |
| 분봉 수집 테이블 | `v4_ohlcv_minute` (NXT 시간대 15:40~20:00, 08:00~08:50) |
| 백필 스크립트 | `scripts/collect_nxt_history_kiwoom.py` (신규) |

---

## 2. 키움 API 문서 확인 결과

**파일**: `/root/kis-autotrade-v4/docs/api/키움 REST API 문서.pdf`

### 2-1. NXT 종목코드 형식 (페이지 199~203)

| 거래소 | stk_cd 형식 | 예시 |
|--------|------------|------|
| KRX | `{6자리코드}` | `039490` |
| NXT | `{6자리코드}_NX` | `039490_NX` |
| SOR | `{6자리코드}_AL` | `039490_AL` |

### 2-2. 차트 API 엔드포인트

| API ID | 내용 | 경로 |
|--------|------|------|
| `ka10080` | 주식분봉차트 | `/api/dostk/chart` |
| `ka10081` | 주식일봉차트 | `/api/dostk/chart` |
| `ka10082` | 주식주봉차트 | `/api/dostk/chart` |

### 2-3. ka10081 일봉 파라미터

```json
{
  "stk_cd": "005930_NX",
  "base_dt": "20260303",
  "updn_code": "2",
  "upd_stkpc_tp": "0"
}
```

**응답 필드** (`stk_dt_pole_chart_qry` 배열):
```json
{
  "dt": "20260303",
  "open_pric": "214000",
  "high_pric": "215000",
  "low_pric": "184600",
  "cur_prc": "186000",
  "trde_qty": "66115399",
  "trde_prica": "13166139"
}
```
- 1회 호출: 최대 229건 (약 11개월치)
- 연속조회: `cont-yn/next-key` 헤더 (현재 N 반환 → 전체 데이터 1회 제공)

### 2-4. ka10080 분봉 파라미터

```json
{
  "stk_cd": "005930_NX",
  "tic_scope": "1",
  "updn_code": "2",
  "upd_stkpc_tp": "0"
}
```

**응답 필드** (`stk_min_pole_chart_qry` 배열):
```json
{
  "cntr_tm": "20260303195900",
  "open_pric": "-185900",
  "high_pric": "-186100",
  "low_pric": "-185800",
  "cur_prc": "-186000",
  "trde_qty": "204785"
}
```
- 1회 호출: 최대 900건 (약 3~4일치 NXT 분봉)
- 연속조회: `cont-yn: Y`, `next-key: A005930_NX2026022716300000010000`
- **가격 앞 +/- 기호** 포함 → `_safe_price()` 함수로 처리

---

## 3. 구현 내역

### 3-1. 신규 스크립트: `scripts/collect_nxt_history_kiwoom.py`

```
기능:
  - ka10081: NXT 일봉 전체 수집 → go100_nxt_ohlcv_daily UPSERT
  - ka10080: NXT 1분봉 수집 (연속조회 최대 10페이지) → v4_ohlcv_minute UPSERT
  - NXT 운영시간 필터: 15:40~20:00(NXT_PM), 08:00~08:50(NXT_AM)
  - 요청 간격: 0.35초 (키움 초당 5회 제한 준수)

실행 옵션:
  --mode   daily|minute|both (기본: both)
  --stock  특정 종목 코드 (콤마 구분)
  --limit  테스트용 종목 수 제한
```

### 3-2. 신규 테이블: `go100_nxt_ohlcv_daily`

```sql
CREATE TABLE go100_nxt_ohlcv_daily (
    stock_code   VARCHAR(12) NOT NULL,
    trade_date   CHAR(8)     NOT NULL,
    open_price   BIGINT,
    high_price   BIGINT,
    low_price    BIGINT,
    close_price  BIGINT,
    volume       BIGINT,
    trade_amount BIGINT,
    created_at   TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (stock_code, trade_date)
);
```

---

## 4. 테스트 결과

### 4-1. 3종목 테스트 (005930, 000660, 035420)

| 종목 | 일봉 건수 | 분봉 건수 | 일봉 기간 |
|------|----------|----------|----------|
| 005930 (삼성전자) | 229건 | 3,252건 | 2025-03-24 ~ 2026-03-03 |
| 000660 (SK하이닉스) | 229건 | 2,418건 | 2025-03-24 ~ 2026-03-03 |
| 035420 (NAVER) | 229건 | 2,437건 | 2025-03-24 ~ 2026-03-03 |

### 4-2. 전종목 백필 진행 현황 (2026-03-03 20:21 기준)

```
go100_nxt_ohlcv_daily: 3,308건 (15종목) — 실행 중
v4_ohlcv_minute (NXT): 45,434건 (482종목) — 실행 중
```

> **주의**: 분봉은 기존 KRX 데이터와 동일 테이블 사용. NXT 운영시간(15:40~20:00) 분봉만 추가 적재.

---

## 5. 수집 아키텍처 (전체)

```
[키움 REST API]
  ka10081 (일봉) ─────→ go100_nxt_ohlcv_daily
  ka10080 (분봉) ─────→ v4_ohlcv_minute (15:40~20:00, 08:00~08:50)

[KIS WebSocket]
  N0STCNT0/N0STASP0 ──→ v4_tick_data + v4_ohlcv_minute (실시간)
  go100-ws-nxt.service: NXT_PM 15:40~20:00
  go100-ws-nxt-am.service: NXT_AM 08:00~08:50
```

---

## 6. 데이터 가용성 정리

| 구분 | API | 범위 | 비고 |
|------|-----|------|------|
| NXT 일봉 | 키움 ka10081 | 최근 229거래일 (약 11개월) | KIS 미지원(404) |
| NXT 분봉 | 키움 ka10080 | 최근 ~30거래일 | 연속조회 최대 10페이지 |
| NXT 실시간 틱 | KIS WS N0STCNT0 | 오늘부터 | go100-ws-nxt |
| NXT 실시간 분봉 | KIS WS 집계 | 오늘부터 | v4_ohlcv_minute |

---

## 7. 잔여/향후 작업

| 항목 | 상태 |
|------|------|
| 전종목 백필 완료 확인 | 내일 확인 (약 60~70분 소요) |
| go100_nxt_ohlcv_daily 주간 갱신 크론 | collect_nxt_stocks.py와 함께 매주 실행 검토 |
| NXT 일봉 신규 집계 (WS 분봉 → 일봉) | v4_ohlcv_minute 집계 SQL로 대체 가능 |
