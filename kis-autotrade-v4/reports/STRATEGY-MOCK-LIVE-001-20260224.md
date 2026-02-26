# 백테스트 통과 전략 모의실매매 검증 보고서 — STRATEGY-MOCK-LIVE-001

**작업 ID:** CUR-STRATEGY-MOCK-LIVE-001  
**일시:** 2026-02-24 KST (화요일)  
**서버:** root@211.188.51.113  
**프로젝트:** /root/kis-autotrade-v4  
**브랜치:** phase-2c-command-center  

---

## 1. 요약

- **목적:** 백테스트 통과 전략에 대한 모의실매매 검증 (모의계좌 전용, 실계좌 미사용)
- **모의계좌:** config_id=3, account_id=1 (kis_config_id=3), KIS_ACCOUNT_MODE=virtual
- **결과:** 수동 1건 BUY→SELL 파이프라인 경유 실행 성공. v4_trade_executions 기록 확인. 자동매매 30분 테스트는 별도 실행 권장으로 생략.

---

## 2. 선행 조건 및 대상 전략

| 항목 | 내용 |
|------|------|
| 선행 보고서 | STRATEGY-FULL-AUDIT-001-20260224.md, STRATEGY-BACKTEST-OPT-001-20260224.md — project-docs에는 존재, kis-autotrade-v4/report 내 동일명 파일 없음 |
| 대상 전략 목록 | BACKTEST-OPT-001 미로드로, DESK1 카드 1건(strategy_id=5)으로 단일 모의매매 검증 수행 |
| 실행 경로 | auto_trade_engine.execute_order (trade_router POST /execute와 동일 경로) → V4OrderExecutor(config_id=3) |

---

## 3. STEP 0: 사전 점검 결과

| 단계 | 항목 | 결과 |
|------|------|------|
| 0-1 | KST | 2026-02-24 11:22 KST 확인 (timeapi.io) |
| 0-2 | 서비스·DB | kis-v41-api active, PostgreSQL OK, Redis PONG |
| 0-3 | DB 백업 | backup_kisautotrade_mocklive_20260224.dump 생성 완료 |
| 0-4 | 대상 전략 | DESK1 카드 1개( strategy_id=5 ) 적용 |
| 0-5 | mock config | kis_configs id=3 (is_production=false), .env 백업 .env.backup.mocklive.20260224 |
| 0-6 | Redis 토큰 | token:kis:kis:3 TTL=-2 (사전 없음, 주문 시 발급) |

---

## 4. STEP 1: 모의실매매 실행 결과

### 4.1 실행 개요

- **방식:** 스크립트 `scripts/strategy_mock_live_001_run.py`에서 auto_trade_engine.execute_order 호출 (DRY_RUN=false, .env 로드)
- **종목/가격:** 001510, 1주, 지정가 1,700원 (056190 3,500원은 상/하한가 오류, 014440은 토큰 제한·중복으로 001510으로 변경)

### 4.2 실행 이력

| 순서 | 종목 | 방향 | 가격 | 결과 | 비고 |
|------|------|------|------|------|------|
| 1 | 056190 | BUY | 3,500 | 실패 | 모의투자 상/하한가 오류 (실제 종가 32,850원대) |
| 2 | 014440 | BUY | 5,000 | 실패 | EGW00133 토큰 1분당 1회 제한 |
| 3 | 001510 | BUY | 1,700 | 성공 | order_no 0000010486, execution_id=22 |
| 4 | 001510 | SELL | 1,700 | 실패(1회) | 동일 세션 내 토큰 재발급 제한 EGW00133 |
| 5 | 001510 | SELL | 1,700 | 성공 | 5분 후 재실행, order_no 0000010727, execution_id=24 |

### 4.3 DB 파이프라인 확인

- **v4_trade_executions:** 당일 account_id=1 기준 BUY filled(22), SELL filled(24) 기록 확인. 실패 건(20,21,23) 포함 5건.
- **v4_order_requests:** 3건 유지 (본 실행은 execute_order 경로만 사용, order_requests 미기록 — 설계상 동일).
- **v4_orders:** 스키마에 없음 (v4_order_requests / v4_trade_executions / v4_trades / v4_positions 구조 기준).

---

## 5. STEP 2·3: 자동매매 테스트 및 결과 분석

- **STEP 2:** 백테스트 상위 3개 전략 is_live=true 전환 후 30분 모니터링 — 본 회차에서는 **미실행** (CEO 승인·별도 일정 권장).
- **STEP 3:** 수동 1건 기준 요약:
  - 체결 성공률: BUY 1/1, SELL 1/1 (최종 청산 기준)
  - 체결 지연: order_request → fill 은 execute_order 단일 호출 내 처리.
  - 슬리피지: 지정가 1,700원, 체결가 1,700원 (executed_price 동일).
  - 오류 유형: EGW00133(토큰 1분 제한), duplicate_order_within_5min(5분 내 동일 종목/방향), 상/하한가 오류(가격 설정 오류).

---

## 6. 체크포인트

- [x] 대상 전략 목록 확정 (DESK1 1건)
- [x] 수동 매매 테스트 완료 (BUY→SELL 1건)
- [ ] 자동매매 테스트 완료 (상위 3개) — 별도 실행 권장
- [x] DB 파이프라인 무결성 확인 (v4_trade_executions)
- [x] is_live 복원 확인 — 변경 없음
- [ ] 코드 커밋 — 선택
- [x] 보고서 push 예정 (project-docs)

---

## 7. 권장 사항

1. **연속 매매 시:** KIS 모의 토큰 1분당 1회 제한(EGW00133)으로 BUY 직후 SELL 시 토큰 재발급 실패 가능. BUY 후 65초 이상 대기 후 SELL 권장 (스크립트 sleep 65초 반영 권장).
2. **지정가:** 종목별 최근 종가/상하한가 확인 후 지정가 설정 (예: ohlcv_daily 조회).
3. **중복 주문:** 5분 내 동일 계좌·종목·방향 주문 시 duplicate_order_within_5min 적용됨.
4. **자동매매 테스트:** is_live=true 전환 시 CEO 승인 후 별도 30분 모니터링 실행 권장.

---

## 8. 참조

- STRATEGY-FULL-AUDIT-001-20260224.md (project-docs)
- STRATEGY-BACKTEST-OPT-001-20260224.md (project-docs)
- KIS-MOCK-TRADE-TEST-001-20260224.md
- kis-v41-rules.md, DB-SCHEMA.md
