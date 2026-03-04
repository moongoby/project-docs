# CUR-GO100-PAPER-TRADING-AUDIT-001 — GO100 가상매매 진행 현황 점검 및 버그 수정

> 날짜: 2026-03-04
> 작업자: Claude Code
> 상태: COMPLETED

---

## [인계 확인]
직전 완료: CUR-V41-ATR-COMMANDER-ACTIVATE-001
현재 단계: GO100 가상매매 운영 점검
CEO 지시 적용: D-001, D-007
strategy_cards: 42 (GO100)
open_positions: 5 (GO100 포트폴리오)

---

## 1. 작업 배경

사용자 요청: GO100 가상매매 진행 현황 전수 확인, 문제 있는 것 조치

---

## 2. 가상매매 포트폴리오 현황 (2026-03-04 11:35 KST 기준)

| portfolio_id | 카드 | 구분 | 초기자본 | 현금 | OPEN포지션 | 마지막실행 |
|---|---|---|---|---|---|---|
| **#9** | `[스캘핑] 거래량돌파 Phase A-2` (card_id=25) | 실거래(DRY-RUN) | 1,000만 | 100.1만 | 4개 | 2026-03-04 |
| **#6** | `[단기스윙] 섹터모멘텀 외국인수급` (card_id=15) | 페이퍼 | 1,000만 | 800.3만 | 1개 | None |
| **#8** | `[데일리] 대형 우량주 수급` (card_id=14) | 페이퍼 | 500만 | 500만 | 0개 | None |
| **#7** | `[스캘핑] 분봉 스캘핑 고변동` (card_id=13) | 페이퍼 | 1억 | 1억 | 0개 | None |

### 오픈 포지션 상세

| portfolio_id | 종목코드 | 종목명 | 수량 | 진입가 | 진입일 |
|---|---|---|---|---|---|
| #9 | 027360 | 아주IB투자 | 425 | 5,880 | 2026-03-04 |
| #9 | 028670 | 팬오션 | 421 | 5,930 | 2026-03-04 |
| #9 | 0080G0 | 0080G0 | 164 | 15,155 | 2026-03-04 |
| #9 | 307750 | 국전약품 | 321 | 4,725 | 2026-03-04 |
| #6 | 000430 | 대원강업 | 465 | 4,295 | 2026-02-25 (7일 경과) |

---

## 3. 발견된 이슈 (4건)

### 이슈 1 — `run_paper_trading.sh` ImportError (심각도: HIGH)
- **위치**: `scripts/go100/run_paper_trading.sh`
- **증상**: 크론(16:10) 매일 실행 시 `paper_trading 미발견 — 스킵` 출력 후 종료
- **원인**: `from backend.app.services.go100.paper_trading import run_daily_paper_trading` → `run_daily_paper_trading`이 `__init__.py`에 없음 (ImportError)
- **결과**: 페이퍼 포트폴리오 크론 실행이 매일 완전 실패
- **조치**: `.venv/bin/python backend/app/services/go100/scheduler/go100_scheduler.py paper` 직접 호출로 변경 ✅

### 이슈 2 — `phase2_data_scheduler` boolean 타입 오류 (심각도: MEDIUM)
- **위치**: `backend/app/services/data/trade_strength_history_collector.py:25`
- **증상**: `Phase2 trade_strength_history: operator does not exist: boolean = integer` WARNING 매 1분 반복
- **원인**: `WHERE is_active = 1` → PostgreSQL boolean 컬럼에 integer 비교 오류
- **조치**: `WHERE is_active = TRUE` 수정 ✅

### 이슈 3 — paper_engine `last_run_date` 미업데이트 (심각도: MEDIUM)
- **위치**: `backend/app/services/go100/paper_trading/paper_engine.py:_update_portfolio_eval()`
- **증상**: 페이퍼 포트폴리오 실행 후 `go100_portfolios.last_run_date`가 항상 `NULL`
- **원인**: `_update_portfolio_eval()` SQL에 `last_run_date` 갱신 누락 (live_engine.py에는 있지만 paper_engine.py에는 없었음)
- **조치**: `last_run_date = now()::date` 추가 ✅

### 이슈 4 — Portfolio #7 `account_id=NULL` (심각도: LOW)
- **위치**: `go100_portfolios.portfolio_id=7` (user_id=2, card_id=13)
- **증상**: 계좌 연결 없이 ACTIVE 상태, 실행 시 오류 가능성
- **조치**: 사용자(user_id=2)가 계좌를 수동 연결해야 함 (운영 조치 대기)

---

## 4. 수정된 파일 (3개)

```
backend/app/services/data/trade_strength_history_collector.py
  └ is_active = 1 → is_active = TRUE

backend/app/services/go100/paper_trading/paper_engine.py
  └ _update_portfolio_eval(): last_run_date = now()::date 추가

scripts/go100/run_paper_trading.sh
  └ ImportError 스크립트 → go100_scheduler.py paper 직접 호출로 교체
```

---

## 5. 추가 확인 사항 (조치 불필요 — 현황 파악)

### Portfolio #9 dry_run=True
- `go100-scheduler@live.service`가 `_main_live(dry_run=True)` 하드코딩으로 실행
- 오늘 09:10 4종목 매수 신호가 **DRY-RUN**으로만 처리됨 (실제 주문 미발생)
- `go100_scheduler.py` 코드: `asyncio.run(_main_live(dry_run=True))` — 설계 의도인지 CEO 확인 필요

### 카드 #42, #43 PAPER_LIVE 상태
- `[D6] 상한가→갭 모멘텀` (card_id=42), `[D7] 종가배팅 트레일링` (card_id=43) → `card_status=PAPER_LIVE`
- `go100_portfolios`에 연결 레코드 없음 → 스케줄러가 실행하지 않음
- 포트폴리오 생성 필요 (운영 조치 대기)

### 페이퍼 포트폴리오 일일 실행 스케줄
- 18:00 KST `go100-scheduler@paper.timer` → portfolio #6, #7, #8 처리 예정
- 16:10 크론 `run_paper_trading.sh` → 이번 수정으로 정상 실행 예정

### OHLCV 데이터
- 최신: 20260303 (어제), 오늘 자 미수집 → 16:00 `collect_ohlcv_daily.py` 이후 수집 예정
- Portfolio #9 포지션들 `current_price=NULL` 상태는 정상 (OHLCV 미수집으로 인한 것, 당일 종가 집계 후 자동 업데이트)

---

## 6. 체크포인트

- [x] 코드 수정 완료 (3개 파일)
- [ ] project-docs 보고서 push
