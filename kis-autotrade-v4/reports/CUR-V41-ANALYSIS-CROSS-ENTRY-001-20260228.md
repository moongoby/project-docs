# CUR-V41-ANALYSIS-CROSS-ENTRY-001-20260228

**작업 ID:** CODE-ANALYSIS-CROSS-ENTRY-001  
**작업명:** 교차종목 진입/자본 라우팅 현재 코드 구조 분석 및 갭 리포트  
**우선순위:** P1  
**분석일:** 2026-02-28  
**분석 유형:** 읽기 전용 (코드/DB/서비스 변경 없음)

---

## 1. 목적

R17 교차종목 릴레이(A종목 익절 → B종목 진입, 5~7종목 동시 모니터링, 진폭우선 우선순위, +370% 연구 결과 반영) 구현에 필요한 코드 변경 범위를 정확히 파악하기 위한 갭 분석.

---

## 2. 분석 대상 파일 (실제 경로)

| 구분 | 지시서 경로 | 실제 경로 |
|------|-------------|-----------|
| 핵심 1 | strategy_engine.py | `backend/app/services/strategy/strategy_engine.py` |
| 핵심 2 | order_executor.py | `backend/app/services/execution/order_executor.py` (레거시), `backend/app/services/trading/v4_order_executor.py` (V4.1) |
| 핵심 3 | position_manager.py | `backend/app/services/position/position_manager.py` (레거시 positions), 오케스트레이터는 v4_positions 직접 사용 |
| 핵심 4 | risk_manager.py | `backend/app/services/risk/risk_manager.py`, `backend/app/services/trading/v4_risk_manager.py` |
| 핵심 5 | split_transfer_engine.py | `backend/app/services/trading/split_transfer_engine.py` |
| 핵심 6 | v4_pipeline_orchestrator.py | `backend/app/services/trading/v4_pipeline_orchestrator.py` |
| 핵심 7 | fund/ | `backend/app/services/execution/fund_pool.py`, `fund_service.py`, `fund_commander.py` 등 |
| 보조 | lifecycle.py | `backend/app/services/position/lifecycle.py` (PositionManager L6) |
| 보조 | adaptive/ | `backend/app/services/adaptive/` (engine, fund_rebalancer, param_optimizer 등) |
| 보조 | live_paper_d6_d7.py | `scripts/live_paper_d6_d7.py` (프로젝트 루트 기준) |
| 보조 | main.py | `backend/app/main.py` |

---

## 3. 분석 질문별 요약 (상세는 /tmp/cross_entry_code_map.json)

| Q | 주제 | 핵심 답변 |
|---|------|-----------|
| Q1 | 전략-종목 매칭 | 1전략:N종목. `generate_signals(tickers, ...)`로 동시 다종목 시그널 생성 가능. |
| Q2 | 파이프라인 실행 | 카드/DESK 순차 처리. A종목 D2 + B종목 D5 동시 시그널은 서로 다른 카드에서 순차 처리됨. |
| Q3 | 포지션 관리 | v4_positions로 멀티종목 지원. ticker, desk_id, card_id로 종목/전략별 추적. |
| Q4 | 자본 풀 | DESK별 v4_desk_fund. 익절 시 used_amount 감소로 가용금 환원. 전용 “릴레이 풀” 없음. |
| Q5 | 익절→재투자 | 익절 금액은 DESK 가용금으로 환원되며, 다음 매수 시 다른 종목(B)에도 사용 가능하나, “즉시 B에 배정”하는 전용 경로 없음. |
| Q6 | 주문 비동기 | OrderExecutor는 async + Lock으로 매수 직렬화. 동시 2종목 주문 불가. |
| Q7 | 리스크 범위 | 종목 단위(중복/비율) + DESK 단위(가용금, 포지션 수, 일일 손실 한도) 모두 존재. |
| Q8 | live_paper_d6_d7 | D6/D7만 실행. 다종목 감시 있으나 진폭우선/교차종목 릴레이 없음. |
| Q9 | strategy_cards 매핑 | 단일 엔진이 카드 목록 순회 → `run_card_pipeline(card)` 순차 호출. |

---

## 4. 갭 분류 요약 (상세는 /tmp/cross_entry_gap_analysis.json)

| 카테고리 | 건수 | 내용 요약 |
|----------|------|-----------|
| **already_exists** | 7 | DESK별 자본 풀, 멀티종목 포지션, 분할매도 후 가용금 환원, 카드별 시그널 매수, 포지션/일일 한도, DESK 인계·split_phase, 1전략 N종목 시그널 |
| **needs_modification** | 4 | 익절→릴레이 풀 즉시 배정 경로, 5~7종목 진폭우선 정렬, 동시 다종목 시그널 통합 처리, 주문 직렬화 완화(릴레이 전용 경로) |
| **needs_new_development** | 4 | 교차종목 릴레이 전용 모듈(M), 5~7종목 동시 모니터링·스코어링(M), 진폭우선 우선순위 엔진(S), 장중 익절→재투자 이벤트(S) |

---

## 5. 산출물 위치

| 산출물 | 경로 |
|--------|------|
| 10개 질문 답변 + 코드 근거 | `/tmp/cross_entry_code_map.json` |
| 갭 3분류 (이미있음/수정/신규) | `/tmp/cross_entry_gap_analysis.json` |
| 실행 흐름 다이어그램 + [NEW]/[MOD] | `/tmp/cross_entry_architecture_diagram.txt` |

---

## 6. HANDOVER 업데이트 문구

```
| CODE-ANALYSIS-CROSS-ENTRY-001 | 02-28 | (보고서 push) | 200 | 교차종목 진입 코드 갭 분석, 이미있음7건/수정4건/신규4건 |
```

---

## 7. 주의사항

- 본 작업은 **코드 분석만** 수행함. 코드 수정, DB 변경, 서비스 재시작 없음.
- 구현 범위는 CEO 결정 후 별도 개발 지시서로 진행.
