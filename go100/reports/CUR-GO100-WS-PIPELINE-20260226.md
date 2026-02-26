# CUR-GO100-WS-PIPELINE-20260226 — 실시간 틱·호가·분봉 수집 파이프라인

**날짜**: 2026-02-26
**작성 시각**: KST 19:32

---

## 1. 구축 개요

KIS WebSocket API를 이용한 실시간 데이터 수집 클라이언트 신규 구축.

| 항목 | 내용 |
|---|---|
| 파일 | `backend/app/services/data/kis_ws_collector.py` (520행) |
| 패키지 | websockets 15.0.1, httpx (기존) |
| 수집 대상 | 틱(체결), 호가(10단계), 1분봉(틱 집계) |

---

## 2. 지원 세션

| 세션 | 시간 (KST) | TR ID (체결/호가) | 계정 | 비고 |
|---|---|---|---|---|
| KRX 정규장 | 08:55~15:35 | H0STCNT0 / H0STASP0 | account_id=1 (모의) | 월~금 |
| NXT 야간장 | 18:00~02:00 | N0STCNT0 / N0STASP0 | account_id=7 (실계좌) | NXT는 실계좌 필수 |

---

## 3. DB 적재 테이블

| 테이블 | 데이터 | 적재 방식 |
|---|---|---|
| `v4_tick_data` | 체결 틱 (종목, 시각, 가격, 수량, 매수/매도, 체결강도) | 5초 버퍼 벌크 INSERT |
| `v4_orderbook_realtime` | 10단계 호가 (매수/매도 가격·수량, 스프레드 등) | 5초 버퍼 벌크 INSERT |
| `v4_ohlcv_minute` | 1분봉 OHLCV (틱에서 실시간 집계) | 완료된 분 단위 UPSERT |

### 분봉 집계 로직
- 틱 수신 시 `(종목, 날짜, 분)` 키로 OHLCV 누적
  - open = 첫 체결가, high = max, low = min, close = 최종 체결가
  - volume 합산, trade_amount = price × volume 합산
- 5초 flush 주기마다 **완료된 분**(현재 분 제외)을 DB UPSERT
- 종료 시 현재 진행 중인 분 포함 force flush

---

## 4. 아키텍처

```
KIS WebSocket Server (:21000)
        │
        ▼
┌─────────────────────────┐
│  KISWebSocketCollector  │
│  - _parse_tick()        │──→ _tick_buffer      ──→ v4_tick_data
│  - _parse_orderbook()   │──→ _orderbook_buffer ──→ v4_orderbook_realtime
│  - _update_minute_bar() │──→ _minute_bars      ──→ v4_ohlcv_minute
│  - _flush_to_db() 5s    │
└─────────────────────────┘
        │
    auto session: KRX/NXT 시간 자동 판정
    재접속: 연결 끊김 시 자동 재연결
    종료: 장 마감 시 자동 종료
```

---

## 5. systemd 서비스

| 서비스 | 파일 | 상태 |
|---|---|---|
| `go100-ws-krx.service` | `/etc/systemd/system/go100-ws-krx.service` | enabled (정규장 시간에 수동 시작) |
| `go100-ws-nxt.service` | `/etc/systemd/system/go100-ws-nxt.service` | **active (running)** |

### 운영 명령어
```bash
# 상태 확인
systemctl status go100-ws-krx
systemctl status go100-ws-nxt

# 시작/중지
systemctl start go100-ws-nxt
systemctl stop go100-ws-nxt

# 로그 확인
journalctl -u go100-ws-nxt -f
journalctl -u go100-ws-krx --since "1 hour ago"
```

---

## 6. 테스트 결과

### 6-1. NXT 야간장 테스트 (KST 19:28)

| 단계 | 결과 |
|---|---|
| Credentials 로드 | OK (account_id=7, mock=False) |
| Approval Key 발급 | OK (POST /oauth2/Approval → 200) |
| WebSocket 연결 | OK (`ws://ops.koreainvestment.com:21000/tryitout/N0STCNT0`) |
| 종목 구독 | OK (40종목 tick + orderbook) |
| 데이터 수신 | NXT 거래량 부족으로 미수신 (정상) |

### 6-2. systemd 서비스 테스트

| 항목 | 결과 |
|---|---|
| 서비스 시작 | OK (`active (running)`) |
| 메모리 사용 | 54.5MB |
| PID/로그 | journalctl 정상 출력 |

---

## 7. 주요 설계 결정

| 결정 | 이유 |
|---|---|
| 세션당 40종목 제한 | KIS WS 구독 제한 (향후 멀티세션 확장) |
| 5초 flush 주기 | DB 부하와 데이터 지연의 균형 |
| ON CONFLICT UPSERT (분봉) | 재시작 시 중복 방지 |
| NXT는 실계좌만 | KIS API 정책 (virtual_supported=False) |
| 분봉: 현재 분 제외 | 미완성 분봉 DB 적재 방지 |

---

## 8. 파일 목록

| 경로 | 설명 |
|---|---|
| `backend/app/services/data/kis_ws_collector.py` | WebSocket 수집 클라이언트 (메인) |
| `/etc/systemd/system/go100-ws-krx.service` | KRX 정규장 systemd 서비스 |
| `/etc/systemd/system/go100-ws-nxt.service` | NXT 야간장 systemd 서비스 |
