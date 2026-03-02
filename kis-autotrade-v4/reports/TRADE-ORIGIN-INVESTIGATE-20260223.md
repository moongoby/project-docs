# TRADE-ORIGIN-INVESTIGATE 보고서 (2026-02-23)

**작성일시:** 2026-02-23 14:25 KST  
**서버:** root@[SERVER-IP]  
**우선순위:** P0 (긴급 — 미확인 실계좌 거래 추적)  
**조사 방식:** 읽기 전용 (코드/DB/서비스 수정 없음)

---

## 1. 거래 출처 추적 결과

| 시스템 | 152550 거래 기록 | 74*** 계좌 등록 | 로그/증거 |
|--------|------------------|-----------------|-----------|
| **V4.1** | **N** | **N** (virtual만 사용) | v4_positions 152550 0건, v4_order_* 0건, v4_account_config=virtual 1건, journalctl 152550/ANKOR 무관 로그만 |
| **GO100** | **N** | **Y** (accounts에 74*** 존재) | go100_orders/go100_trades/go100_positions 152550 0건 |
| **레거시(68)** | **미확인** | **미확인** | 68서버 SSH 접속 불가 (타임아웃) |

### 1.1 상세 근거

- **V4.1**
  - `v4_account_config`: id=1, account_type=**virtual**, is_active=t → 74*** 미등록.
  - `v4_positions`: ticker='152550' 0건, 오늘(2026-02-23) 생성 포지션 0건.
  - `v4_order_requests`, `v4_order_executions`, `v4_trade_executions`: 152550 오늘 0건.
  - kis-v41-api / kis-v41-scheduler 로그: 152550·ANKOR 관련 주문/매매 로그 없음.
- **GO100**
  - `go100_orders`, `go100_trades`, `go100_positions`: stock_code='152550' 0건.
  - `accounts`: account_id=7 → 74***, is_mock=f, broker_type=KIS (실계좌 등록됨).
- **레거시(68)**
  - `ssh root@[SERVER-IP-68]` 접속 불가 → 68서버 내 로그/DB 미확인.
  - 113 서버 .env 내 68/레거시 IP 직접 설정 없음.

---

## 2. 113 서버 자동매매와 13:58 매수 시점

- **kis-trading-engine.service** (unified_trading_scheduler)가 1분 주기로 **realtime_general_market_auto_trade.py**(일반시장 실매매) 실행.
- **13:58:32~13:58:33** 로그: `일반시장 실매매 실행` 직후 **PRAGMA busy_timeout=30000** (SQLite 문법) 실행으로 **PostgreSQL SyntaxError** 발생 → **실매매 스크립트가 DB 연결 단계에서 크래시, 주문 로직 미실행**.
- 동일 PRAGMA 오류로 14:01, 14:02, 14:03, 14:04에도 실매매 스크립트 반복 실패.
- **결론:** 13:58 매수·14:02 매도 체결 시점에 113 서버의 **일반시장 실매매 스크립트는 정상 실행되지 않았음**. 해당 거래는 **113 서버 자동매매 파이프라인으로는 설명 불가**.

---

## 3. V4.1 현재 상태

### 3.1 OPEN 포지션 (5건)

| id | ticker | desk_id | card_id | status | entry_price | quantity | entry_date |
|----|--------|---------|---------|--------|-------------|----------|------------|
| 49 | 221800 | 1 | NULL | OPEN | 19070 | 1820 | 2026-02-20 |
| 51 | 001510 | 2 | NULL | OPEN | 1579 | 11883 | 2026-02-20 |
| 53 | 001290 | 2 | NULL | OPEN | 1175 | 16806 | 2026-02-20 |
| 55 | 373110 | 3 | NULL | OPEN | 1619 | 12595 | 2026-02-20 |
| 61 | 360140 | 4 | NULL | OPEN | 12935 | 2005 | 2026-02-20 |

(152550 한국ANKOR유전 없음.)

### 3.2 펀드풀 / 잔고 / 하트비트

- `v4_fund_pool_snapshot`: 0건.
- `v4_system_heartbeat`: 1건 (2026-02-13 11:04:59, state=IDLE).
- `v4_trade_analysis`: 0건.

### 3.3 오늘(2026-02-23) 매매 이력

- `v4_positions` 중 created_at >= '2026-02-23': **0건**.

---

## 4. 113 서버 트레이딩 관련 프로세스·서비스

### 4.1 systemd 서비스 (트레이딩 관련)

| 서비스 | 상태 | 비고 |
|--------|------|------|
| kis-v41-api | active | 8003 |
| kis-v41-scheduler | active | — |
| kis-v41-monitor | active | — |
| kis-v41-position-monitor | active | — |
| kis-v41-minute-collector | active | — |
| kis-trading-engine | active | unified_trading_scheduler (일반/NXT 실매매) |
| kis-scalping | active | 스냅샷 수집 전용, 주문 미실행 |
| kis-webapp-api | active | — |
| go100 | active | 8002 |
| go100-frontend | active | 3000 |

### 4.2 포트

- 8001: (기타)
- 8002: go100 (API)
- 8003: kis-v41-api
- 3000: go100-frontend
- 3001: (기타)

### 4.3 crontab

- 자동매매 직접 실행(trade/order/buy/sell/execute/go100) 항목 없음.  
- vkospi, data_miner, alert_cron, minute_batch 등 데이터/알림 위주.

---

## 5. 계좌·KIS 설정 요약 (마스킹)

- **accounts**: 74*** (account_id=7, is_mock=f, KIS) 등록됨.
- **v4_account_config**: 74*** 미등록, virtual 1건만 사용.
- **kis_configs**: user_id 15·27 → 74*** (실계좌), 6·18·28 → 50*** (모의).

---

## 6. 결론

- **거래 발생 시스템:** **미확인** (113 서버 V4.1·GO100·레거시 orders/실매매 스크립트로는 특정 불가).
- **152550:** V4.1·GO100 DB 및 로그에 **기록 없음**.
- **74***:** V4.1에는 미등록, GO100/공유 accounts에는 등록. kis_configs에 74*** 연결 사용자 존재.
- **위험 판단:** 113 서버 V4.1 파이프라인은 모의계좌만 사용하며 152550 거래 없음. 실계좌 74*** 거래는 **수동 주문(HTS/모바일)·68 서버 레거시·기타 클라이언트** 가능성 있음. 68 서버 접속 불가로 레거시 여부는 미확인.

---

## 7. DB 무결성

- **strategy_cards:** 62건.
- **v4_positions OPEN:** 5건 (ID 49, 51, 53, 55, 61).

---

## 8. 권장 사항 (참고)

1. 68 서버 접속 가능 시: 레거시 프로세스·로그·orders 테이블에서 152550·74***·주문번호 28593800/28801100 검색.
2. 수동 주문 여부: 동일 계좌·동일 시간대 HTS/모바일 사용 이력 확인.
3. kis-trading-engine: realtime_general_market_auto_trade.py의 **PRAGMA** 사용 제거 또는 PostgreSQL 호환 처리 후, 실계좌 사용 여부는 정책에 따라 별도 검토.

---

*본 보고서는 읽기 전용 조사 결과이며, strategy_cards·v4_positions·코드·서비스는 수정하지 않았습니다.*
