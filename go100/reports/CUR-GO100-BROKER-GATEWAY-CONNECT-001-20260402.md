# CUR-GO100-BROKER-GATEWAY-CONNECT-001-20260402
> GO100 실매매 전환 — BrokerGateway 연결

[인계 확인]
직전 완료: REPLAY-DESK2-DEPRECATED
현재 단계: Phase 2c — BrokerGateway 실매매 연결
CEO 지시 적용: D-001, D-003
strategy_cards: LIVE 6개 (user_id=3, account_id=7)
open_positions: 0

---

## 작업 내용

### 1. factory.py — MockKISApi 하드코딩 제거 (핵심 수정)

**변경 전:** `_create_kis_api()` → 항상 `MockKISApi()` 반환 (line 218)

**변경 후:** `GO100_LIVE_TRADING_ENABLED` 환경변수 기반 분기
- `true` → `BrokerGateway` 생성, `self.broker_gateway`에 저장 + MockKISApi 반환 (V4.1 안정성)
- `false`/미설정 → `self.broker_gateway = None` + MockKISApi 반환

**BrokerGatewayKISAdapter 클래스 신규 (line 20-114):**
- `BrokerGateway`를 `KISApiInterface` 호환 어댑터로 래핑
- `set_account_id(account_id)` 로 전략카드의 account_id 설정
- `buy_market()`, `sell_market()` → `BrokerGateway.place_order(account_id, ...)` 위임
- `get_balance()`, `get_holdings()` → `BrokerGateway.get_balance(account_id)` 위임
- V4.1 OrderExecutor 직접 연결용 (향후 V4.1 실매매 전환 시 사용)

### 2. live_engine.py — BrokerGatewayExecutor 경로 추가 (GO100 실매매 핵심)

**BrokerGatewayExecutor 클래스 신규 (line 37-84):**
- BrokerGateway를 V4OrderExecutor 인터페이스로 래핑
- `place_buy_order()`, `place_sell_order()` → `BrokerGateway.place_order()` 위임
- `get_balance()` → `BrokerGateway.get_balance()` 위임
- `dry_run=True` 시 모의 응답 반환

**`_get_executor()` 수정 (line 521-556):**
- 기존: 항상 V4OrderExecutor(config_id) 반환
- 변경: `GO100_LIVE_TRADING_ENABLED=true` + account_id → BrokerGatewayExecutor 반환
- BrokerGateway(db_pool=AsyncSessionLocal) — 올바른 import 경로 사용
- fallback: KIWOOM → V4OrderExecutor(KIWOOM) / KIS → V4OrderExecutor(config_id)

**버그 수정:**
- `from backend.app.database import` → `from backend.app.core.database import AsyncSessionLocal` (import 경로 수정)
- `gateway = BrokerGateway(db_pool=db.get_bind)` 데드코드 제거

### 3. 아키텍처 흐름

```
전략카드 (account_id=7)
  ↓
go100_portfolios (account_id=7)
  ↓
live_engine._get_executor()
  ├─ GO100_LIVE_TRADING_ENABLED=true + account_id
  │    ↓ BrokerGatewayExecutor
  │  BrokerGateway.place_order(account_id=7, {...})
  │    ↓
  │  accounts → KIS config_id=2 → KISOrderService (실전 tr_id TTTC0012U)
  │
  ├─ KIWOOM 계좌 → _make_kiwoom_executor()
  │
  └─ KIS fallback → V4OrderExecutor(config_id)
```

### 4. 안전장치 현황

| 안전장치 | 위치 | 상태 |
|---------|------|------|
| GO100_LIVE_TRADING_ENABLED 환경변수 | factory.py, live_engine.py | 미설정=false (모의매매) |
| BrokerGateway A-1 HOTFIX | broker_gateway.py:131-141 | 실계좌 주문 차단 활성 |
| BrokerGatewayExecutor dry_run | live_engine.py:53-54 | dry_run=True → 모의 응답 |
| hallucination_guard | hallucination_guard.py:178 | GO100_LIVE_TRADING_ENABLED 검사 |
| MockKISApi V4.1 보존 | factory.py:327-328 | V4.1 시스템은 항상 Mock 사용 |

---

## 검증 체크리스트

- [x] 구현 목표: MockKISApi 하드코딩을 GO100_LIVE_TRADING_ENABLED 분기로 교체 + live_engine BrokerGateway 경로 추가
- [x] 검증 방법: `grep -n "MockKISApi\|BrokerGateway\|GO100_LIVE_TRADING" backend/app/services/factory.py`
- [x] 완료 기준: factory.py + live_engine.py에 BrokerGateway 분기 존재, 서비스 정상 기동
- [x] 실패 기준: import 에러, 서비스 기동 실패, 기존 MockKISApi 동작 깨짐
- [x] 서비스 재시작 확인: go100 active, go100-frontend active
- [x] 에러 로그 0건: journalctl -u go100 --since 60s | grep -i error → 0건

## 수정 파일

| 파일 | 변경 | 줄 수 |
|------|------|-------|
| backend/app/services/factory.py | BrokerGatewayKISAdapter + _create_kis_api() 분기 | +115 |
| backend/app/services/go100/live_trading/live_engine.py | BrokerGatewayExecutor + _get_executor() BrokerGateway 경로 | +60 |

## DB 확인

| 항목 | 값 |
|------|-----|
| LIVE 카드 | 6개 (card_id 25, 72, 79, 83, 88, 89) |
| account_id=7 | KIS, 74032243, is_mock=false, config_id=2, active |
| PAPER_LIVE 카드 | 2개 (card_id 42, 43, account_id 미설정) |

## 실매매 활성화 절차 (CEO 승인 후)

1. `.env`에 `GO100_LIVE_TRADING_ENABLED=true` 추가
2. `broker_gateway.py` A-1 HOTFIX 실계좌 차단 해제 (CEO 승인 필수)
3. `sudo systemctl restart go100`
4. 소액 테스트: `curl -X POST .../live-trading/{pid}/run?dry_run=false`

---

## 저장 정보
- 서버 경로: /root/project-docs/go100/reports/CUR-GO100-BROKER-GATEWAY-CONNECT-001-20260402.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-BROKER-GATEWAY-CONNECT-001-20260402.md
- 커밋: (pending)
- HTTP 확인: (pending)
- HANDOVER 업데이트: (pending)
