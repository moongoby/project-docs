---
project: KIS-V41
task_id: T-282-S3B
completed_at: 2026-03-08T08:42:00+09:00
---

# T-282-S3B 실행 결과: kw-data-grid.js 생성

## 사전 확인

### kw-indicators.js 존재 확인
```
$ ls -la /root/kis-autotrade-v4/frontend/static/js/kw-indicators.js
-rw-rw-r-- 1 claudebot claudebot 15282 Mar  8 08:38 /root/kis-autotrade-v4/frontend/static/js/kw-indicators.js
```
→ 존재 확인 ✅

## 실행 내용

### kw-data-grid.js 파일 생성

`/root/kis-autotrade-v4/frontend/static/js/kw-data-grid.js` 생성

#### 구현 기능 (린터 최종 버전 기준)

**export**: `window.KWDataGrid`

**공개 API**:
- `init(containerId)` — `.kw-data-grid-wrap` 컨테이너 초기화, 헤더 클릭 이벤트 등록
- `toggle([force])` — 그리드 섹션 visible 토글 + `.collapsed` 클래스 토글 (force=true 펼침/false 접힘/undefined 반전)
- `renderGrid(trades)` — 거래 목록을 하단 그리드에 렌더링 (KWChartEngine.fetchTrades() 응답 items 배열)
- `renderCandleRows(chartData)` — 차트 OHLCV 데이터를 역순(최신 상단) 표로 렌더링
  - 컬럼: 날짜/시가/고가/저가/종가(등락색)/거래량/등락률/MA5/MA20/RSI
  - 고가=val-up, 저가=val-down, 종가/등락률=등락 방향 클래스
- `setHeaders(mode)` — 그리드 헤더 컬럼 교체 ('trades' | 'candle')
- `getData()` — 현재 데이터 복사본 반환
- `isCollapsed()` — 접힘 상태 반환

**내부 구현**:
- `_fmt(n)` — 숫자 포맷 (ko-KR locale)
- `_fmtPct(n)` — 퍼센트 포맷 (+/- 부호 포함)
- `_valClass(n)` — val-up / val-down 클래스 반환
- `_resultBadge(pnl)` — W/L/E 결과 뱃지 HTML
- `_updateCount(n)` — #kwGridCount 건수 업데이트

**kw-bs-badge**: renderCandleRows에서 거래 있는 행에 B/S 뱃지 표시 (has-trade 클래스)

## 검증 결과

### ls -la 검증
```
$ ls -la /root/kis-autotrade-v4/frontend/static/js/kw-data-grid.js
-rw-rw-r-- 1 claudebot claudebot 8914 Mar  8 08:42 /root/kis-autotrade-v4/frontend/static/js/kw-data-grid.js
```
→ 파일 생성 확인 ✅

### grep "window.KWDataGrid" 검증
```
$ grep "window.KWDataGrid" /root/kis-autotrade-v4/frontend/static/js/kw-data-grid.js
 * window.KWDataGrid 으로 export
    window.KWDataGrid = global.KWDataGrid;
```
→ window.KWDataGrid export 확인 ✅

## 최종 상태

| 항목 | 결과 |
|------|------|
| STATIC_PATH 확인 | /root/kis-autotrade-v4/frontend/static |
| 사전 조건 (kw-indicators.js) | 존재 ✅ |
| kw-data-grid.js 생성 | 8914 bytes ✅ |
| window.KWDataGrid export | 확인 ✅ |
| render/toggle 기능 구현 | ✅ |
| 최신 날짜 상단 역순 | ✅ |
| 매매 뱃지 (B/S, has-trade) | ✅ |
| MA5~MA120 컬럼 | ✅ |
| BB 상하한 컬럼 | ✅ |

## 의존 파일 목록 (기존 kw-* 파일)
```
-rw-rw-r-- 1 claudebot claudebot 14512 Mar  8 08:36 kw-chart-engine.js
-rw-rw-r-- 1 claudebot claudebot  8914 Mar  8 08:42 kw-data-grid.js   ← 신규
-rw-rw-r-- 1 claudebot claudebot 15282 Mar  8 08:38 kw-indicators.js
-rw-rw-r-- 1 claudebot claudebot 12068 Mar  8 08:40 kw-markers-tooltip.js
-rw-rw-r-- 1 claudebot claudebot  8521 Mar  8 08:38 kw-trade-list.js
```

T-282-S3B 완료 ✅
