# CUR-GO100-SUPPLY-DEMAND-AUDIT-001-20260302

> **CEO P0 지시 이행: 실시간 수급 데이터 전수 조사 보고**
> CEO 지시: "최우선 진행해 실시간 수급데이터부터 확인 반영하고"
> 생성: 2026-03-02 20:20 KST | 조사자: Cursor

---

## 1. 수급 관련 테이블 전수 목록

총 **10개** 핵심 수급 테이블 확인

| # | 테이블명 | 행수 | 날짜 범위 | 분류 |
|---|----------|------|-----------|------|
| 1 | `go100_investor_flow` | 275,846 | 2010-01-28 ~ 2026-02-27 | 종목별 투자자 수급 (외국인/기관/개인) |
| 2 | `v4_investor_daily` | 275,846 | 2010-01-28 ~ 2026-02-27 | V4.1 종목별 수급 (동일 구조) |
| 3 | `v4_market_investor_daily` | 3,620 | 2018-10-15 ~ 2026-02-27 | 시장 전체 수급 (KOSPI/KOSDAQ) |
| 4 | `go100_tick_data` | 878,813 | 2026-02-27 | 실시간 틱 데이터 |
| 5 | `v4_tick_data` | 878,813 | 2026-02-27 | V4.1 틱 데이터 (동일 내용) |
| 6 | `go100_orderbook_snapshot` | 1,401,273 | 2026-02-27 | 실시간 호가 스냅샷 |
| 7 | `v4_orderbook_realtime` | 1,401,273 | 2026-02-27 | V4.1 호가 실시간 (동일 내용) |
| 8 | `v4_trade_strength_history` | 231,307 | 2025-11-26 ~ 2026-02-27 | 거래 강도 (VP 관련) |
| 9 | `v4_program_trades` | 287 | 2026-02-25 ~ 2026-02-25 | 프로그램 매매 |
| 10 | `go100_tick_daily_stats` | 21 | 2026-02-27 | 틱 일별 통계 |
| 11 | `go100_orderbook_daily_stats` | **0** | — | 호가 일별 통계 (⚠️ 비어있음) |

---

## 2. 투자자별 수급 상세 (go100_investor_flow / v4_investor_daily)

### 컬럼 구조 (20개 필드)
- 기본: `stock_code`, `trade_date`
- 외국인: `foreign_buy_qty`, `foreign_sell_qty`, `foreign_net_qty`, `foreign_net_amount`, `foreign_hold_qty`, `foreign_hold_ratio`
- 기관: `institution_buy_qty`, `institution_sell_qty`, `institution_net_qty`, `institution_net_amount`
- 개인: `individual_net_qty`, `individual_net_amount`
- 프로그램: `program_buy_amount`, `program_sell_amount`, `program_net_amount`
- 파생: `consecutive_foreign_buy_days`, `consecutive_institution_buy_days`

### 최근 10영업일 현황
| 날짜 | 종목수 | 외국인매수종목 | 3일연속외국인매수 |
|------|--------|---------------|-----------------|
| 2026-02-27 | 3,839 | 1,493 | **269** |
| 2026-02-26 | 3,839 | 1,302 | 0 |
| 2026-02-25 | 3,839 | 1,363 | 0 |
| 2026-02-24 | 3,839 | 1,771 | 68 |
| 2026-02-23 | 3,839 | 1,909 | 639 |

**최신 데이터: 2026-02-27 (금요일) — 03-03(월) 데이터 미수집 상태**

---

## 3. 시장 전체 수급 (v4_market_investor_daily)

| 날짜 | 시장 | 외국인순매수(백만) | 기관순매수(백만) |
|------|------|------------------|-----------------|
| 2026-02-27 | KOSPI | **-70.5억** | +5.7억 |
| 2026-02-27 | KOSDAQ | +0.6억 | +4.5억 |
| 2026-02-26 | KOSPI | -21.1억 | +12.6억 |
| 2026-02-25 | KOSPI | -13.1억 | +14.7억 |

**KOSPI 외국인 3일 연속 순매도 중 (02-25~02-27)**

---

## 4. 실시간 데이터 (틱/호가)

| 테이블 | 행수 | 최신 날짜 | 비고 |
|--------|------|-----------|------|
| go100_tick_data / v4_tick_data | 878,813 | 2026-02-27 | 02-27 1일치 수집 완료 |
| go100_orderbook_snapshot / v4_orderbook_realtime | 1,401,273 | 2026-02-27 | 02-27 1일치 호가 완료 |
| v4_trade_strength_history | 231,307 | 2026-02-27 | VP 거래강도 11-26~02-27 |

**현재 갭 (03-03 기준): 02-28 ~ 03-02 실시간 데이터 미수집**

---

## 5. 이슈 및 개선 권고

### 이슈 1: go100_orderbook_daily_stats 비어있음 (0건)
- 현상: 테이블 존재하지만 집계 데이터 없음
- 원인: 일별 통계 집계 cron 미실행 또는 수집 후 집계 누락
- 조치: go100_orderbook_snapshot → daily_stats 집계 배치 필요

### 이슈 2: 실시간 데이터 02-28~03-02 갭 (주말/공휴일 제외 시 02-28 영업일 데이터 누락)
- 02-28(금) 영업일 틱/호가 데이터 미수집
- 원인: WebSocket 수집 cron 미동작 또는 저장 오류
- 조치: go100-ws-nxt/go100-ws-daytime 서비스 재가동 및 02-28 데이터 수집 재시도

### 이슈 3: v4_program_trades 데이터 희소 (287건, 02-25만)
- 조치: 프로그램 매매 수집 주기 확인

---

## 6. KIS AutoTrade V4.1 CTE 파이프라인 반영 현황

현재 CTE 파이프라인에서 수급 데이터 활용:
- **L3.3 SupplyDemandGate**: go100_investor_flow/v4_investor_daily 활용
  - `consecutive_foreign_buy_days >= 3` → ALLOW (외국인 3일 연속 매수)
  - `institution_net_qty > 0` → 가점
- **L4.5 EQS**: `vp_ratio` 활용 (v4_trade_strength_history)

**03-03 Virtual Run 수급 데이터 상태**: 02-27 데이터 정상 (3,839종목, 외국인매수 269종목 ALLOW 후보)

---

## OVERALL

| 항목 | 결과 |
|------|------|
| 수급 테이블 전수 조사 | ✅ 10개 테이블 |
| 외국인/기관/개인 수급 | ✅ 275,846건 (2010~2026-02-27) |
| 실시간 틱/호가 | ✅ 02-27 기준 최신 |
| 이슈 | ⚠️ go100_orderbook_daily_stats 0건, 02-28 데이터 갭 |
| CTE L3.3 반영 | ✅ 02-27 기준 정상 작동 예상 |
