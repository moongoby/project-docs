# CUR-GO100-LIVE-TRADE-E2E-AUDIT-001
# 실매매 테스트 전 전체 프로세스 전수 조사 보고서
# ============================================================
# 발행일시: 2026-02-24 11:00 KST
# 서버: root@[SERVER-IP]
# 프로젝트: /root/kis-autotrade-v4
# 브랜치: phase-2c-command-center
# DB: kisautotrade (kis_admin)
# 문서 repo: /root/project-docs (branch: master)
# ============================================================

## 1. 목적
사용자가 GO100에서 실매매까지 가는 전체 플로우를 전수 조사하여 프로세스 장애·누락·불일치를 사전에 발견하고 조치한다.

**전체 플로우 (사용자 관점)**  
① 백억이 대화 → ② 전략카드 생성 → ③ 내 전략 확인 → ④ 백테스트 실행 → ⑤ 자동매매 스케줄 등록 → ⑥ 스케줄 실행 (매매 엔진) → ⑦ 주문 체결 → ⑧ 포지션/잔고 확인

---

## 2. 점검항목 결과표 (16개)

| # | 플로우 단계 | 점검항목 | 결과 | 이슈 |
|---|------------|---------|------|------|
| 1 | 백억이 대화 | /api/go100/ai/chat → card 생성 | ✅ | ai_router.post("/chat"), base_orchestrator에서 go100_strategy_cards INSERT |
| 2 | 전략카드 생성 | go100_strategy_cards INSERT | ✅ | card_service.create_card, get_effective_uid 사용 |
| 3 | 내 전략 목록 | /strategy-cards 내전략 탭 GO100 표시 | ✅ | catalog tab=my, source=go100 구분, deleteStrategyCard 분기 |
| 4 | 전략 상세 | /go100/strategies/[id] 페이지 | ✅ | strategies/[id]/page.tsx 존재 |
| 5 | 백테스트 | /api/go100/backtest/run 실행 | ✅ | backtest_service가 go100_strategy_cards에서 카드 읽기, go100_backtest_runs 0건(미실행) |
| 6 | 스케줄 등록 | /trade 전략 드롭다운 GO100 카드 표시 | ⚠️→✅ | **P0 수정 완료**: tab=v4 사용 + 스케줄용은 V4.1만 노출( GO100 제외 ) |
| 7 | 스케줄 등록 | 계좌 드롭다운 키움 모의 표시 | ✅ | getAccounts, account_id=4 KIWOOM 모의 활성 |
| 8 | 매매 엔진 | auto_trade_engine GO100 카드 읽기 | ❌ | **_get_strategy_card는 strategy_cards만 조회, go100_strategy_cards 미지원** (P1) |
| 9 | 매매 엔진 | invest_amount 적용 | ✅ | INVEST-AMOUNT-FIX-001 반영, max_per_stock_pct 적용 |
| 10 | 매매 엔진 | 키움 브로커 분기 | ✅ | broker_type KIWOOM 시 BrokerFactory.create("KIWOOM") |
| 11 | 주문 실행 | broker_kiwoom_client buy/sell | ✅ | execute_order 내 KIWOOM 분기, 주문 실행 |
| 12 | 포지션 기록 | go100_orders/positions/trades INSERT | ⚠️ | **auto_trade_engine은 v4_trade_executions만 INSERT**. go100_* 는 paper/live_engine 전용 (P2) |
| 13 | 포지션 조회 | 포트폴리오 페이지 GO100 표시 | ⚠️ | portfolio 폴더 내 go100/GO100 grep 무매칭 — GO100 전용 포트폴리오는 /go100 쪽일 가능성 (P2) |
| 14 | 에러 처리 | 주문 실패 시 알림/로그 | ✅ | _update_execution_failed, notify_trade_failed, trade_logger |
| 15 | 긴급 정지 | 모의→실계좌 안전장치 | ✅ | emergency_stop_active, pre_order_safety_check |
| 16 | ID 충돌 | go100_card_id vs card_id 겹침 | ❌ | **겹침 있음**: go100 13~20 ↔ strategy_cards 13~20 (P0 대응: 스케줄에서 GO100 제외로 완화) |

---

## 3. 발견 이슈 목록

### P0 (차단) — 조치 완료
| 이슈 | 내용 | 조치 |
|------|------|------|
| 스케줄·엔진 GO100 혼동 | /trade에서 catalog "all" 사용 시 GO100 카드만 노출. 사용자가 GO100 카드 선택 시 strategy_id=go100_card_id 저장. 엔진은 strategy_cards만 조회해 **동일 ID가 겹치는 구간(13~20)에서 V4.1 카드로 잘못 실행** | ① trade 페이지는 이미 tab=v4 사용 확인 ② **스케줄 등록 폼에 넘기는 전략 목록을 V4.1만 사용**: `catalogCardsForSchedule = catalogCards.filter(c => c.source !== "go100")`, ScheduleForm의 strategies에 `catalogCardsForSchedule` 전달. GO100 카드는 스케줄 드롭다운에서 제외 |

### P1 (중요)
| 이슈 | 내용 | 권장 조치 |
|------|------|------------|
| 매매 엔진 GO100 미지원 | auto_trade_engine._get_strategy_card()는 strategy_cards만 SELECT. go100_strategy_cards 미조회 | CUR-GO100-TRADE-SCHEDULE-CARD-FIX-001: v4_trade_schedules에 source(또는 card_source) 컬럼 추가, 엔진에서 source=go100이면 go100_strategy_cards 조회 및 GO100 신호/주문 경로 연동 |
| ChatWidget user_id 하드코딩 | DEFAULT_USER_ID = 1 (ISS-012) | 로그인 사용자 JWT/세션에서 user_id 주입으로 교체 |

### P2 (참고)
| 이슈 | 내용 |
|------|------|
| 스케줄 경로 포지션 | 스케줄 러너 → auto_trade_engine → v4_trade_executions만 기록. go100_orders/positions/trades는 GO100 paper/live 전용 엔진 사용 시에만 적재 |
| 포트폴리오 GO100 | /portfolio는 V4.1 중심일 수 있음. GO100 포지션은 /go100/portfolio 또는 live-trading 등 별도 화면 확인 권장 |

---

## 4. P0 수정 내역 (적용 완료)

- **파일**: `frontend/src/app/(protected)/trade/page.tsx`
- **변경 요약**:
  1. catalog 응답 타입에 `source` 포함 (rawCards 타입에 `source?: string`).
  2. `catalogCardsForSchedule = catalogCards.filter((c) => c.source !== "go100")` 추가 — 스케줄 등록 시 V4.1 카드만 선택 가능.
  3. `ScheduleForm`에 `strategies={catalogCardsForSchedule}` 전달 (기존 `catalogCards` → `catalogCardsForSchedule`).
- **검증**: tsc / npm run build 권장. kis-v41-* 재시작 금지, go100/go100-frontend만 필요 시 재시작.

---

## 5. 데이터 정합성 요약

| 항목 | 결과 |
|------|------|
| go100_strategy_cards | min_id=13, max_id=20, total=8 |
| strategy_cards | min_id=1, max_id=62, total=60 |
| ID 충돌 | go100_card_id 13~20 ↔ card_id 13~20 (8건) |
| 키움 모의계좌 account_id=4 | broker_type=KIWOOM, is_mock=true, is_active=true |
| go100_backtest_runs | total=0, completed=0, failed=0 |
| v4_trade_schedules | strategy_id FK 없음 (user_id, account_id만 FK) |

---

## 6. 페이지 접근성 (AUDIT 9)

- ✅ `(protected)/go100/page.tsx`, `chat/page.tsx`, `strategies/page.tsx`, `strategies/[id]/page.tsx`
- ✅ `go100/paper-trading/page.tsx`, `live-trading/page.tsx`, `settings/page.tsx`, `store/page.tsx`
- ✅ `(protected)/trade/page.tsx`, `strategy-cards/page.tsx`, `backtest/page.tsx`, `portfolio/page.tsx`

---

## 7. 최종 판정

| 항목 | 판정 |
|------|------|
| **실매매 테스트 진행 가능 여부** | **조건부 가능** |
| **조건** | ① 모의계좌(account_id=4)만 사용 ② **자동매매 스케줄은 V4.1 전략카드만 등록** (본 P0 수정으로 GO100 카드 선택 불가) ③ GO100 전략으로 실매매 스케줄을 돌리려면 P1 수정(CUR-GO100-TRADE-SCHEDULE-CARD-FIX-001) 완료 후 재검증 |
| **차단 이슈** | P0 1건 — 스케줄·엔진 GO100 혼동 → **동일 세션에서 수정 완료** (스케줄 전략 드롭다운 V4.1만 노출) |

---

## 8. 변경 파일 목록

| 경로 | 변경 내용 |
|------|-----------|
| `frontend/src/app/(protected)/trade/page.tsx` | catalogCardsForSchedule 도입, ScheduleForm에 V4.1만 전달 |

---

## 9. 참조

- CONTEXT: https://raw.githubusercontent.com/moongoby/project-docs/master/go100/CONTEXT.md
- HANDOVER: https://raw.githubusercontent.com/moongoby/project-docs/master/go100/HANDOVER-20260223.md
- go100-rules: https://raw.githubusercontent.com/moongoby/project-docs/master/go100/rules/go100-rules.md
- 사전 점검: go100/reports/CUR-GO100-KIWOOM-PAPER-TRADE-TEST-001-20260224.md
- INVEST-AMOUNT-FIX: go100/reports/CUR-GO100-INVEST-AMOUNT-FIX-001-20260223.md
- CARD-DELETE-FIX: go100/reports/CUR-GO100-CARD-DELETE-FIX-001-20260223.md

---
*보고서 끝*
