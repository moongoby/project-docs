# CUR-GO100-TRADE-MODAL-IMPL-001 — 자동매매 시작 모달 구현 보고서

**작성일:** 2026-02-25 (KST)  
**작업 ID:** CUR-GO100-TRADE-MODAL-IMPL-001  
**우선순위:** P0 ★ 최우선  
**브랜치:** feat/CUR-GO100-TRADE-MODAL-IMPL-001 → phase-2c-command-center  

---

## 1. 구현 요약

- **GO100 전용 Trade Router** 신규 추가: `backend/app/routers/go100/go100_trade_router.py`
- **main.py**: `trade_modal_router` 대신 `go100_trade_router` 등록 (동일 prefix `/api/go100/trade`)
- **실계좌(account_id 5, 6)** 사용 시 **403** 응답: "실계좌 사용은 대표님 승인이 필요합니다. 모의계좌(account_id=4)를 사용하세요."
- **이미 활성 스케줄** 존재 시 **409**: "이미 활성 자동매매가 진행 중입니다."
- **run_interval**: `5m`, **market_open_only**: true, **card_source**: `'go100'`
- **GET /accounts**: 실계좌(5, 6)에 **is_locked: true** 추가
- **프론트 AutoTradeModal**: 제목에 전략명, 계좌 locked 비활성화·"(대표님 승인 필요)", 기본 선택 account_id=4, 성공 시 Toast, z-[9998]
- **DB 마이그레이션**: `backend/migrations/027_go100_trade_schedules_card_source.sql` — `v4_trade_schedules.card_source` 컬럼 보장

---

## 2. 수정·신규 파일 목록

| 구분 | 경로 |
|------|------|
| **신규** | `backend/app/routers/go100/go100_trade_router.py` |
| **신규** | `backend/migrations/027_go100_trade_schedules_card_source.sql` |
| **수정** | `backend/app/main.py` (go100_trade_router import 및 등록) |
| **수정** | `frontend/src/go100/components/AutoTradeModal.tsx` (제목, 계좌 locked, 기본 4, 토스트, z-index) |
| **수정** | `frontend/src/go100/api/go100Api.ts` (TradeAccount에 `is_locked` 추가) |

**보호 파일 (미수정):**  
`backend/app/api/v1/trade_router.py`, `ScheduleForm`, `auto_trade_engine`, `client.ts`, `auth-store`

---

## 3. API 명세 (go100_trade_router)

- **POST /api/go100/trade/start**  
  Body: `go100_card_id`, `account_id`, (선택) `invest_amount`, `max_stocks`, `stop_loss_pct`, `take_profit_pct`  
  - account_id 5 또는 6 → 403  
  - 이미 활성 스케줄 → 409  
  - 성공: `v4_trade_schedules` INSERT (card_source='go100', run_interval='5m'), `go100_strategy_cards` UPDATE (is_active=true, account_id)

- **POST /api/go100/trade/stop**  
  Body: `go100_card_id`  
  - 해당 카드 go100 스케줄·카드 is_active false

- **GET /api/go100/trade/status/{card_id}**  
  - 없음: `{ "status": "no_schedule" }`  
  - 있음: `status`, `schedule_id`, `account_id`, `invest_amount`, `max_stocks`, `last_run_at`, `next_run_at` + 프론트 호환 `is_trading`, `schedule`, `account`

- **GET /api/go100/trade/accounts**  
  - 활성 계좌 목록, 실계좌(5, 6)에 `is_locked: true`

---

## 4. 토글 연동 (기존 유지)

`backend/app/routers/go100/strategy_router.py`  
- **PATCH /{card_id}/toggle**: is_active → false 시 `v4_trade_schedules`에서 `card_source='go100'` AND `strategy_id=card_id` 행 `is_active=false` (이미 반영됨)

---

## 5. 배포·검증 안내

1. **DB 마이그레이션 (서버에서 실행)**  
   ```bash
   PGPASSWORD='KisAuto2026!Secure' psql -U kis_admin -d kisautotrade -f /root/kis-autotrade-v4/backend/migrations/027_go100_trade_schedules_card_source.sql
   ```
2. **go100 서비스 재시작**  
   ```bash
   systemctl restart go100
   curl -s http://localhost:8002/health | python3 -m json.tool
   ```
3. **프론트 빌드**  
   - `backtest/page.tsx`의 `checkBacktestReadiness` 미정의 등 기존 TS 오류 해결 후 `npx tsc --noEmit`, `npm run build` 권장.
4. **E2E**  
   - go100 전략카드 상세 → "자동매매 시작" → 모의계좌(4) 선택 → 시작 → 상태 변경·중지 확인.

---

## 6. 참고

- 설계: [CUR-GO100-TRADE-PROCESS-REDESIGN-001-20260224](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/reports/CUR-GO100-TRADE-PROCESS-REDESIGN-001-20260224.md)
- API 명세: [API_SPEC.md](https://raw.githubusercontent.com/moongoby/project-docs/master/go100/API_SPEC.md) 섹션 8
