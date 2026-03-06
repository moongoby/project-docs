# [GO100] CUR-GO100-PAPER-TRADE-STATUS-001 — 모의투자 세션 상태 점검 보고서

**Task ID**: T-012
**작성일**: 2026-03-05
**작성자**: claudebot (자동 점검)
**목적**: 현재 ACTIVE 모의투자 세션 상태, 오늘 거래 발생 여부, 크론 실행 이력 정밀 점검

---

## 1. ACTIVE 세션 현황

| 항목 | 값 |
|------|----|
| session_id | 2 |
| user_id | 2 |
| strategy_card_id | 35 |
| strategy_name | [시드] 스캘핑 기본 |
| start_date | 2026-02-27 |
| end_date | 2026-03-29 |
| status | **ACTIVE** |
| initial_capital | 10,000,000원 |
| current_capital | 10,000,000원 (변동 없음) |
| total_trades | 0 |
| win_rate | NULL |
| total_return | NULL |

**전체 세션 목록**:
- session_id=1: CANCELLED (2026-02-27 ~ 2026-03-29, 거래 0건)
- session_id=2: **ACTIVE** (2026-02-27 ~ 2026-03-29, 거래 0건)

---

## 2. 오늘 거래 발생 여부 (2026-03-05)

| 항목 | 값 |
|------|----|
| 오늘 거래 건수 (cnt) | **0** |
| 마지막 거래 시각 (last_trade) | **NULL** |
| 전체 누적 거래 건수 | **0** |

**결론**: 세션 시작(2026-02-27) 이후 6일간 **거래 전무**.

---

## 3. 전략 카드 상세 (ID=35)

| 항목 | 내용 |
|------|------|
| strategy_name | [시드] 스캘핑 기본 |
| universe_filter | {} (필터 없음) |
| entry_type | market |
| entry_conditions | golden_cross(fast=5, slow=20) AND volume_surge(period=20, threshold=2.0) |
| position_size | 0.1 (자본의 10%) |
| stop_loss | -3% |
| take_profit | +7% |
| trailing_stop | 5% |
| max_holding_days | 10일 |
| max_stocks | 5 |

---

## 4. 크론 설정 확인

등록된 paper trading 관련 cron:

```
# [GO100 DIR-PT-V3] 30일 모의투자 V3 Brain 매수 — 09:10 KST (00:10 UTC) 평일
10 0 * * 1-5  /root/kis-autotrade-v4/venv/bin/python3 \
  /root/kis-autotrade-v4/scripts/go100/run_paper_trading_v3.py --mode buy \
  >> /root/kis-autotrade-v4/logs/paper_trading_v3_buy.log 2>&1

# [GO100 DIR-PT-V3] 30일 모의투자 V3 Brain 매도 — 15:15 KST (06:15 UTC) 평일
15 6 * * 1-5  cd /root/kis-autotrade-v4 && .venv/bin/python3 \
  scripts/go100/run_paper_trading_v3.py --mode sell \
  >> /root/kis-autotrade-v4/logs/paper_trading_v3_sell.log 2>&1

# [GO100 DIR-PT-V3] 주간 리뷰 — 금 16:30 KST (07:30 UTC)
30 7 * * 5    cd /root/kis-autotrade-v4 && .venv/bin/python3 \
  scripts/go100/run_paper_trading_v3.py --mode weekly_review \
  >> /root/kis-autotrade-v4/logs/paper_trading_v3_review.log 2>&1
```

**상태**: cron 등록 정상. 매수(09:10 KST), 매도(15:15 KST) 평일 실행 설정.

---

## 5. 로그 분석 (2026-03-05)

### 5-1. /var/log/go100/paper_trading.log (오늘 실행 이력)

```
2026-03-05 16:10:04  BEGIN - session_id=2 조회 시작
2026-03-05 16:10:04  go100_paper_trading_sessions WHERE session_id=2 → OK
2026-03-05 16:10:04  go100_strategy_cards WHERE go100_card_id=35 → OK
2026-03-05 16:10:04  SELECT MAX(date) FROM ohlcv_daily → OK
2026-03-05 16:10:05  go100_paper_trades WHERE session_id=2 → 0건
2026-03-05 16:10:05  ohlcv_daily WHERE date >= '20251105' AND date <= '20260305' → 조회
2026-03-05 16:13:15  stock_universe WHERE market='KOSPI' LIMIT 80 → 조회
2026-03-05 16:13:15  ROLLBACK
run_paper_trading_daily error: 'stock_code'   ← ⚠️ 버그 발생
```

### 5-2. /var/log/go100/paper.log (go100 scheduler 결과)

```
INFO: GO100 SCHEDULER: 페이퍼 pid=8 bought=0 sold=0
INFO: PAPER 스케줄 완료:
  portfolios_ran: 3
  results:
    - card not found (portfolio 1)
    - bought=0, sold=0, cash=9,754,477 (portfolio 2)
    - bought=0, sold=0, cash=5,000,000 (portfolio 3)
  errors: []
```

---

## 6. 임포트 검증 결과

```python
# 지시서 명령:
from backend.app.services.go100.paper_trading_engine_30d import PaperTradingEngine30D
```

**결과**: ❌ ImportError — `PaperTradingEngine30D` 존재하지 않음.

**실제 클래스명**: `PaperTradingEngine30d` (소문자 d)

```python
from backend.app.services.go100.paper_trading_engine_30d import PaperTradingEngine30d
# → ✅ IMPORT OK
```

---

## 7. 발견된 이슈 요약

| 번호 | 유형 | 내용 | 영향도 |
|------|------|------|--------|
| I-01 | 버그 | `run_paper_trading_daily error: 'stock_code'` | 🔴 HIGH — 매수 시도 시 오류로 실패 |
| I-02 | 불일치 | 클래스명 `PaperTradingEngine30D` vs 실제 `PaperTradingEngine30d` | 🟡 MEDIUM — 지시서 오타, 실제 코드는 문제없음 |
| I-03 | 상태 | 세션 시작 6일 경과, 누적 거래 0건 | 🔴 HIGH — 30일 사이클에 거래 미발생 |
| I-04 | 상태 | session_id=1 CANCELLED 상태 (이유 불명) | 🟡 MEDIUM — 이력 확인 필요 |

---

## 8. 진단 및 권고

### 핵심 문제
`run_paper_trading_engine_30d.py` 내 `run_daily_check()` 함수에서 ohlcv_daily 데이터를 처리할 때 `'stock_code'` 키를 접근하려 했으나 딕셔너리/레코드 구조 불일치로 KeyError 발생.

- stock_universe 조회 결과에서 `stock_code` 컬럼명 vs 실제 반환 키 불일치 가능성
- asyncpg Record vs dict 변환 누락 가능성

### 권고 조치
1. `paper_trading_engine_30d.py` 내 `'stock_code'` 접근 부분 디버깅
2. asyncpg Record 객체를 dict로 변환하거나 정확한 키 확인
3. 세션 거래 미발생 상태이므로 다음 평일 09:10 KST 매수 크론 실행 전 버그 수정 필요

---

## 9. 저장 정보 블록 (PATH-001 §4-8)

```
REPORT_PATH: /root/project-docs/go100/reports/CUR-GO100-PAPER-TRADE-STATUS-001-20260305.md
LOCAL_PATH:  /root/kis-autotrade-v4/report/go100/CUR-GO100-PAPER-TRADE-STATUS-001-20260305.md
TASK_ID:     T-012
DATE:        2026-03-05
PROJECT:     GO100
STATUS:      점검 완료
```
