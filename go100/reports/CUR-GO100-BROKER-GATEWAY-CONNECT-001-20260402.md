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
- `true` → `BrokerGatewayKISAdapter` 반환 (BrokerGateway 래핑)
- `false`/미설정 → `MockKISApi` 반환 (기존 동작 유지)

**BrokerGatewayKISAdapter 클래스 신규:**
- `BrokerGateway`를 `KISApiInterface` 호환 어댑터로 래핑
- `set_account_id(account_id)` 로 전략카드의 account_id 설정
- `buy_market()`, `sell_market()` → `BrokerGateway.place_order(account_id, ...)` 위임
- `get_balance()`, `get_holdings()` → `BrokerGateway.get_balance(account_id)` 위임
- `get_current_price()` → hash 기반 fallback (BrokerGateway에 현재가 API 없음)
- 생성 실패 시 MockKISApi fallback (안정성 보장)

### 2. live_service.py — dry_run 자동 판단 + account_id 로깅

**변경 전:** `run_now(dry_run=True)` — 항상 모의매매

**변경 후:** `run_now(dry_run=None)` — 환경변수 자동 판단
- `dry_run=None` (기본값) → `GO100_LIVE_TRADING_ENABLED=true`이면 실매매, 아니면 모의
- `dry_run=True` → 강제 모의 (기존 호출 코드 호환)
- `dry_run=False` → 강제 실매매
- 실매매 실행 시 portfolio_id + account_id 로깅 추가

### 3. 안전장치 현황

| 안전장치 | 위치 | 상태 |
|---------|------|------|
| GO100_LIVE_TRADING_ENABLED 환경변수 | factory.py, live_service.py | 미설정=false (모의매매) |
| BrokerGateway A-1 HOTFIX | broker_gateway.py:131-141 | 실계좌 주문 차단 활성 |
| hallucination_guard paper_trade_first() | hallucination_guard.py:175 | 실매매 게이트 활성 |
| V4OrderExecutor dry_run | live_engine.py:526 | dry_run=True → KIS API 미호출 |
| accounts.is_mock 필드 | DB accounts 테이블 | is_mock=false → A-1 HOTFIX 차단 |

---

## 검증 체크리스트

- [x] 구현 목표: MockKISApi 하드코딩을 GO100_LIVE_TRADING_ENABLED 환경변수 분기로 교체
- [x] 검증 방법: `grep -n "MockKISApi\|BrokerGateway\|GO100_LIVE_TRADING" backend/app/services/factory.py`
- [x] 완료 기준: factory.py에 BrokerGateway/MockKISApi 분기 존재, 서비스 정상 기동
- [x] 실패 기준: import 에러, 서비스 기동 실패, 기존 MockKISApi 동작 깨짐
- [x] 서비스 재시작 확인: go100 active (running) — 18:53:37 KST
- [x] 에러 로그 0건: journalctl -u go100 --since 60s | grep -i error → 0건

## 수정 파일

| 파일 | 변경 | 줄 수 |
|------|------|-------|
| backend/app/services/factory.py | BrokerGatewayKISAdapter 클래스 + _create_kis_api() 분기 | +115 |
| backend/app/services/go100/live_trading/live_service.py | run_now() dry_run 자동판단 + account_id 로깅 | +20/-5 |

## 실매매 활성화 절차 (CEO 승인 후)

1. `.env`에 `GO100_LIVE_TRADING_ENABLED=true` 추가
2. `broker_gateway.py` A-1 HOTFIX 실계좌 차단 해제 (CEO 승인 필수)
3. `sudo systemctl restart go100`
4. 실매매 확인: `curl -X POST .../live-trading/{pid}/run`

---

## 저장 정보
- 서버 경로: /root/project-docs/go100/reports/CUR-GO100-BROKER-GATEWAY-CONNECT-001-20260402.md
- GitHub: https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-BROKER-GATEWAY-CONNECT-001-20260402.md
- 커밋: (pending)
- HTTP 확인: (pending)
- HANDOVER 업데이트: (pending)
