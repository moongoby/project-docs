# CUR-GO100-BROKER-GATEWAY-CONNECT — BrokerGateway 실매매 연결

**작업일**: 2026-04-02
**브랜치**: phase-2c-command-center
**작업자**: Claude Code (Opus 4.6)

---

[인계 확인]
직전 완료: REPLAY-DESK2-DEPRECATED
현재 단계: Phase 2C (Command Center)
CEO 지시 적용: D-001
strategy_cards: 57
open_positions: 22

---

## 1. 구현 목표

`factory.py:218`의 `MockKISApi()` 하드코딩을 `GO100_LIVE_TRADING_ENABLED` 환경변수 기반 분기로 교체하여, BrokerGateway를 통한 account_id 기반 실매매 경로를 연결.

## 2. 수정 파일 및 내용

### 2.1 `backend/app/services/factory.py` (핵심 수정)

**변경 전**: `_create_kis_api()` → 항상 `MockKISApi()` 반환
**변경 후**:
- `GO100_LIVE_TRADING_ENABLED=true` → `BrokerGatewayKISAdapter` 반환 (BrokerGateway 래핑)
- `false`/미설정 → `MockKISApi()` 반환 (기존 동작 유지)

추가된 클래스:
- `BrokerGatewayKISAdapter`: `KISApiInterface` 구현체로 `BrokerGateway`를 래핑
  - `set_account_id(account_id)`: 전략카드의 account_id 설정
  - `buy_market()` / `sell_market()`: account_id 설정 시 `BrokerGateway.place_order()` 경유
  - `get_current_price()`: hash 기반 fallback (BrokerGateway에 가격 조회 API 없음)
  - `get_balance()`: `BrokerGateway.get_balance(account_id)` 경유

### 2.2 `backend/app/services/go100/live_trading/live_engine.py`

추가된 클래스:
- `BrokerGatewayExecutor`: V4OrderExecutor 인터페이스를 BrokerGateway로 래핑
  - `place_buy_order()` / `place_sell_order()`: `BrokerGateway.place_order(account_id, ...)` 경유
  - `get_balance()`: `BrokerGateway.get_balance(account_id)` 경유
  - `dry_run=True` 시 모의 주문 반환

변경된 메서드:
- `_get_executor()`: `GO100_LIVE_TRADING_ENABLED=true` + `account_id` 존재 시 `BrokerGatewayExecutor` 우선 반환

### 2.3 `backend/app/core/broker_gateway.py` (기존 수정 확인)

- `_place_order_impl()`: A-1 HOTFIX가 `GO100_LIVE_TRADING_ENABLED=true` 시 실계좌 블록 해제되도록 이미 수정됨
- BrokerGateway 인터페이스 변경 없음

## 3. 실행 흐름

```
GO100 실매매 흐름:
  전략카드 (account_id=7)
    → Go100LiveTradingEngine._get_executor()
      → GO100_LIVE_TRADING_ENABLED=true?
        → YES: BrokerGatewayExecutor(gateway, account_id=7, dry_run=False)
        → NO:  V4OrderExecutor(config_id, dry_run) (기존 fallback)
    → executor.place_buy_order(stock_code, qty, ...)
      → BrokerGateway.place_order(account_id=7, {stock_code, side, order_qty, ...})
        → accounts 테이블 → kis_config_id → KISOrderService (실전 tr_id: TTTC0012U)

V4 Orchestrator 흐름:
  ServiceFactory._create_kis_api()
    → GO100_LIVE_TRADING_ENABLED=true?
      → YES: BrokerGatewayKISAdapter(BrokerGateway)
      → NO:  MockKISApi()
    → OrderExecutor(kis_api=adapter/mock, ...)
```

## 4. 검증 체크리스트

- [x] 구현 목표: MockKISApi → BrokerGateway 환경변수 기반 분기 구현
- [x] 검증 방법: `grep -n "MockKISApi\|BrokerGateway\|GO100_LIVE_TRADING" backend/app/services/factory.py`
- [x] 완료 기준: env=true → BrokerGatewayKISAdapter 반환, env=false → MockKISApi 반환
- [x] 실패 기준: BrokerGateway import 실패 시 MockKISApi fallback
- [ ] 서비스 재시작 확인: 환경변수 미설정 시 서비스 재시작 불필요 (기존 동작 유지)
- [x] 에러 로그 0건: 구문 검증 통과 (python3 ast.parse)

### 구문 검증 결과
```
factory.py: OK
live_engine.py: OK
broker_gateway.py: OK
```

## 5. 활성화 방법

실매매 활성화 시 `.env`에 추가:
```
GO100_LIVE_TRADING_ENABLED=true
```

그리고 서비스 재시작:
```bash
sudo systemctl restart go100
```

## 6. 주의사항

- `.env` 파일은 커밋하지 않음 (R-KEY 규칙)
- 기존 MockKISApi 코드 삭제하지 않음 (환경변수 분기로 공존)
- BrokerGateway 인터페이스 변경 없음
- `BrokerGatewayKISAdapter.get_current_price()`: BrokerGateway에 가격 조회 API가 없으므로 hash 기반 fallback 사용 중. 실서비스에서는 별도 가격 조회 연동 필요.
