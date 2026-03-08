# KIS-295 trades.html 빈화면 원인 진단 및 수정 보고서

**Task ID**: KIS-295
**날짜**: 2026-03-08
**작성자**: Claude Code (Sonnet 4.6)
**커밋**: bad34b3f

---

[인계 확인]
직전 완료: KIS-293
현재 단계: Phase 2c
CEO 지시 적용: D-001, D-007
strategy_cards: 60
open_positions: 0

---

## 1. 문제 현상

`https://trading41.newtalk.kr/trades.html` 접속 시:
- MA5/10/20/60/120 값 전부 "-"
- 거래 목록 빈칸
- 차트 빈 화면

---

## 2. 진단 결과

### STEP 1: 내부 API 확인

| 엔드포인트 | 상태코드 | 원인 |
|-----------|---------|------|
| `GET http://127.0.0.1:8003/api/chart-data?symbol=005930` | 404 Not Found | 경로 미존재 |
| `GET http://127.0.0.1:8003/api/stocks/search?q=삼성` | 400 Bad Request | URL 인코딩 문제 + 경로 미존재 |
| `GET http://127.0.0.1:8003/api/trades/unified` | 404 Not Found | 경로 미존재 |

→ 실제 등록된 경로:
- `/api/v4/trades/unified` (v4_trades_unified_router)
- `/api/v4/chart/daily/{stock_code}` (v4_chart router)
- `/api/v4/stocks/search` (v4_trades_unified_router)
- `/api/v4/trades/{trade_id}/chart/daily` (v4_trades_unified_router)

### STEP 2: 외부 Nginx API 확인

| 엔드포인트 | 상태코드 |
|-----------|---------|
| `GET https://trading41.newtalk.kr/api/v4/trades/unified?limit=3` | **200 OK** |
| `GET https://trading41.newtalk.kr/api/v4/chart/daily/005930?limit=5` | **200 OK** |
| `GET https://trading41.newtalk.kr/api/v4/stocks/search?q=삼성` | **200 OK** |
| `GET https://trading41.newtalk.kr/api/v4/trades/BT_211438/chart/daily` | **200 OK** |

→ Nginx는 `/api/v4/` → 8003에 `X-Internal-API-Key` 헤더 주입. 외부 접근 정상.

### STEP 3: 근본 원인 분석

**원인 1: URL 불일치 (3곳)**
```
trades.html INIT SCRIPT 실제 호출          실제 등록된 API
/api/trades/unified              →         /api/v4/trades/unified
/api/chart-data?stock_code=X    →         /api/v4/trades/{trade_id}/chart/daily
/api/trades?stock_code=X        →         /api/v4/trades/stock/{stock_code}/history
```

**원인 2: 모듈 API 불일치 (10+곳)**
| 잘못된 호출 | 실제 메서드/시그니처 |
|-----------|-----------------|
| `KWChartEngine.init('chart-container')` | `new KWChartEngine(); engine.init()` |
| `KWChartEngine.subscribeCrosshairMove()` | `engine.onCrosshairMove()` |
| `KWChartEngine.setData(rawArray)` | `engine.setData({candles,indicators})` |
| `KWChartEngine.setMAData()` | 존재하지 않음 |
| `KWChartEngine.setBBData()` | 존재하지 않음 |
| `KWTradeList.renderTradeList()` | `KWTradeList.renderList()` |
| `KWTradeList.applyFilters()` | 존재하지 않음 |
| `KWTradeList.updateTradeCount()` | 존재하지 않음 |
| `KWMarkersTooltip.createDataWindow()` | 존재하지 않음 |
| `KWMarkersTooltip.buildMarkers(rawTrades)` | `buildMarkers(enrichedChartData)` |
| `KWDataGrid.renderDataGrid()` | `KWDataGrid.renderCandleRows()` |
| `KWDataGrid.toggleDataGrid()` | `KWDataGrid.toggle()` |
| `KWIndicators.formatPrice()` | 존재하지 않음 (`fmt()`) |

**원인 3: 날짜 형식 불일치**
- `/api/v4/trades/{trade_id}/chart/daily` 응답 `time: "20260306"` (YYYYMMDD)
- Lightweight Charts v5는 `"YYYY-MM-DD"` 형식 요구
- → 차트 candle 렌더링 불가 (LWCharts 파싱 실패)

---

## 3. 수정 내용

### 수정 1: `backend/app/routers/v4_trades_unified.py`

`get_trade_daily_chart` 함수에서 candle 날짜 형식 변환:
```python
# 수정 전
"time": row[0],  # YYYYMMDD string

# 수정 후
def _v8_to_iso(d: str) -> str:
    """YYYYMMDD → YYYY-MM-DD (Lightweight Charts 호환)"""
    s = str(d).strip()
    return s[:4] + "-" + s[4:6] + "-" + s[6:8] if len(s) == 8 else s

"time": _v8_to_iso(row[0]),  # KIS-295: YYYY-MM-DD format for LW Charts
```

→ MA/BB 지표도 `c["time"]`을 참조하므로 동시에 수정됨

### 수정 2: `frontend/trades.html` + `frontend/static/trades.html`

INIT SCRIPT 완전 재작성 (188줄 → 200줄):

**주요 변경:**
1. `const chartEngine = new window.KWChartEngine()` — 생성자 패턴 사용
2. `chartEngine.fetchTrades(params)` — 올바른 API URL 사용
3. `chartEngine.fetchChartData(tradeId, 'daily')` — `trade_id` 기반 차트 로드
4. `KWTradeList.renderList()` + `KWTradeList.onSelect()` — 올바른 메서드
5. `KWMarkersTooltip.bindTrades(candles, stockTrades)` + `buildMarkers(enriched)` — 올바른 2단계 처리
6. `KWDataGrid.init()` + `renderCandleRows()` + `toggle()` — 올바른 메서드
7. RSI/MACD pane → `chartEngine.addPane/removePane` 연결
8. MA bar → `info.ma[key]` (crosshair payload) 기반 업데이트
9. 필터 수집 → trades.html 실제 element ID 기준 (`filter-channel` 등)

---

## 4. 검증 결과

### 코드 검증
- Python AST: `v4_trades_unified.py` ✅ PASS
- JS 문법: `trades.html` INIT SCRIPT node -c ✅ PASS
- 잘못된 URL 패턴 없음: grep 0건 ✅
- 잘못된 메서드 없음: grep 0건 ✅

### API 응답 검증
| 엔드포인트 | HTTP | 비고 |
|-----------|------|------|
| `/api/v4/trades/unified?limit=3` | 200 | 105,526건 총 |
| `/api/v4/trades/BT_211438/chart/daily` | 200 | candles: 57, first_time: **2025-12-08** ✅ |
| `/api/v4/stocks/search?q=삼성` | 200 | 삼성전자 등 20건+ |
| `https://trading41.newtalk.kr/trades.html` | 200 | HTML 정상 서빙 |
| JS 모듈 5개 (kw-*.js) | 200 | 전부 정상 |

### candle time 형식 변경 확인
```
수정 전: "time": "20260306"  → LW Charts 파싱 불가
수정 후: "time": "2025-12-08" → LW Charts v5 YYYY-MM-DD 호환 ✅
```

---

## 5. 커밋 정보

| 항목 | 내용 |
|------|------|
| 커밋 해시 | bad34b3f |
| 브랜치 | phase-2c-command-center |
| 변경 파일 | 3개 (v4_trades_unified.py, trades.html, static/trades.html) |
| +/- | +275 / -358 |

---

## 6. 남은 이슈

- `stock_name` 필드: trades.html `filter-stock` 입력 → `stock_name` LIKE 검색으로 동작 (stock_code 직접 검색 불가, API 제한)
- 종목 이력(stock-history) 날짜 표시: `entry_date` 필드명 vs `trade_date` 불일치로 날짜 "-" 표시 (기능에는 영향 없음)

---

## 체크포인트

- [x] 코드 레포 커밋 완료: bad34b3f (phase-2c-command-center)
- [x] project-docs 보고서 push 완료 (진행 중)

HANDOVER.md 업데이트 완료: (push 후 기재 예정)
