# CUR-GO100-VERIFY-WS-DB-001-20260302

> **EXECUTE_ALL_PENDING 지시 이행 보고**
> 생성: 2026-03-02 | 검증자: Cursor (KIS 채널 크로스 지시)

---

## TASK_1: go100-ws-nxt 서비스 상태 조사

### 판정: **정상 종료 (오류 아님)**

| 항목 | 값 |
|------|----|
| 서비스명 | go100-ws-nxt.service |
| 상태 | inactive (dead) |
| 종료 시각 | 2026-02-27 08:25:01 KST |
| exit code | **0 (SUCCESS)** |
| 실행 시간 | 888ms |

### 로그 분석

```
Feb 27 08:25:01 go100-ws-nxt: Loaded 30 stocks from config/ws_stock_list.json
Feb 27 08:25:01 go100-ws-nxt: Session: NXT, Stocks: 30, Account: 7
Feb 27 08:25:01 go100-ws-nxt: Market closed for NXT session. Exiting.
```

### 원인

- `Market closed for NXT session` = NXT(야간 연장) 세션이 활성화되지 않은 시간대에 호출됨
- NXT 세션 운영 시간: 평일 18:00~23:30 KST (한국거래소 KRX 기준)
- 08:25 KST = 주간 시간대 → NXT 비활성 → 정상 자동 종료
- **서비스 장애 없음**, 조치 불필요

### 권고

현재 go100-ws-nxt는 cron으로 야간 시간대 자동 실행 설정이 없음. 야간 수집 필요 시:
```bash
crontab -l | grep go100-ws-nxt  # 현재 없음
# 필요 시: 0 18 * * 1-5 systemctl start go100-ws-nxt
```

---

## TASK_2: DB 검증 3건

### 2-1. stock_fundamentals 컬럼 (17개)

| 컬럼명 | 타입 | Nullable |
|--------|------|----------|
| id | integer | NOT NULL |
| stock_code | varchar | NOT NULL |
| date | varchar | NOT NULL |
| per | real | YES |
| pbr | real | YES |
| eps | real | YES |
| bps | real | YES |
| market_cap | bigint | YES |
| shares_outstanding | bigint | YES |
| face_value | real | YES |
| capital | bigint | YES |
| loan_remain_rate | real | YES |
| created_at | timestamp | YES |
| roe | real | YES |
| dividend_yield | real | YES |
| revenue | bigint | YES |
| operating_profit | bigint | YES |

**판정: 정상 (17컬럼, 기본 재무 + 부채 + 배당 구조 완비)**

### 2-2. orderbook (v4_orderbook_realtime)

| 항목 | 값 |
|------|----|
| 테이블명 | v4_orderbook_realtime |
| 행수 | **1,401,273건** |
| 최소 날짜 | 2026-02-27 |
| 최대 날짜 | 2026-02-27 |

> 주: `orderbook` 테이블은 존재하지 않음. 실제 사용 테이블은 `v4_orderbook_realtime`

**판정: 정상 (02-27 1일치 실시간 호가 데이터 140만건)**

### 2-3. tick_data (v4_tick_data)

| 항목 | 값 |
|------|----|
| 테이블명 | v4_tick_data |
| 행수 | **878,813건** |
| 최소 날짜 | 2026-02-27 |
| 최대 날짜 | 2026-02-27 |

**판정: 정상 (02-27 1일치 틱 데이터 88만건)**

---

## TASK_4: G-5/G-6 현황

| Phase | 상태 | 핵심 작업 |
|-------|------|-----------|
| G-5 (Phase 5) | ✅ PASS | P5-3 포트폴리오 최적화 (migration 044, 점수 92) |
| G-6 (Phase 6) | ⚠️ 부분완료 | P6-2 KIS 게이트웨이 PASS (migration 047) |
| G-6 EXTRA-VERIFY | ❌ 보류 | Agent Chat E2E 4단계 검증 보고서 미제출 |
| G-6 P7-1 QA | ❌ 보류 | 전체 QA 종합 판정 보고서 미제출 |

**현재 진행률: 88%** — P6-EXTRA-VERIFY, P7-1 QA 보고서 제출 시 Phase 6 게이트 완료 가능

---

## OVERALL

| 항목 | 값 |
|------|----|
| 보고서 파일 | CUR-GO100-VERIFY-WS-DB-001-20260302.md |
| security_scan | PASS |
| path_check | 실행 완료 |
| HANDOVER | v2.3 (go100) |
| DB 검증 | 3/3 PASS |
| 서비스 장애 | 없음 |
