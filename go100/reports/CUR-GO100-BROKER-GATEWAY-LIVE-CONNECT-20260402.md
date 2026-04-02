# CUR-GO100-BROKER-GATEWAY-LIVE-CONNECT — 실매매 전환 BrokerGateway 연결

**작업일**: 2026-04-02
**HANDOVER 버전**: v11.22

[인계 확인]
직전 완료: REPLAY-DESK2-DEPRECATED
현재 단계: Phase 8 실매매 전환
CEO 지시 적용: D-001, D-007

---

## 작업 요약

`GO100_LIVE_TRADING_ENABLED` 환경변수 기반으로 `MockKISApi` → `BrokerGateway` 실매매 전환 경로 구현.

## 수정 파일 (3개)

### 1. `backend/app/services/factory.py`
- `BrokerGatewayKISAdapter` 클래스 추가 (BrokerGateway → KISApiInterface 어댑터)
- `_create_kis_api()`: `GO100_LIVE_TRADING_ENABLED=true` → BrokerGateway 생성 + `self.broker_gateway`에 저장
- `false`(기본값) → 기존 MockKISApi 유지

### 2. `backend/app/services/go100/live_trading/live_engine.py`
- `BrokerGatewayExecutor` 클래스 추가 (BrokerGateway → V4OrderExecutor 인터페이스 어댑터)
  - `place_buy_order()`, `place_sell_order()`, `get_balance()` 구현
  - `dry_run=True` 시 API 미호출, 시뮬레이션 결과 반환
- `_get_executor()`: `GO100_LIVE_TRADING_ENABLED=true` + `account_id` 존재 시 `BrokerGatewayExecutor` 반환
  - 기존 V4OrderExecutor / KIWOOM 경로는 fallback으로 유지

### 3. `backend/app/core/broker_gateway.py`
- `_place_order_impl()`: HOTFIX 하드블록을 `GO100_LIVE_TRADING_ENABLED` 환경변수 기반 조건부로 변경
  - `true` → 실계좌 주문 허용 (WARNING 로그 기록)
  - `false`(기본값) → 기존 하드블록 유지 (안전 보장)
- KIS 실전 도메인 차단도 동일하게 환경변수 기반 조건부 적용

## 실행 흐름

```
전략카드 (account_id=7) → live_service.run_now() → live_engine.run_one_day()
  → _get_executor(pf, db, dry_run)
    → GO100_LIVE_TRADING_ENABLED=true?
      → YES: BrokerGatewayExecutor(gateway, account_id=7) 반환
      → NO:  V4OrderExecutor(config_id, dry_run) 반환 (기존 모의매매)
  → executor.place_buy_order() / place_sell_order()
    → BrokerGateway.place_order(account_id=7, {stock_code, side, qty, price})
      → accounts 테이블 → kis_config_id → KIS 실전 API (TTTC0012U)
```

## 검증 체크리스트

- [x] 구현 목표: MockKISApi → BrokerGateway 환경변수 기반 분기 구현
- [x] 검증 방법: `grep -n "MockKISApi\|BrokerGateway\|GO100_LIVE_TRADING" backend/app/services/factory.py`
- [x] 완료 기준: 3개 파일 수정, 구문 검사 통과, 서비스 재시작 성공, 에러 로그 0건
- [x] 실패 기준: 구문 오류, 서비스 시작 실패, 기존 MockKISApi 경로 손상
- [x] 서비스 재시작 확인: `systemctl restart go100` + `systemctl restart go100-frontend` 성공
- [x] 에러 로그 0건: `journalctl -u go100 --since "60s ago" | grep -i error` → 0건
- [x] Health check: `curl http://localhost:8002/health` → `{"status":"ok"}`

## 활성화 방법

```bash
# .env 파일에 추가 (절대 git commit 금지)
GO100_LIVE_TRADING_ENABLED=true

# 서비스 재시작
sudo systemctl restart go100
```

## 안전장치
1. 환경변수 미설정(기본값) → MockKISApi 유지 (모의매매)
2. BrokerGateway 생성 실패 시 → MockKISApi fallback
3. dry_run=True(기본값) → API 미호출
4. 실계좌 주문 시 WARNING 로그 자동 기록
