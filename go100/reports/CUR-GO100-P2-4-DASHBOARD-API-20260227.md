# CUR-GO100-P2-4 — 대시보드 API 엔드포인트 구현

**일시:** 2026-02-27  
**작업 ID:** P2-4 (GO100 대시보드 API 연동)  
**목적:** 프론트엔드 대시보드에 필요한 REST API 4종 구현

---

## 1. 요약

- **파일:** `backend/app/routers/go100/dashboard_router.py` 확장
- **추가 엔드포인트:**  
  `GET /api/go100/dashboard/summary`, `/signals`, `/integrity`, `/experience`
- **인증:** 기존과 동일하게 `get_current_user` 의존 — 미인증 시 401

---

## 2. 엔드포인트 명세

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/go100/dashboard/summary` | 포트폴리오 요약, 전략카드 현황, 최근 시그널(거래 활동) |
| GET | `/api/go100/dashboard/signals` | 크로스마켓 시그널 최근 7일 (기본) — `go100_global_market` |
| GET | `/api/go100/dashboard/integrity` | 데이터 무결성 최근 상태 — `go100_data_integrity_log` |
| GET | `/api/go100/dashboard/experience` | 경험 로그 통계 — `go100_usage_logs` (일별 요청, 인텐트, 에러율 등) |

---

## 3. 응답 구조

### 3.1 GET /api/go100/dashboard/summary

- **portfolio_summary:** total_asset, total_return_pct, mdd_pct, goal_progress_pct, regime, regime_kr, paper_status, live_status  
- **strategy_cards:** 전략 카드별 go100_card_id, strategy_name, card_status, is_live, allocated_amount, 백테스트 지표, win_rate, total_trades  
- **recent_signals:** 최근 7일 거래 최대 10건 (type, at, side, stock_name, stock_code, quantity, price)

### 3.2 GET /api/go100/dashboard/signals

- **Query:** `days` (기본 7, 1~30)
- **응답:** `days`, `signals` (data_date, usd_krw, vix, vix_label, sp500, sp500_change_pct, nasdaq, nasdaq_change_pct, dow, dow_change_pct, us10y_yield), `count`

### 3.3 GET /api/go100/dashboard/integrity

- **Query:** `hours` (기본 24, 1~168)
- **응답:** status(HEALTHY|DEGRADED|CRITICAL|no_data|error), total_checks, passed, failed, critical_failures, last_run, checks[] (check_type, target_table, is_pass, severity, message)

### 3.4 GET /api/go100/dashboard/experience

- **Query:** `days` (기본 7, 1~90)
- **응답:** `get_usage_stats()`와 동일 — daily_requests, intent_distribution, avg_latency_ms, error_rate, total_requests

---

## 4. 수정 파일

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/routers/go100/dashboard_router.py` | `get_usage_stats` import 추가; GET `/summary`, `/signals`, `/integrity`, `/experience` 4개 핸들러 추가 |

- **summary:** 기존 `get_overview`, `get_user_portfolio`, `get_backtest_results`, `get_trade_history` 등 조합.
- **signals:** `go100_global_market` 테이블 조회 (크로스마켓 지표).
- **integrity:** `go100_data_integrity_log` 테이블에서 `check_time` 기준 최근 N시간 조회 후 집계.
- **experience:** `usage_logger.get_usage_stats(days, db)` 호출.

---

## 5. API 테스트

백엔드 재기동 후 아래로 동작 확인 가능. (미인증 시 401, 인증 시 200 및 JSON 반환)

```bash
# 인증 쿠키/헤더 없이 호출 시 401 예상
curl -s http://localhost:8002/api/go100/dashboard/summary | python3 -m json.tool
curl -s "http://localhost:8002/api/go100/dashboard/signals?days=7" | python3 -m json.tool
curl -s "http://localhost:8002/api/go100/dashboard/integrity?hours=24" | python3 -m json.tool
curl -s "http://localhost:8002/api/go100/dashboard/experience?days=7" | python3 -m json.tool
```

- **참고:** 현재 8002에서 기동 중인 서버가 수정 전 코드를 로드한 경우 새 경로는 404를 반환할 수 있음. **백엔드 재시작 후** 위 엔드포인트가 등록됨.

---

## 6. 의존성

- DB: `go100_global_market`, `go100_data_integrity_log`, `go100_usage_logs`, 기존 대시보드용 쿼리(포트폴리오, 전략 카드, 거래 이력 등)
- 서비스: `get_usage_stats` (`backend.app.services.go100.ai.usage_logger`)

---

## 7. 상태

- [x] 1단계: 대시보드 라우터 확장
- [x] 2단계: 각 엔드포인트 구현
- [ ] 3단계: API 테스트 (백엔드 재기동 후 curl/프론트 연동으로 확인 권장)
