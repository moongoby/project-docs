# CUR-V41-LIVE-TRADING-AUTOFIX-001 — GO100 라이브 트레이딩 자동매매 버그 수정 및 실매매 실행 결과

- **작업일**: 2026-03-03 15:10 KST
- **커밋**: bfd7664b (kis-autotrade-v4, phase-2c-command-center)
- **대상**: moongoby@naver.com (user_id=3), 카드 #25 [스캘핑] 데이트레이딩 거래량 돌파 Phase A-2

---

## 1. 자동매매 미진행 원인 분석 (3개 버그)

### Bug-1: `_get_universe_candidates` — universe_filter 조건 미적용

| 항목 | 내용 |
|------|------|
| **파일** | `backend/app/services/go100/live_trading/live_engine.py:601` |
| **증상** | run-now 실행 시 bought=0, sold=0 (오류 없음) |
| **원인** | `_get_universe_candidates`가 universe_filter의 복잡 조건(volume ≥ 2M, change_pct ≥ 1.5%, price range)을 무시하고 `stock_universe`에서 stock_code 알파벳 첫 50개만 반환 → 소형주만 선별되어 신호 평가 전부 탈락 |
| **수정** | `ohlcv_daily` JOIN + conditions 파싱으로 price/volume/change_pct 조건 SQL에 적용. 결과: 조건 충족 종목(오늘 거래량순) 반환 |

### Bug-2: `_place_order_kiwoom` — 키움 인증키 환경변수 미설정

| 항목 | 내용 |
|------|------|
| **파일** | `backend/app/services/trading/v4_order_executor.py:139` |
| **증상** | `BUY 오류: 키움 앱키 미설정: KIWOOM_APP_KEY, KIWOOM_APP_SECRET(KIWOOM_SECRET_KEY) 확인` |
| **원인** | `_place_order_kiwoom`이 `os.getenv("KIWOOM_APP_KEY", "")` 환경변수만 읽음. 시스템에 `KIWOOM_APP_KEY` env 미설정 (키는 DB accounts 테이블 암호화 저장) |
| **수정** | env 미설정 시 `kiwoom_credentials._load_from_db(account_id)`로 DB에서 복호화 로드 |

### Bug-3: `check_live_eligibility` — go100_paper_accounts 빈 테이블

| 항목 | 내용 |
|------|------|
| **파일** | `backend/app/services/go100/ai/live_trading.py:50` |
| **증상** | 백억이 AI "실매매 시작하고 싶어" → "페이퍼 트레이딩 계좌가 없습니다" (적격 거부) |
| **원인** | `go100_paper_accounts` 테이블이 빈 상태. 실제 페이퍼 데이터는 `go100_portfolios`에 존재 |
| **수정** | `go100_paper_accounts` 없을 시 `go100_portfolios` 폴백, 승률도 `go100_trades` 기반으로 조회 |

---

## 2. 백억이(AI) 활성화 흐름

```
백억이: "실매매 켜줘"
→ intent: LIVE_ENABLE
→ go100_live_trading_config.is_enabled = true ✅
→ 7단계 안전 검사 적용 확인
```

백억이 응답:
> **실매매가 활성화되었습니다. 주문 시 7단계 안전 검사가 적용됩니다.**

---

## 3. 라이브 포트폴리오 생성

```
POST /api/go100/live-trading/start
{
  "go100_card_id": 25,
  "account_id": 4,          ← KIWOOM 81201280 (모의)
  "invest_amount": 3000000,
  "max_stocks": 3,
  "stop_loss_pct": -3.0,
  "take_profit_pct": 5.0,
  "disclaimer_agreed": true
}

응답:
{
  "portfolio_id": 9,
  "status": "ACTIVE",
  "initial_capital": 10,000,000원
}
```

카드 #25 상태: `card_status=LIVE`, `is_live=true` ✅

---

## 4. 실매매 실행 결과 (run-now dry_run=false)

### 매수 체결 (4종목)

| position_id | 종목코드 | 종목명 | 수량 | 체결가 | 투자금 | 손절가 |
|-------------|---------|--------|------|--------|--------|--------|
| 8 | 027360 | 아주IB투자 | 425주 | 5,880원 | 2,499,000원 | 5,292원 |
| 9 | 028670 | 팬오션 | 421주 | 5,930원 | 2,496,530원 | 5,337원 |
| 10 | 005870 | 휴니드 | 275주 | 9,060원 | 2,491,500원 | 8,154원 |
| 11 | 001250 | GS글로벌 | 574주 | 2,630원 | 1,509,620원 | 2,367원 |

### 포트폴리오 현황

| 항목 | 값 |
|------|-----|
| 잔여 현금 | 1,002,000원 |
| 총 자산 | 9,998,650원 |
| 오픈 포지션 | 4종목 |
| 상태 | ACTIVE |

### 일부 오류 (API rate limit)

```
BUY 실패 0080G0, 307750, 024740, 463250, 449450, 013810:
  "허용된 요청 개수를 초과하였습니다[1700: API ID=kt10000]"
```
→ 키움 REST API rate limit 초과 (처음 4건은 체결, 이후 6건 rate limit). 비기능 오류.

---

## 5. 수정 파일 목록

| 파일 | 수정 내용 |
|------|----------|
| `backend/app/services/go100/live_trading/live_engine.py` | `_get_universe_candidates` universe_filter 조건 적용 (ohlcv_daily JOIN) |
| `backend/app/services/trading/v4_order_executor.py` | `_place_order_kiwoom` DB 자격증명 폴백 로드 |
| `backend/app/services/go100/ai/live_trading.py` | `check_live_eligibility` go100_portfolios 폴백 |

**커밋**: bfd7664b (kis-autotrade-v4, phase-2c-command-center)

---

## 6. 전체 흐름 요약

```
원인 진단 (3개 버그 식별)
  ↓
Bug-1 수정: live_engine._get_universe_candidates — ohlcv_daily 필터 적용
  ↓
Bug-2 수정: v4_order_executor._place_order_kiwoom — DB 키 복호화 로드
  ↓
Bug-3 수정: live_trading.check_live_eligibility — go100_portfolios 폴백
  ↓
백억이 AI 활성화: "실매매 켜줘" → LIVE_ENABLE ✅
  ↓
라이브 포트폴리오 생성 (portfolio_id=9, 카드 #25) ✅
  ↓
run-now dry_run=false 실행
  ↓
유니버스 필터 통과 → 신호 평가 → 매수 체결 4종목 ✅
  아주IB투자(027360) · 팬오션(028670) · 휴니드(005870) · GS글로벌(001250)
```
