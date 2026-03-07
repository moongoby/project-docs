---
project: KIS-V41
task_id: T-282-S2B
completed_at: 2026-03-08T08:36:18+09:00
---

# T-282-S2B 실행 결과

## 사전 확인

### /tmp/T-282-S1-RESULT.md 상태
```
$ cat /tmp/T-282-S1-RESULT.md
FILE_NOT_FOUND
```
T-282-S1 결과 파일이 없었으므로, 프로젝트 코드베이스에서 직접 STATIC_PATH 및 API 엔드포인트를 확인.

### STATIC_PATH 확인
```
$ find /root/kis-autotrade-v4/frontend -name "*.html" | head -5
/root/kis-autotrade-v4/frontend/ai-model.html
/root/kis-autotrade-v4/frontend/static/desk2-live.html
/root/kis-autotrade-v4/frontend/static/trades.html
...
$ ls /root/kis-autotrade-v4/frontend/static/
admin.html  css  desk2-backtest.html  desk2-live.html  js  trades.html ...
```
→ **STATIC_PATH = /root/kis-autotrade-v4/frontend/static**

### API 엔드포인트 확인 (v4_trades_unified.py + trades-viewer.js)
```
$ grep "@router.get\|@router.post" /root/kis-autotrade-v4/backend/app/routers/v4_trades_unified.py
@router.get("/trades/unified")
@router.get("/trades/{trade_id}/detail")
@router.get("/trades/{trade_id}/chart/minute")
@router.get("/trades/{trade_id}/chart/daily")
@router.get("/trades/stock/{stock_code}/history")
@router.get("/trades/hypothesis-matrix")
@router.get("/stocks/search")
```

---

## 실행

### 1. JS 디렉토리 확인
```
$ ls /root/kis-autotrade-v4/frontend/static/js/
backtest-dashboard.js  dashboard.js  data-collection.js  desk2-backtest.js  desk2-live.js  trades-viewer.js
```
→ /root/kis-autotrade-v4/frontend/static/js/ 이미 존재

### 2. kw-chart-engine.js 파일 생성

파일 경로: `/root/kis-autotrade-v4/frontend/static/js/kw-chart-engine.js`

**구현 내용:**

```
window.KWChartEngine으로 export:
  - global.KWChartEngine = KWChartEngine
  - window.KWChartEngine = KWChartEngine (명시적 browser export)

색상 상수 (한국 표준):
  - 양봉: #FF3B3B
  - 음봉: #3B82FF
  - UP_VOL:  #FF3B3B55 (빨강반투명)
  - DOWN_VOL: #3B82FF55 (파랑반투명)
  - MA5: #F1C40F, MA10: #E67E22, MA20: #3498DB, MA60: #9B59B6, MA120: #1ABC9C
  - BB_UPPER: #F39C12, BB_LOWER: #2ECC71

API_URLS 객체 (T-282-S1 실제 엔드포인트):
  - trades_unified:    '/api/v4/trades/unified'
  - trade_detail:      '/api/v4/trades/{trade_id}/detail'
  - chart_minute:      '/api/v4/trades/{trade_id}/chart/minute'
  - chart_daily:       '/api/v4/trades/{trade_id}/chart/daily'
  - stock_history:     '/api/v4/trades/stock/{stock_code}/history'
  - hypothesis_matrix: '/api/v4/trades/hypothesis-matrix'
  - stocks_search:     '/api/v4/stocks/search'

차트 구성:
  - Lightweight Charts v5 createChart 초기화
  - CandlestickSeries (Pane 0): upColor/downColor/wickUpColor/wickDownColor (#FF3B3B/#3B82FF)
  - LineSeries x5 (MA5~MA120, Pane 0): 5색 이평선
  - LineSeries x2 (BB upper/lower, Pane 0): 볼린저밴드 점선 (lineStyle: Dashed)
  - HistogramSeries (Pane 1): 거래량, 양봉=빨강반투명, 음봉=파랑반투명
    * v5: chart.addHistogramSeries(opts, 1) — paneIndex=1 지원
    * fallback: scaleMargins { top: 0.80, bottom: 0.00 }
  - CrosshairMode.Normal + vertLine/horzLine Dashed 십자선
  - ResizeObserver 반응형 (clientWidth/clientHeight 자동 반영)

함수:
  - init(containerId)                 — 차트 생성·초기화
  - setData(data)                     — candles + indicators 세팅
  - setMarkers(markers)               — 진입/청산 마커
  - toggleMA(bool)                    — MA 시리즈 표시 토글
  - toggleBB(bool)                    — BB 시리즈 표시 토글
  - toggleVol(bool)                   — 거래량 표시 토글
  - onCrosshairMove(callback)         — OHLC+MA값 콜백 등록
  - fetchChartData(stockCode, period) — API 호출, fallback 지원 (minute→daily)
  - fetchTrades(params)               — /api/v4/trades/unified 호출
  - fetchStockHistory(stockCode)      — /api/v4/trades/stock/{code}/history 호출

getter:
  - getChart()       — IChartApi 반환
  - getCandleSeries()— CandlestickSeries 반환
  - getChartData()   — 현재 로드된 candles 배열 반환
  - getState()       — { maVisible, bbVisible, volVisible } 반환
```

---

## 검증

### ls -la
```
$ ls -la /root/kis-autotrade-v4/frontend/static/js/kw-chart-engine.js
-rw-rw-r-- 1 claudebot claudebot 14512 Mar  8 08:36 /root/kis-autotrade-v4/frontend/static/js/kw-chart-engine.js
```

### wc -l
```
$ wc -l /root/kis-autotrade-v4/frontend/static/js/kw-chart-engine.js
378 /root/kis-autotrade-v4/frontend/static/js/kw-chart-engine.js
```
→ 378줄 (기대: 140줄 이상) ✅

### grep window.KWChartEngine
```
$ grep "window.KWChartEngine" /root/kis-autotrade-v4/frontend/static/js/kw-chart-engine.js
 * window.KWChartEngine 으로 export
  // window.KWChartEngine 글로벌 등록
  if (typeof window !== 'undefined') { window.KWChartEngine = KWChartEngine; }
```
→ 3줄 매칭 (기대: 1줄 이상) ✅

### grep -c function init|setData|setMarkers|onCrosshairMove
```
$ grep -c "function init\|function setData\|function setMarkers\|function onCrosshairMove" /root/kis-autotrade-v4/frontend/static/js/kw-chart-engine.js
4
```
→ 4 (기대: 4) ✅

---

## 검증 결과 요약

| 체크 항목 | 기대값 | 실제값 | 상태 |
|-----------|--------|--------|------|
| 파일 존재 (ls -la) | 존재 | -rw-rw-r-- 14512바이트 | ✅ |
| 줄 수 (wc -l) | 140+ | 378 | ✅ |
| window.KWChartEngine (grep) | 1줄+ | 3줄 | ✅ |
| 핵심 함수 4개 (grep -c) | 4 | 4 | ✅ |

---

## 산출물

- **파일**: /root/kis-autotrade-v4/frontend/static/js/kw-chart-engine.js
- **크기**: 14512 bytes, 378줄
- **STATIC_PATH**: /root/kis-autotrade-v4/frontend/static (코드베이스에서 직접 확인)
- **API_URLS**: v4_trades_unified.py + trades-viewer.js에서 확인한 실제 엔드포인트 7개

## 완료 상태

T-282-S2B ALL PASS ✅
