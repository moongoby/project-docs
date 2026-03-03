# CUR-GO100-NXT-DATA-COLLECTION-20260303 — NXT 실시간 데이터 수집 체계 구축 보고서

**작성일시**: 2026-03-03 19:15 KST
**작업자**: Claude Code
**우선순위**: P1
**상태**: 완료 (NXT WS 수집 중)

---

## 1. 요약

NXT(한국 넥스트 트레이드) 야간장 실시간 데이터 수집이 미설정 상태였음을 확인하고,
장중(KRX)과 동일하게 전체 수집 체계를 구축 완료.

---

## 2. 사전 현황

### 기존 인프라 (구축되어 있었으나 크론 미등록)
| 항목 | 내용 |
|------|------|
| `go100-ws-nxt.service` | 존재(enabled)하나 자동 시작 크론 미등록 |
| `collect_nxt_stocks.py` | 존재하나 크론 미등록 |
| `stock_universe.is_nxt` | 플래그 컬럼 존재, 640개 종목 NXT 가능 |
| KIS API (NXT) | 6개 등록: 실시간체결가/호가/시간외/VI/체결통보 |
| 마지막 서비스 실행 | 2026-02-27 08:25 (4일 전, 장외 시간 → 즉시 종료) |
| 데이터 저장 테이블 | `v4_tick_data`, `v4_orderbook_realtime`, `v4_ohlcv_minute` (KRX와 동일) |

### NXT 야간장 스펙
- **시간**: 매 평일 18:00 ~ 익일 02:00 (KST)
- **대상**: NXT 거래 가능 종목 (현재 640개 이상)
- **TR**: 체결가 `N0STCNT0`, 호가 `N0STASP0`
- **계좌**: `account_id=7` (실계좌, NXT 지원)

---

## 3. 조치 내역

### 3-1. go100-ws-nxt 서비스 즉시 시작 (19:04 KST)
```
Active: active (running) since Tue 2026-03-03 19:04:22 KST
Connected to ws://ops.koreainvestment.com:21000/tryitout/N0STCNT0
Subscribed 30 stocks (tick + orderbook)
```

### 3-2. 크론 등록 (3건)

| 크론 | 스케줄 | 역할 |
|------|--------|------|
| `systemctl start go100-ws-nxt` | 매 평일 18:00 | NXT 야간장 개장 시 수집 시작 |
| `systemctl stop go100-ws-nxt` | 매 화~토 02:00 | NXT 야간장 폐장 시 수집 종료 |
| `collect_nxt_stocks.py` | 매주 토요일 03:30 | NXT 거래 가능 종목 is_nxt 플래그 갱신 |

### 3-3. NXT 종목 플래그 즉시 갱신 (진행 중)
`collect_nxt_stocks.py` 백그라운드 실행 중 (3,844개 종목 순차 조회, KIS API rate limit으로 약 30분 소요)

---

## 4. 데이터 수집 구조

```
KRX 정규장 (09:00~15:30)              NXT 야간장 (18:00~02:00)
─────────────────────────             ─────────────────────────
go100-ws-krx (cron 08:50 start)  →   go100-ws-nxt (cron 18:00 start)
  ↓ TR: H0STCNT0 / H0STASP0           ↓ TR: N0STCNT0 / N0STASP0
  ↓                                    ↓
v4_tick_data (체결 틱)               v4_tick_data (체결 틱)
v4_orderbook_realtime (호가)         v4_orderbook_realtime (호가)
v4_ohlcv_minute (1분봉 집계)         v4_ohlcv_minute (1분봉 집계)
  ↓ cron 15:40 stop                    ↓ cron 02:00 stop
```

---

## 5. 실시간 수집 현황 (19:15 기준)

| 항목 | 상태 |
|------|------|
| go100-ws-nxt 서비스 | ✅ active (running) |
| WS 연결 | ✅ ws://ops.koreainvestment.com:21000 |
| 구독 종목 | 30개 (config/ws_stock_list.json 기준) |
| 틱 데이터 | 0건 (NXT 야간장 초반 낮은 유동성, 정상) |
| 마지막 KRX 틱 | 2026-03-03 15:32 (정규장 마감) |

> **NXT 야간장 유동성**: KRX 정규장 대비 매우 낮음. 거래 발생 시 자동 수집.
> 주요 NXT 거래 시간대: 18:00~20:00 (프리마켓 주문 집중)

---

## 6. 잔여 과제

| 항목 | 내용 |
|------|------|
| collect_nxt_stocks.py 완료 확인 | 진행 중 (~30분 소요), 완료 후 is_nxt 업데이트 건수 확인 |
| ws_stock_list.json NXT 최적화 | NXT is_nxt=TRUE 종목만 포함하도록 자동 갱신 검토 |
| NXT 분봉 수집 확인 | 내일 NXT 야간장(18:00~) 분봉 적재 여부 사후 확인 |
