# DESK2-INFRA-CHECK-001

**일시:** 2026-02-27  
**목적:** DESK2 재설계를 위한 서버 데이터·인프라 현황 점검  
**규칙:** kis-v41-* 서비스 재시작 금지, strategy_cards/v4_positions 직접 변경 금지

---

## 1. DB 무결성: strategy_cards=?, v4_positions OPEN=?

| 항목 | 기대값 | 실제값 | 비고 |
|------|--------|--------|------|
| strategy_cards | 62 | **60** | 기준 불일치 — 즉시 중단·보고 대상 |
| v4_positions (status='OPEN') | 5 | **14** | 기준 불일치 — 즉시 중단·보고 대상 |

**결론:** 사전확인 기준(62, 5)과 불일치. DB/서비스 변경 없이 읽기 전용 점검만 수행함.

---

## 2. 수집기 상태

| 서비스 | 상태 | 비고 |
|--------|------|------|
| kis-v41-minute-collector | **active** | 2026-02-27 08:54:25 기동, 약 3h 33min 가동 중 |
| kis-v41-orderbook-collector | **inactive** | dead, disabled |

**minute-collector 최근 로그 요약:**  
- `backend.app.services.data_pipeline.collector_minute --days 66 --oldest-first` 실행 중  
- KIS API `inquire-time-dailychartprice` 호출 정상 (HTTP 200), 065350, 437730, 462350, 214180 등 종목 분봉 수집 중

**orderbook-collector:**  
- inactive(dead). 최근 로그 없음.

**기타 관련 서비스 (systemd):**  
- go100-ws-krx.service — active (GO100 KIS WebSocket)  
- kis-v41-api, kis-v41-monitor, kis-v41-scheduler — active  
- kis-v41-position-monitor — active  
- kis-scalping.service, kis-trading-engine.service — active  

**크론 (수집 관련):**  
- `0 16 * * 1-5` / `0 2 * * 6`: minute_batch_cron.sh  
- `*/5 9-15 * * 1-5`: collect_strength_intraday.sh  
- `40 16 * * 1-5`: run_orderbook_daily_stats.sh  
- `50 16 * * 1-5`: run_tick_daily_stats.sh  
- 기타: collect_ohlcv_daily, collect_market_investor, collect_program_trades 등

---

## 3. 호가·틱 데이터 현황

**호가/틱 관련 테이블:**

| 테이블명 | 행수 | 비고 |
|----------|------|------|
| go100_orderbook_snapshot (VIEW) | 690,425 | v4_orderbook_realtime 기반 뷰 |
| v4_orderbook_realtime | 690,425 | 실시간 호가 스냅샷 |
| orderbook_snapshots | 35,894 | 레거시 호가 스냅샷 |
| v4_tick_data | 457,592 | 틱 데이터 |
| go100_orderbook_daily_stats | (미집계) | 일별 호가 통계 |
| go100_tick_daily_stats | (미집계) | 일별 틱 통계 |
| price_tick_snapshots | (미집계) | 가격 틱 스냅샷 |

**최신 데이터 시각:**  
- v4_orderbook_realtime: **2026-02-27 12:28:02** (당일 실시간 수집 중)

**틱/체결 관련 테이블:**  
- v4_tick_data, v4_order_executions, v4_trade_executions, price_tick_snapshots

---

## 4. 분봉 데이터 (3개월)

| 항목 | 값 |
|------|-----|
| 시작일 | 2025-02-18 |
| 종료일 | 2026-02-27 |
| 총 행수 | 43,216,742 |
| 컬럼 | trade_date, trade_time, stock_code, OHLCV 등 (partition by trade_date) |

**최근 90일(약 3개월) 일별:**  
- 거래일 58일분 집계됨 (2025-12-01 ~ 2026-02-27)  
- 일별 행수: 약 17만 ~ 21만 건, 종목 수 498~567  
- 2026-02-27: 당일 부분 수집만 반영 (3,672 bars, 21 symbols) — 장중 수집 진행 중  
- 2026-02-16, 17, 18, 21, 22: 휴장/주말로 데이터 없음  
- 2026-01-01, 01-03, 01-04: 휴장/연휴로 미수집

**데이터 빈 날짜 (거래일인데 행 0):**  
- 명시적 “거래일인데 0건”인 날 없음. 휴장일·주말 제외 후 누락 거래일 없음.

---

## 5. 일봉·뉴스 데이터 범위

| 데이터 | 최초일 | 최종일 | 총 행수 |
|--------|--------|--------|---------|
| ohlcv_daily | 2023-01-02 | 2026-02-26 | 2,611,905 |
| go100_news_items | 2025-02-27 | 2026-02-26 | 2,140,477 |

(뉴스는 data_date 기준)

---

## 6. 레짐 데이터

| 항목 | 값 |
|------|-----|
| v4_market_regime_daily 총 행수 | 822 |
| market_type | KOSPI / KOSDAQ 별 일자별 1행씩 |
| 2025-11-01 이후 일자 | 153행 (약 76일×2 + 일부) — 누락일 없음 |

**OHLC=0 대체 확인 (ma5/ma20/ma60=0):**  
- open_price/close_price 컬럼 없음. ma5, ma20, ma60 사용.  
- **ma5=0 또는 ma20=0**인 행 다수 존재 (예: 2026-01-12~27, 2026-02-10~11 KOSPI/KOSDAQ, 2025-12-15~18 등).  
- 해당 구간은 지수 데이터 부재 또는 초기화 이슈 가능성.

---

## 7. VI 테이블: 존재 여부, 행수

| 항목 | 값 |
|------|-----|
| v4_vi_occurrences 존재 | 예 |
| 행수 | 319 |

---

## 8. DESK2 테이블: 존재 여부, 각 행수

| 테이블명 | 존재 | 행수 |
|----------|------|------|
| v4_desk2_candidates | 예 | 0 |
| v4_desk2_daily_summary | 예 | 0 |
| v4_desk2_signals | 예 | 0 |
| v4_desk2_trades | 예 | 0 |

DESK2 관련 테이블 4개 모두 존재하나, 현재 데이터 없음 (재설계·배치 전 상태).

---

## 9. 디스크/메모리/서비스 상태

**디스크:**  
- `/` : 99G 중 67G 사용, 28G 가용 (**71%**)

**메모리:**  
- total 15Gi, used 7.8Gi, free 672Mi, available 7.8Gi  
- Swap 8Gi 중 1.9Gi 사용

**uptime:**  
- 12:28:47 기준 14일 19시간 11분 가동  
- load average: 1.39, 1.27, 1.29

**주요 서비스:**  
- kis-v41-api: **active**  
- kis-v41-monitor: **active**  
- kis-v41-scheduler: **active**

---

## 요약 및 권장사항

1. **DB 무결성:** strategy_cards 60건, v4_positions OPEN 14건 — 사전 기대(62, 5)와 불일치. 원인 확인 및 운영 정책 검토 권장.  
2. **수집기:** minute-collector 정상 가동 중. orderbook-collector는 비가동 — 필요 시 활성화 검토.  
3. **호가/틱:** v4_orderbook_realtime·v4_tick_data 적재 정상, 당일 호가 최신 시각 12:28.  
4. **분봉:** 최근 3개월 58거래일분 충실, 당일은 장중 수집 중.  
5. **레짐:** ma5/ma20=0 행 존재 — 지수/입력 데이터 점검 권장.  
6. **DESK2:** 테이블만 준비됨, 데이터 0 — 재설계·파이프라인 반영 후 적재 예정.
