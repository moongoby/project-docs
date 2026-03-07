---
project: KIS-V41
task_id: T-282-S2C
completed_at: 2026-03-08T08:38:00+09:00
---

# T-282-S2C 실행 결과

## 지시서 원문 (KIS_20260308_050411_BRIDGE.md)

```
TASK_ID: T-282-S2C
TITLE: 기술적 지표 계산 유틸리티 (kw-indicators.js)
PRIORITY: P0
PROJECT: KIS-V41
DEPENDS_ON: T-282-S1 완료 (static 경로만 필요)
PARALLEL: T-282-S2A, T-282-S2B, T-282-S2D와 동시 실행 가능
ESTIMATED_TIME: 2분

[사전 확인]
- STATIC_PATH=$(grep "static 루트:" /tmp/T-282-S1-RESULT.md | awk -F': ' '{print $2}')

[실행]
1. ${STATIC_PATH}/js/kw-indicators.js 파일 생성 — 핵심 기능:
   - window.KWIndicators로 export
   - 순수 함수 (DB/API 의존 없음, 브라우저 단독 실행)
   - calcMA(data, period) — 단순 이동평균
   - calcBB(data, period=20, mult=2) — 볼린저밴드 상하한
   - calcRSI(data, period=14) — RSI
   - calcEMA(data, period) — 지수이동평균
   - calcMACD(data, fast=12, slow=26, signal=9) — MACD line/signal/histogram
   - normalizeChartData(raw) — API 응답 → 표준화 (date/time/open/high/low/close/volume/ma5~120/bb/rsi/macd)
     KIS API 필드명 호환: stck_oprc→open, stck_hgpr→high, stck_lwpr→low, stck_clpr→close, acml_vol→volume
   - ensureIndicators(data) — API에서 지표 미제공 시 자동 계산 fallback
   - fmt(n) — 숫자 천단위 포맷 (ko-KR)
   - fmtPct(n) — +0.00% 형식
   - fmtDate(d) — YYYY-MM-DD 형식

   ※ 이전 대화에서 제공한 kw-indicators.js 코드를 그대로 사용

[검증]
ls -la ${STATIC_PATH}/js/kw-indicators.js
grep "window.KWIndicators" ${STATIC_PATH}/js/kw-indicators.js
grep -c "function calc" ${STATIC_PATH}/js/kw-indicators.js
# 기대: 5 이상
```

---

## 실행 과정

### 사전 확인 — STATIC_PATH 결정

T-282-S1-RESULT.md 파일 확인:
```
$ cat /tmp/T-282-S1-RESULT.md
FILE_NOT_FOUND
```

T-282-S1-RESULT.md 파일이 존재하지 않아 직접 프로젝트 구조 확인:
```
$ ls /root/kis-autotrade-v4/frontend/static/js/
backtest-dashboard.js
dashboard.js
data-collection.js
desk2-backtest.js
desk2-live.js
kw-chart-engine.js
trades-viewer.js

$ ls /root/kis-autotrade-v4/frontend/static/
admin.html
admin.html.bak.202602262205
css
desk2-backtest.css
desk2-backtest.html
desk2-backtest.js
desk2-live.html
js
trades.html
trades.html.bak.20260308083234
```

STATIC_PATH = `/root/kis-autotrade-v4/frontend/static` 로 확정.

---

### 파일 생성

경로: `/root/kis-autotrade-v4/frontend/static/js/kw-indicators.js`

생성 내용 (전문):

```javascript
/**
 * kw-indicators.js
 * 기술적 지표 계산 유틸리티 (KIS AutoTrade V4.1)
 * - 순수 함수, DB/API 의존 없음, 브라우저 단독 실행 가능
 * - window.KWIndicators 로 export
 */

(function (global) {
  'use strict';

  /* ─────────────────────────────────────────────
   * 내부 헬퍼
   * ───────────────────────────────────────────── */

  /** 숫자 배열에서 인덱스 i 까지 period 개의 합계 */
  function _sum(arr, i, period) {
    let s = 0;
    for (let k = i - period + 1; k <= i; k++) s += arr[k];
    return s;
  }

  /* ─────────────────────────────────────────────
   * 이동평균 계산
   * ───────────────────────────────────────────── */

  /**
   * calcMA(data, period) — 단순 이동평균 (SMA)
   * @param {number[]} data   종가 배열 (시간순 오름차순)
   * @param {number}   period 기간
   * @returns {(number|null)[]} MA 배열 (period-1 개는 null)
   */
  function calcMA(data, period) {
    const result = [];
    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        result.push(null);
      } else {
        result.push(_sum(data, i, period) / period);
      }
    }
    return result;
  }

  /* ─────────────────────────────────────────────
   * 지수이동평균 계산
   * ───────────────────────────────────────────── */

  /**
   * calcEMA(data, period) — 지수이동평균 (EMA)
   * @param {number[]} data
   * @param {number}   period
   * @returns {(number|null)[]}
   */
  function calcEMA(data, period) {
    const k = 2 / (period + 1);
    const result = new Array(data.length).fill(null);

    // 첫 EMA = SMA
    let firstIdx = period - 1;
    if (firstIdx >= data.length) return result;

    let ema = _sum(data, firstIdx, period) / period;
    result[firstIdx] = ema;

    for (let i = firstIdx + 1; i < data.length; i++) {
      ema = data[i] * k + ema * (1 - k);
      result[i] = ema;
    }
    return result;
  }

  /* ─────────────────────────────────────────────
   * 볼린저밴드 계산
   * ───────────────────────────────────────────── */

  /**
   * calcBB(data, period=20, mult=2) — 볼린저밴드
   * @param {number[]} data
   * @param {number}   period  기준 SMA 기간 (default 20)
   * @param {number}   mult    표준편차 배수 (default 2)
   * @returns {{ upper:(number|null)[], middle:(number|null)[], lower:(number|null)[] }}
   */
  function calcBB(data, period, mult) {
    period = period === undefined ? 20 : period;
    mult   = mult   === undefined ? 2  : mult;

    const upper  = [];
    const middle = [];
    const lower  = [];

    for (let i = 0; i < data.length; i++) {
      if (i < period - 1) {
        upper.push(null);
        middle.push(null);
        lower.push(null);
      } else {
        const sma = _sum(data, i, period) / period;
        let variance = 0;
        for (let k = i - period + 1; k <= i; k++) {
          variance += Math.pow(data[k] - sma, 2);
        }
        const std = Math.sqrt(variance / period);
        upper.push(sma + mult * std);
        middle.push(sma);
        lower.push(sma - mult * std);
      }
    }
    return { upper, middle, lower };
  }

  /* ─────────────────────────────────────────────
   * RSI 계산
   * ───────────────────────────────────────────── */

  /**
   * calcRSI(data, period=14) — Relative Strength Index
   * @param {number[]} data
   * @param {number}   period (default 14)
   * @returns {(number|null)[]}
   */
  function calcRSI(data, period) {
    period = period === undefined ? 14 : period;
    const result = new Array(data.length).fill(null);
    if (data.length < period + 1) return result;

    // 첫 번째 평균 이익/손실
    let avgGain = 0;
    let avgLoss = 0;
    for (let i = 1; i <= period; i++) {
      const diff = data[i] - data[i - 1];
      if (diff >= 0) avgGain += diff;
      else avgLoss += Math.abs(diff);
    }
    avgGain /= period;
    avgLoss /= period;

    const rs0 = avgLoss === 0 ? Infinity : avgGain / avgLoss;
    result[period] = avgLoss === 0 ? 100 : 100 - 100 / (1 + rs0);

    for (let i = period + 1; i < data.length; i++) {
      const diff = data[i] - data[i - 1];
      const gain = diff >= 0 ? diff : 0;
      const loss = diff <  0 ? Math.abs(diff) : 0;
      avgGain = (avgGain * (period - 1) + gain) / period;
      avgLoss = (avgLoss * (period - 1) + loss) / period;
      const rs = avgLoss === 0 ? Infinity : avgGain / avgLoss;
      result[i] = avgLoss === 0 ? 100 : 100 - 100 / (1 + rs);
    }
    return result;
  }

  /* ─────────────────────────────────────────────
   * MACD 계산
   * ───────────────────────────────────────────── */

  /**
   * calcMACD(data, fast=12, slow=26, signal=9)
   * @param {number[]} data
   * @param {number}   fast    (default 12)
   * @param {number}   slow    (default 26)
   * @param {number}   signal  (default 9)
   * @returns {{ macd:(number|null)[], signal:(number|null)[], histogram:(number|null)[] }}
   */
  function calcMACD(data, fast, slow, signalPeriod) {
    fast         = fast         === undefined ? 12 : fast;
    slow         = slow         === undefined ? 26 : slow;
    signalPeriod = signalPeriod === undefined ? 9  : signalPeriod;

    const emaFast = calcEMA(data, fast);
    const emaSlow = calcEMA(data, slow);

    const macdLine = data.map(function (_, i) {
      if (emaFast[i] === null || emaSlow[i] === null) return null;
      return emaFast[i] - emaSlow[i];
    });

    // Signal = EMA(macdLine, signalPeriod) — null 제거 후 계산
    const macdValues = macdLine.filter(function (v) { return v !== null; });
    const sigRaw = calcEMA(macdValues, signalPeriod);

    // signal 배열을 원래 인덱스로 복원
    const signalLine = new Array(data.length).fill(null);
    let j = 0;
    for (let i = 0; i < data.length; i++) {
      if (macdLine[i] !== null) {
        signalLine[i] = sigRaw[j++];
      }
    }

    const histogram = data.map(function (_, i) {
      if (macdLine[i] === null || signalLine[i] === null) return null;
      return macdLine[i] - signalLine[i];
    });

    return { macd: macdLine, signal: signalLine, histogram: histogram };
  }

  /* ─────────────────────────────────────────────
   * 포맷 헬퍼
   * ───────────────────────────────────────────── */

  /**
   * fmt(n) — 숫자 천단위 포맷 (ko-KR)
   * @param {number} n
   * @returns {string}
   */
  function fmt(n) {
    if (n === null || n === undefined || isNaN(n)) return '-';
    return Number(n).toLocaleString('ko-KR');
  }

  /**
   * fmtPct(n) — +0.00% 형식
   * @param {number} n  (예: 1.23 → "+1.23%")
   * @returns {string}
   */
  function fmtPct(n) {
    if (n === null || n === undefined || isNaN(n)) return '-';
    const sign = n >= 0 ? '+' : '';
    return sign + Number(n).toFixed(2) + '%';
  }

  /**
   * fmtDate(d) — YYYY-MM-DD 형식
   * @param {string|Date} d
   * @returns {string}
   */
  function fmtDate(d) {
    if (!d) return '-';
    if (d instanceof Date) {
      const y = d.getFullYear();
      const m = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return y + '-' + m + '-' + day;
    }
    // 문자열 YYYYMMDD → YYYY-MM-DD
    const s = String(d).replace(/-/g, '');
    if (s.length === 8) {
      return s.slice(0, 4) + '-' + s.slice(4, 6) + '-' + s.slice(6, 8);
    }
    // ISO or other
    return String(d).slice(0, 10);
  }

  /* ─────────────────────────────────────────────
   * API 응답 정규화
   * ───────────────────────────────────────────── */

  /**
   * normalizeChartData(raw)
   * KIS API 응답(또는 내부 API) → 표준화된 오브젝트 배열
   *
   * KIS API 필드 호환:
   *   stck_oprc → open
   *   stck_hgpr → high
   *   stck_lwpr → low
   *   stck_clpr → close
   *   acml_vol  → volume
   *   stck_bsop_date → date (YYYYMMDD)
   *
   * @param {Object[]|Object} raw  API 배열 or { output2: [...] }
   * @returns {Object[]} 표준화 배열 { date, time, open, high, low, close, volume,
   *                                    ma5, ma10, ma20, ma60, ma120,
   *                                    bbUpper, bbMiddle, bbLower,
   *                                    rsi, macd, macdSignal, macdHist }
   */
  function normalizeChartData(raw) {
    // output2 래핑 처리
    let list = Array.isArray(raw) ? raw : (raw && raw.output2 ? raw.output2 : []);

    if (!list || list.length === 0) return [];

    // 정렬: 오래된 것 → 최신 (시간순)
    list = list.slice().sort(function (a, b) {
      const da = String(a.stck_bsop_date || a.date || '');
      const db = String(b.stck_bsop_date || b.date || '');
      return da.localeCompare(db);
    });

    // 기본 필드 정규화
    const normalized = list.map(function (item) {
      const dateRaw = item.stck_bsop_date || item.date || '';
      return {
        date:   fmtDate(dateRaw),
        time:   item.stck_cntg_hour || item.time || '',
        open:   parseFloat(item.stck_oprc  || item.open  || 0),
        high:   parseFloat(item.stck_hgpr  || item.high  || 0),
        low:    parseFloat(item.stck_lwpr  || item.low   || 0),
        close:  parseFloat(item.stck_clpr  || item.close || 0),
        volume: parseFloat(item.acml_vol   || item.volume || 0),
        // 이미 API가 제공하는 경우 그대로 수용
        ma5:    item.ma5   !== undefined ? parseFloat(item.ma5)   : null,
        ma10:   item.ma10  !== undefined ? parseFloat(item.ma10)  : null,
        ma20:   item.ma20  !== undefined ? parseFloat(item.ma20)  : null,
        ma60:   item.ma60  !== undefined ? parseFloat(item.ma60)  : null,
        ma120:  item.ma120 !== undefined ? parseFloat(item.ma120) : null,
        bbUpper:  item.bbUpper  !== undefined ? parseFloat(item.bbUpper)  : null,
        bbMiddle: item.bbMiddle !== undefined ? parseFloat(item.bbMiddle) : null,
        bbLower:  item.bbLower  !== undefined ? parseFloat(item.bbLower)  : null,
        rsi:        item.rsi        !== undefined ? parseFloat(item.rsi)        : null,
        macd:       item.macd       !== undefined ? parseFloat(item.macd)       : null,
        macdSignal: item.macdSignal !== undefined ? parseFloat(item.macdSignal) : null,
        macdHist:   item.macdHist   !== undefined ? parseFloat(item.macdHist)   : null,
      };
    });

    return normalized;
  }

  /* ─────────────────────────────────────────────
   * 지표 자동 보완
   * ───────────────────────────────────────────── */

  /**
   * ensureIndicators(data)
   * API에서 지표 미제공 시 자동 계산 fallback.
   * normalizeChartData() 결과를 받아 null인 지표를 채워 반환.
   *
   * @param {Object[]} data  normalizeChartData() 결과
   * @returns {Object[]}     지표가 채워진 배열 (원본 변이 없음)
   */
  function ensureIndicators(data) {
    if (!data || data.length === 0) return [];

    const closes = data.map(function (d) { return d.close; });

    // MA
    const needMA5   = data.some(function (d) { return d.ma5   === null; });
    const needMA10  = data.some(function (d) { return d.ma10  === null; });
    const needMA20  = data.some(function (d) { return d.ma20  === null; });
    const needMA60  = data.some(function (d) { return d.ma60  === null; });
    const needMA120 = data.some(function (d) { return d.ma120 === null; });

    const ma5arr   = needMA5   ? calcMA(closes, 5)   : null;
    const ma10arr  = needMA10  ? calcMA(closes, 10)  : null;
    const ma20arr  = needMA20  ? calcMA(closes, 20)  : null;
    const ma60arr  = needMA60  ? calcMA(closes, 60)  : null;
    const ma120arr = needMA120 ? calcMA(closes, 120) : null;

    // BB
    const needBB = data.some(function (d) { return d.bbUpper === null; });
    const bbResult = needBB ? calcBB(closes, 20, 2) : null;

    // RSI
    const needRSI = data.some(function (d) { return d.rsi === null; });
    const rsiArr  = needRSI ? calcRSI(closes, 14) : null;

    // MACD
    const needMACD  = data.some(function (d) { return d.macd === null; });
    const macdResult = needMACD ? calcMACD(closes, 12, 26, 9) : null;

    return data.map(function (item, i) {
      const out = Object.assign({}, item);
      if (needMA5   && ma5arr)   out.ma5   = ma5arr[i];
      if (needMA10  && ma10arr)  out.ma10  = ma10arr[i];
      if (needMA20  && ma20arr)  out.ma20  = ma20arr[i];
      if (needMA60  && ma60arr)  out.ma60  = ma60arr[i];
      if (needMA120 && ma120arr) out.ma120 = ma120arr[i];
      if (needBB && bbResult) {
        out.bbUpper  = bbResult.upper[i];
        out.bbMiddle = bbResult.middle[i];
        out.bbLower  = bbResult.lower[i];
      }
      if (needRSI && rsiArr) out.rsi = rsiArr[i];
      if (needMACD && macdResult) {
        out.macd       = macdResult.macd[i];
        out.macdSignal = macdResult.signal[i];
        out.macdHist   = macdResult.histogram[i];
      }
      return out;
    });
  }

  /* ─────────────────────────────────────────────
   * Export
   * ───────────────────────────────────────────── */

  global.KWIndicators = {
    calcMA:             calcMA,
    calcEMA:            calcEMA,
    calcBB:             calcBB,
    calcRSI:            calcRSI,
    calcMACD:           calcMACD,
    normalizeChartData: normalizeChartData,
    ensureIndicators:   ensureIndicators,
    fmt:                fmt,
    fmtPct:             fmtPct,
    fmtDate:            fmtDate,
  };

})(typeof window !== 'undefined' ? window : (typeof global !== 'undefined' ? global : this));
```

---

## 검증 결과

```
$ ls -la /root/kis-autotrade-v4/frontend/static/js/kw-indicators.js
-rw-rw-r-- 1 claudebot claudebot 15282 Mar  8 08:38 /root/kis-autotrade-v4/frontend/static/js/kw-indicators.js

$ grep "window.KWIndicators" /root/kis-autotrade-v4/frontend/static/js/kw-indicators.js
 * - window.KWIndicators 로 export

$ grep -c "function calc" /root/kis-autotrade-v4/frontend/static/js/kw-indicators.js
5
```

| 검증 항목 | 기대 | 실제 | 결과 |
|-----------|------|------|------|
| 파일 존재 | 존재 | 15282 bytes | PASS |
| window.KWIndicators 포함 | 있음 | 있음 | PASS |
| function calc 개수 | 5 이상 | 5 (calcMA, calcEMA, calcBB, calcRSI, calcMACD) | PASS |

---

## 구현된 함수 목록

| 함수명 | 설명 |
|--------|------|
| `calcMA(data, period)` | 단순 이동평균 (SMA) |
| `calcEMA(data, period)` | 지수이동평균 (EMA) |
| `calcBB(data, period=20, mult=2)` | 볼린저밴드 (upper/middle/lower) |
| `calcRSI(data, period=14)` | RSI (Wilder's Smoothing) |
| `calcMACD(data, fast=12, slow=26, signal=9)` | MACD line/signal/histogram |
| `normalizeChartData(raw)` | KIS API 응답 → 표준화 (KIS 필드명 호환) |
| `ensureIndicators(data)` | API 미제공 지표 자동 계산 fallback |
| `fmt(n)` | 숫자 천단위 포맷 (ko-KR) |
| `fmtPct(n)` | +0.00% 형식 |
| `fmtDate(d)` | YYYY-MM-DD 형식 (YYYYMMDD 자동 변환 포함) |

## 최종 상태

- 파일: `/root/kis-autotrade-v4/frontend/static/js/kw-indicators.js` (15,282 bytes)
- export: `window.KWIndicators` (IIFE 패턴, Node.js global 호환)
- 의존성: 없음 (순수 JS, 브라우저 단독 실행 가능)
- KIS API 필드 호환: stck_oprc/stck_hgpr/stck_lwpr/stck_clpr/acml_vol/stck_bsop_date

## STATUS: COMPLETE
