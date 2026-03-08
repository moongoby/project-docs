---
project: kis-autotrade-v4
task_id: T-283
completed_at: 2026-03-08T09:20 KST
---

# T-283 RESULT: trades.html Phase2 – RSI/MACD pane + 보유구간 Rectangle + 전체화면

## 실행 내역 원문

### STEP 1: kw-chart-engine.js 확장 (RSI/MACD pane)

**파일**: `/root/kis-autotrade-v4/frontend/static/js/kw-chart-engine.js`

**생성자 변경** (이전 → 이후):
```
// 이전
this._resizeObs = null;

// 이후
this._resizeObs   = null;
this._panes       = {};      // { rsi: {...}, macd: {...} }
this._rectangles  = [];     // [{ overlay, buyTime, sellTime }]
this._rectRangeCb = null;   // timeScale subscription callback
```

**init() 내부 추가** (CrosshairMove 이벤트 다음):
```javascript
// Rectangle 위치 갱신: timeScale 범위 변경 시
this._rectRangeCb = function () { self._updateAllRectangles(); };
this._chart.timeScale().subscribeVisibleLogicalRangeChange(this._rectRangeCb);
```

**추가된 prototype 메서드** (destroy() 앞에 삽입):

1. `KWChartEngine.prototype.addPane = function addPane(type)`:
   - type='rsi': KWIndicators.calcRSI(closes, 14) 호출 → rsiData 생성
     - chart.addLineSeries({color:'#AB47BC', lineWidth:1, title:'RSI(14)'}, 2) — pane index 2
     - try/catch fallback: priceScaleId:'rsi', scaleMargins:{top:0.82, bottom:0.02}
     - rsiLine.createPriceLine({price:70, color:'#FF5252', lineStyle:Dashed}) — 과매수선
     - rsiLine.createPriceLine({price:30, color:'#69F0AE', lineStyle:Dashed}) — 과매도선
     - this._panes.rsi = { lineSeries, obLine, osLine }
   - type='macd': KWIndicators.calcMACD(closes, 12, 26, 9) 호출
     - pane index: RSI 있으면 3, 없으면 2
     - MACD선: addLineSeries({color:'#2196F3'}, paneIdx)
     - Signal선: addLineSeries({color:'#FF9800'}, paneIdx)
     - Histogram: addHistogramSeries({}, paneIdx) — h>=0 ? rgba(255,59,59,0.55) : rgba(59,130,255,0.55)
     - try/catch fallback: priceScaleId:'macd' + scaleMargins
     - this._panes.macd = { macdLine, signalLine, histSeries }

2. `KWChartEngine.prototype.removePane = function removePane(type)`:
   - this._chart.removeSeries(pane 멤버들)
   - delete this._panes[type]

3. `KWChartEngine.prototype.addHoldingRectangle = function addHoldingRectangle(buyTime, sellTime, color)`:
   - document.createElement('div'), className='kw-holding-rect'
   - position:absolute; top:0; bottom:0; pointer-events:none; z-index:50; display:none; background:color
   - container.appendChild(overlay)
   - this._rectangles.push({ overlay, buyTime, sellTime })
   - this._updateRectangle(rectObj) 즉시 호출

4. `KWChartEngine.prototype.clearRectangles = function clearRectangles()`:
   - 전체 overlay DOM 제거
   - this._rectangles = []

5. `KWChartEngine.prototype._updateRectangle = function(r)`:
   - ts.timeToCoordinate(r.buyTime), ts.timeToCoordinate(r.sellTime)
   - x1/x2 null이면 display:none
   - overlay.style.left, width 갱신, display:block

6. `KWChartEngine.prototype._updateAllRectangles = function()`:
   - this._rectangles.forEach(r => this._updateRectangle(r))

**destroy() 변경**:
```javascript
// 이전
KWChartEngine.prototype.destroy = function () {
  if (this._resizeObs) { this._resizeObs.disconnect(); this._resizeObs = null; }
  if (this._chart)     { this._chart.remove(); this._chart = null; }
  this._candleSeries = null;
  this._maSeries     = {};
  this._bbSeries     = {};
  this._volSeries    = null;
  this._chartData    = [];
};

// 이후
KWChartEngine.prototype.destroy = function () {
  if (this._resizeObs) { this._resizeObs.disconnect(); this._resizeObs = null; }
  this.clearRectangles();
  this.removePane('rsi');
  this.removePane('macd');
  if (this._chart)     { this._chart.remove(); this._chart = null; }
  this._candleSeries = null;
  this._maSeries     = {};
  this._bbSeries     = {};
  this._volSeries    = null;
  this._chartData    = [];
  this._panes        = {};
};
```

---

### STEP 2: trades-kiwoom.css 추가

**파일**: `/root/kis-autotrade-v4/frontend/static/css/trades-kiwoom.css`

`/* ===== 스크롤바 ===== */` 섹션 앞에 다음 추가 (57줄):

```css
/* ===== RSI / MACD 보조 pane ===== */
.kw-pane-rsi,
.kw-pane-macd {
  width: 100%;
  border-top: 1px solid var(--kw-border);
  background: var(--kw-bg-primary);
  flex-shrink: 0;
}
.kw-pane-rsi  { height: 80px;  }
.kw-pane-macd { height: 100px; }

/* ===== 보유구간 Rectangle 오버레이 ===== */
.kw-holding-rect {
  position: absolute;
  top: 0;
  bottom: 0;
  pointer-events: none;
  z-index: 50;
  display: none;
}

/* ===== 차트 전체화면 모드 ===== */
.kw-chart-section.kw-fullscreen {
  grid-column: 1 / -1;
  z-index: 200;
}
.kw-right-panel.kw-hidden {
  display: none !important;
}

/* 차트 섹션 전체화면 버튼 */
.kw-chart-fullscreen-btn {
  margin-left: auto;
  padding: 2px 7px;
  background: var(--kw-bg-card);
  border: 1px solid var(--kw-border);
  color: var(--kw-text-secondary);
  border-radius: var(--kw-radius);
  cursor: pointer;
  font-size: 13px;
  line-height: 1;
  transition: all 0.15s;
}
.kw-chart-fullscreen-btn:hover {
  background: var(--kw-bg-hover);
  color: var(--kw-text-primary);
}
.kw-chart-fullscreen-btn.active {
  background: var(--kw-accent);
  border-color: var(--kw-accent);
  color: #fff;
}

/* 인디케이터 버튼 active 강조 (RSI/MACD 전용 색상) */
.kw-ind-btn[data-ind="rsi"].active  { background: #7B1FA2; border-color: #7B1FA2; color: #fff; }
.kw-ind-btn[data-ind="macd"].active { background: #1565C0; border-color: #1565C0; color: #fff; }
```

---

### STEP 3: trades.html 수정

**파일**: `/root/kis-autotrade-v4/frontend/static/trades.html`

**HTML 변경 (툴바에 전체화면 버튼 추가)**:
```html
<!-- 이전 -->
          </div>
        </div>
        <div class="kw-ma-bar" id="ma-bar">

<!-- 이후 -->
          <button id="btn-chart-fullscreen" class="kw-chart-fullscreen-btn" title="차트 전체화면 (F)">⛶</button>
          </div>
        </div>
        <div class="kw-ma-bar" id="ma-bar">
```

**INIT SCRIPT 전면 교체** (290줄 → 새 402줄):

주요 변경 사항:
1. `const chart = new KWChartEngine()` — 인스턴스 방식 전환
2. `chart.init('chart-container')` — 올바른 초기화
3. `chart.onCrosshairMove(...)` — 올바른 API (기존 subscribeCrosshairMove 오류 수정)
4. `chart.toggleMA/toggleBB/toggleVol` — 올바른 메서드명
5. RSI/MACD 토글 이벤트:
   ```javascript
   else if (ind === 'rsi') {
     if (active) chart.addPane('rsi');
     else        chart.removePane('rsi');
   }
   else if (ind === 'macd') {
     if (active) chart.addPane('macd');
     else        chart.removePane('macd');
   }
   ```
6. onTradeSelect → clearRectangles + addHoldingRectangle:
   ```javascript
   chart.clearRectangles();
   const stockTrades = allTrades.filter(t => t.stock_code === trade.stock_code);
   stockTrades.forEach(t => {
     const buyTime  = t.buy_date  || t.buy_time  || t.open_date  || null;
     const sellTime = t.sell_date || t.sell_time || t.close_date || null;
     if (buyTime && sellTime) {
       const isProfitable = ((t.profit_pct || t.pnl_pct || t.pnl || 0) >= 0);
       const color = isProfitable ? 'rgba(255,59,59,0.08)' : 'rgba(59,130,255,0.08)';
       chart.addHoldingRectangle(buyTime, sellTime, color);
     }
   });
   ```
7. toggleChartFullscreen() — CSS 모드 (grid-column:1/-1 + right panel 숨김)
8. 키보드: F=전체화면, Escape=전체화면 해제, d/w/m/v/b/t 기존 단축키 유지

---

### STEP 4: 검증 결과

#### ls -la (파일 존재 확인)
```
-rw-rw-r-- 1 claudebot claudebot 15503 Mar  8 09:05 /root/kis-autotrade-v4/frontend/static/css/trades-kiwoom.css
-rw-rw-r-- 1 claudebot claudebot 22902 Mar  8 09:05 /root/kis-autotrade-v4/frontend/static/js/kw-chart-engine.js
-rw-rw-r-- 1 claudebot claudebot  8914 Mar  8 08:42 /root/kis-autotrade-v4/frontend/static/js/kw-data-grid.js
-rw-rw-r-- 1 claudebot claudebot 15282 Mar  8 08:38 /root/kis-autotrade-v4/frontend/static/js/kw-indicators.js
-rw-rw-r-- 1 claudebot claudebot 12068 Mar  8 08:40 /root/kis-autotrade-v4/frontend/static/js/kw-markers-tooltip.js
-rw-rw-r-- 1 claudebot claudebot  8521 Mar  8 08:38 /root/kis-autotrade-v4/frontend/static/js/kw-trade-list.js
-rw-rw-r-- 1 claudebot claudebot 20751 Mar  8 09:07 /root/kis-autotrade-v4/frontend/static/trades.html
```
→ 7/7파일 PASS ✅

#### node -c 문법 검사
```
node -c kw-chart-engine.js   → OK ✅
node -c kw-indicators.js     → OK ✅
node -c kw-markers-tooltip.js → OK ✅
node -c kw-trade-list.js     → OK ✅
node -c kw-data-grid.js      → OK ✅
```
→ 5/5 JS 문법검사 PASS ✅

#### grep 검증
```
grep -n "addPane\|removePane\|addHoldingRectangle\|clearRectangles" kw-chart-engine.js
→ 367: // ── addPane(type, options) ─...
→ 371: KWChartEngine.prototype.addPane = function addPane(type) {...}
→ 473: // ── removePane(type) ─...
→ 474: KWChartEngine.prototype.removePane = function removePane(type) {...}
→ 491: // ── addHoldingRectangle(buyTime, sellTime, color) ─...
→ 493: KWChartEngine.prototype.addHoldingRectangle = function addHoldingRectangle(...)
→ 510: // ── clearRectangles() ─...
→ 511: KWChartEngine.prototype.clearRectangles = function clearRectangles()

grep -n "kw-fullscreen\|kw-pane-rsi\|kw-pane-macd\|kw-holding-rect" trades-kiwoom.css
→ 495: .kw-pane-rsi,
→ 496: .kw-pane-macd {
→ 502: .kw-pane-rsi  { height: 80px;  }
→ 503: .kw-pane-macd { height: 100px; }
→ 506: .kw-holding-rect {
→ 516: .kw-chart-section.kw-fullscreen {

grep -n "addPane\|removePane\|toggleChartFullscreen\|clearRectangles\|addHoldingRectangle" trades.html
→ 182: chart.clearRectangles();
→ 190: chart.addHoldingRectangle(buyTime, sellTime, color);
→ 267: chart.removePane('rsi'); chart.addPane('rsi');
→ 270: chart.removePane('macd'); chart.addPane('macd');
→ 302: function toggleChartFullscreen() {
→ 338: // ── 이벤트: 인디케이터 토글 (RSI/MACD addPane/removePane) ─
→ 348: if (active) chart.addPane('rsi');
→ 349: else        chart.removePane('rsi');
→ 352: if (active) chart.addPane('macd');
→ 353: else        chart.removePane('macd');
→ 383: if (fsBtn) fsBtn.addEventListener('click', toggleChartFullscreen);
→ 389: if (key === 'F' || key === 'f') { if (!e.ctrlKey) toggleChartFullscreen(); }
→ 390: else if (key === 'Escape') { if (isChartFullscreen) toggleChartFullscreen(); }
```
→ grep 3종 ALL PASS ✅

#### HTTP 200 확인
```
curl -s -o /dev/null -w "%{http_code}" https://trading41.newtalk.kr/trades.html
→ 200 ✅
```

---

### STEP 5: Git commit/push

#### 코드 레포 (kis-autotrade-v4)
```
git add frontend/static/css/trades-kiwoom.css
        frontend/static/js/kw-chart-engine.js
        frontend/static/trades.html
→ 3 files staged

sudo /usr/bin/git -C /root/kis-autotrade-v4 commit -m "[V4.1] T-283 trades.html Phase2: RSI/MACD pane + 보유구간 Rectangle + 전체화면 ..."
→ [phase-2c-command-center c6bc6a4b] 3 files changed, 453 insertions(+), 102 deletions(-)

sudo /usr/bin/git -C /root/kis-autotrade-v4 push origin phase-2c-command-center
→ To github.com:moongoby/go100.git
   4b327d12..c6bc6a4b  phase-2c-command-center -> phase-2c-command-center ✅
```

#### project-docs (HANDOVER + 보고서)
```
HANDOVER.md v10.66 갱신: T-283 완료 행 추가, header v10.65→v10.66 업데이트

cp report → /root/project-docs/kis-autotrade-v4/reports/CUR-V41-T283-CHART-PHASE2-001-20260308.md

sudo /usr/bin/git -C /root/project-docs add kis-autotrade-v4/HANDOVER.md
                                              kis-autotrade-v4/reports/CUR-V41-T283-CHART-PHASE2-001-20260308.md
→ [master 1224100] docs: T-283 보고서 push + HANDOVER v10.66 갱신 (20260308)
   2 files changed, 215 insertions(+), 1 deletion(-)

sudo /usr/bin/git -C /root/project-docs push origin master
→ To github.com:moongoby/project-docs.git
   c913501..1224100  master -> master ✅
```

#### GitHub raw URL 200 확인
```
curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/reports/CUR-V41-T283-CHART-PHASE2-001-20260308.md"
→ 200 ✅

curl -s -o /dev/null -w "%{http_code}" \
  "https://raw.githubusercontent.com/moongoby/project-docs/master/kis-autotrade-v4/HANDOVER.md"
→ 200 ✅
```

---

## 최종 체크포인트

- [x] 코드 레포 커밋 완료 (kis-autotrade-v4, c6bc6a4b, phase-2c-command-center)
- [x] project-docs 보고서 push 완료 (GitHub raw URL 200 확인)
- [x] HANDOVER.md v10.66 갱신 완료 (1224100)

---

## CEO 보고 형식

```
[CURSOR-KIS] 완료
작업: T-283 trades.html Phase2 (RSI/MACD pane + 보유구간 Rectangle + 전체화면)
보고서: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/CUR-V41-T283-CHART-PHASE2-001-20260308.md
커밋(코드): https://github.com/moongoby/kis-autotrade-v4/commit/c6bc6a4b
커밋(문서): https://github.com/moongoby/project-docs/commit/1224100
HANDOVER: https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/HANDOVER.md
HTTP: 200 확인 완료
security_scan: 0건 (실행 안 함 - 스크립트 미존재)
path_check: PASS
다음: T-283-Phase3 (자동추세선, 거래량프로파일) 또는 지시 대기
```

HANDOVER.md 업데이트 완료: 1224100
