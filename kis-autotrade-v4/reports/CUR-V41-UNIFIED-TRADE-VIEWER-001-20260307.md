# CUR-V41-UNIFIED-TRADE-VIEWER-001-20260307

**Task ID**: T-278
**제목**: CEO 통합 거래 뷰어 Phase 1 — API + 프론트엔드 + 차트
**날짜**: 2026-03-07
**커밋**: 296742a9
**작성자**: Claude Code (claudebot)

---

[인계 확인]
직전 완료: T-277 (큐 정리 + 장전 점검 + HANDOVER v10.60)
현재 단계: Phase 2c Command Center
CEO 지시 적용: D-001, D-002
strategy_cards: 60
open_positions: 0

---

## 1. 사전 확인

| 항목 | 결과 |
|------|------|
| strategy_cards 수 | 60 (기준값: 60) ✅ |
| open_positions (OPEN) | 0 (기준값: 0) ✅ |
| Redis ping | PONG ✅ |
| FastAPI 헬스체크 | HTTP 200 ✅ |

---

## 2. 구현 내용

### Step 1 — 백엔드 API (`backend/app/routers/v4_trades_unified.py`)

신규 파일 생성. 7개 엔드포인트 구현:

| 번호 | 엔드포인트 | 설명 |
|------|-----------|------|
| 1 | `GET /api/v4/trades/unified` | 전 채널(BT/MOCK/PAPER/LIVE) 통합 거래 목록 + 요약통계 |
| 2 | `GET /api/v4/trades/{trade_id}/detail` | 거래 상세 + 진입시점 스냅샷 + 종목 전 채널 이력 |
| 3 | `GET /api/v4/trades/{trade_id}/chart/minute` | 분봉 차트 + 매수/매도 마커 |
| 4 | `GET /api/v4/trades/{trade_id}/chart/daily` | 일봉 차트 + MA5/10/20/60 + BB + 보유구간 |
| 5 | `GET /api/v4/trades/stock/{stock_code}/history` | 종목 전 채널 히스토리 (채널 색상 포함) |
| 6 | `GET /api/v4/trades/hypothesis-matrix` | 가설×시나리오 피봇 매트릭스 |
| 7 | `GET /api/v4/stocks/search` | 종목명 자동완성 (한글/영문 ILIKE) |

**데이터 소스 매핑**:
- BT(백테스트): `v4_backtest_trades` WHERE trade_type='SELL'
- MOCK(가상매매): `v4_mock_trades`
- PAPER/LIVE: `v4_positions` WHERE status='CLOSED'
- 종목명: 모든 채널에 `stock_universe` LEFT JOIN (stock_name 우선)

**종목명 JOIN 방식**:
```sql
LEFT JOIN (
    SELECT DISTINCT ON (stock_code) stock_code, stock_name
    FROM stock_universe ORDER BY stock_code, collected_at DESC
) su ON su.stock_code = t.stock_code
COALESCE(su.stock_name, t.stock_code) AS display_name
```

**요약 통계 계산**: total_count, win_rate, profit_factor, avg_pnl_pct, cum_pct, mdd_pct, max_win_pct, max_loss_pct

**MA/BB 계산** (Python 서버사이드):
- MA5/10/20/60: 단순이동평균
- BB: 20일 기준, ±2σ

### Step 2 — `backend/app/main.py` 라우터 등록

```python
from backend.app.routers.v4_trades_unified import router as v4_trades_unified_router
app.include_router(v4_trades_unified_router)  # T-278
```

### Step 3 — 프론트엔드

| 파일 | 설명 |
|------|------|
| `frontend/static/trades.html` | CEO 통합 거래 뷰어 메인 페이지 |
| `frontend/static/css/trades-viewer.css` | 다크모드, 채널 뱃지, 반응형 |
| `frontend/static/js/trades-viewer.js` | 10개 JS 모듈 |

**CSS 특징**:
- 배경: `#1a1a2e` (다크), 텍스트: `#e0e0e0`
- 채널 뱃지: BT=`#4a9eff`, MOCK=`#ff9f43`, PAPER=`#2ed573`, LIVE=`#ff4757`
- WIN=`#2ed573`, LOSS=`#ff4757`
- 반응형: 1200px+ 2컬럼(목록+상세), 미만 1컬럼, 모바일 360px+ 대응

**JS 모듈 구조**:
- `TradesApp`: 메인 컨트롤러
- `FilterManager`: 필터 상태 관리, URL 쿼리스트링 동기화
- `TradeTable`: 테이블 렌더링, 페이지네이션, 행 클릭
- `SummaryCards`: 요약 카드 (8개 지표)
- `StockSearch`: 종목명 자동완성 (debounce 300ms)
- `DetailPanel`: 상세 패널 (섹션 A~D)
- `MinuteChart`: lightweight-charts 분봉 + 매수/매도 마커
- `DailyChart`: lightweight-charts 일봉 + MA/BB + 보유구간
- `HistoryOverlay`: 전 채널 거래 일봉 차트 오버레이
- `HypothesisMatrix`: 가설비교 탭 매트릭스

**종목명 표시 전역 함수**:
```javascript
function displayStock(stock_name, stock_code) {
  return `${stock_name} <span class="code-sub">(${stock_code})</span>`;
}
```

### Step 4 — 기존 JS 파일 종목명 소급 적용

| 파일 | 수정 내용 |
|------|---------|
| `frontend/static/js/desk2-backtest.js` | 거래 테이블 종목 컬럼: `stock_code + stock_name` → `stock_name 우선 + code 보조` |
| `frontend/static/js/dashboard.js` | 포지션 테이블 `p.ticker` → `p.stock_name || p.ticker` 우선, 체결 테이블 동일 |

---

## 3. 테스트 결과

파일: `backend/tests/test_trades_unified.py`

| TC | 항목 | 결과 |
|----|------|------|
| TC-01 | unified 응답 구조 검증 | ✅ PASS |
| TC-02 | stock_name JOIN 정상 (null 아닌지) | ✅ PASS |
| TC-03 | BUY-SELL 페어링 정확성 | ✅ PASS |
| TC-04 | 채널 필터 동작 (MOCK) | ✅ PASS |
| TC-05 | DESK 필터 동작 | ✅ PASS |
| TC-06 | 종목명 검색 (한글) | ✅ PASS |
| TC-07 | 분봉 차트 데이터 반환 | ✅ PASS |
| TC-08 | 일봉 차트 + MA/BB 포함 | ✅ PASS |
| TC-09 | 종목 히스토리 채널 색상 포함 | ✅ PASS |
| TC-10 | 가설 매트릭스 피봇 구조 | ✅ PASS |
| TC-11 | 종목 자동완성 (최대 20건) | ✅ PASS |
| TC-12 | 종목명 우선 표시 규칙 | ✅ PASS |
| TC-12b | _safe_float NaN/Inf 방어 | ✅ PASS |

**총계: 13/13 ALL PASS**

---

## 4. 서비스 재시작 및 헬스체크

```bash
sudo systemctl restart go100
# HTTP 200 확인
curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/health
# → 200 ✅
```

API 보안 미들웨어(`InternalAPIKeyMiddleware`)가 외부 직접 접근 차단 (정상 동작).
프론트엔드 접근 시 정상 작동함.

---

## 5. 완료 기준 체크리스트

| 기준 | 상태 |
|------|------|
| trades.html 파일 생성 (`/static/trades.html`) | ✅ |
| 백테스트 거래 목록 종목명으로 표시 | ✅ |
| 거래 클릭 → 분봉 차트 + 매수/매도 마커 (JS) | ✅ |
| 일봉 차트 + 보유구간 하이라이트 (JS) | ✅ |
| 종목 히스토리 오버레이 전 채널 (JS) | ✅ |
| 기간 전환 (1D~ALL) | ✅ |
| 가설 비교 매트릭스 | ✅ |
| 종목명 자동완성 검색 | ✅ |
| desk2-backtest.html 종목명 소급 적용 | ✅ |
| 테스트 TC-01~12 ALL PASS | ✅ (13/13) |
| git commit + push | ✅ (296742a9) |

---

## 6. 커밋 정보

```
커밋 해시: 296742a9
브랜치: phase-2c-command-center
메시지: [V4.1] T-278 CEO 통합 거래 뷰어 Phase 1 — trades.html + API 7개 + 차트 + 히스토리 오버레이 + 종목명 우선 표시 (TC-01~12 ALL PASS)
변경 파일: 8개 (신규 5개, 수정 3개)
삽입: +2842줄
```

---

## 체크포인트

- [x] 코드 레포 커밋 완료 (kis-autotrade-v4, 296742a9)
- [ ] project-docs 보고서 push 완료 (GitHub raw URL 200 확인)

HANDOVER.md 업데이트 완료: (push 후 기록 예정)
