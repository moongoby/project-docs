# DESK2-BT-DASHBOARD-DATA-FIX-001 — 대시보드 데이터 미조회 조치

**Task ID:** DESK2-BT-DASHBOARD-DATA-FIX-001  
**일시:** 2026-02-27  
**대상 페이지:** https://trading41.newtalk.kr/desk2-backtest.html (DESK2 백테스트 분석 대시보드)

---

## 1. 현상

- 대시보드에서 **요약 지표(총 세션, 총 거래, 승률, 수익률, PF)**, **세션 목록**, **거래 목록**, **차트**가 모두 비어 있음.
- DB 및 백테스트 실행 이력은 쌓여 있는 상태에서 해당 페이지에만 데이터가 조회되지 않음.

---

## 2. 원인 분석

### 2.1 데이터 제공 구조 (DESK2-BT-CHART-DASHBOARD-HOTFIX-001 기준)

- **API 서버(kis-v41-api)** 가 동작 중이면: `/api/v4/desk2-backtest/sessions`, `/summary` 등으로 데이터 제공.
- **API 서버 미가동 시**: 정적 JSON(`/desk2-bt-data.json`, `/desk2-charts/trade_*.json`)으로 대시보드 데이터 제공하도록 HOTFIX 적용됨.

### 2.2 실제 원인

| 구분 | 내용 |
|------|------|
| **배포 대상 JS** | `desk2-backtest.html` 이 로드하는 스크립트는 **`/js/desk2-backtest.js`** (배포 시 `frontend/static/js/desk2-backtest.js` 복사). |
| **정적 데이터 로직 위치** | HOTFIX-001 정적 JSON 우선 로직은 **`frontend/static/desk2-backtest.js`** 에만 반영되어 있었음. |
| **결과** | **`frontend/static/js/desk2-backtest.js`** 에는 정적 데이터 요청(`/desk2-bt-data.json`) 및 폴백 로직이 없어, API만 호출. API 서버가 비가동이면 모든 요청 실패 → 화면에 데이터 미표시. |

즉, **배포에 사용되는 JS 파일과 정적 데이터 로직이 적용된 JS 파일이 불일치**하여, 실제 서비스에서는 정적 JSON을 사용하지 못한 상태였음.

---

## 3. 조치 내역

### 3.1 코드 수정

| 파일 | 조치 |
|------|------|
| `frontend/static/js/desk2-backtest.js` | **`frontend/static/desk2-backtest.js`** 와 동일한 내용으로 교체. 정적 데이터 우선 로직 포함. |

**적용된 로직 요약:**

- `useStaticData = true` 로 시작.
- **세션/집계:** `GET /desk2-bt-data.json` → `data.sessions`, `data.summary` 사용.
- **거래 목록:** 동일 JSON의 `data.trades`를 세션 선택 시 `session_id`로 필터하여 표시.
- **차트:** `GET /desk2-charts/trade_{safeTradeId}.json` 사용.
- 정적 요청 실패 시 `useStaticData = false` 로 전환 후 기존 API(`/api/v4/desk2-backtest/*`) 호출로 폴백.

### 3.2 배포 및 정적 데이터 생성

- **배포 스크립트:** `scripts/deploy_static.sh`  
  - `frontend/static/` → `DST`(기본값 `/var/www/trading.newtalk.kr`) 로 HTML/JS/CSS 복사.
  - 배포 후 **`scripts/desk2_static_data_gen.py`** 를 `DESK2_STATIC_OUT="$DST"` 로 실행하여 **`desk2-bt-data.json`** 및 **`desk2-charts/trade_*.json`** 생성.
- **실서비스 반영:** 수정된 `js/desk2-backtest.js` 반영 후, **배포 서버에서 `bash scripts/deploy_static.sh` 실행** 필요.

---

## 4. 배포 후 확인 방법

```bash
# 1) 정적 파일 배포 및 정적 JSON 생성
cd /root/kis-autotrade-v4 && bash scripts/deploy_static.sh

# 2) 대시보드 페이지 접근 가능 여부
curl -s -o /dev/null -w "%{http_code}" https://trading41.newtalk.kr/desk2-backtest.html
# 기대: 200

# 3) 정적 데이터 존재 및 개수 확인
curl -s https://trading41.newtalk.kr/desk2-bt-data.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('Sessions:', len(d.get('sessions',[])), 'Trades:', len(d.get('trades',[])))"
# 기대: Sessions: N, Trades: M (N, M > 0)
```

브라우저에서 https://trading41.newtalk.kr/desk2-backtest.html 접속 후:

- 요약 카드에 총 세션/총 거래/승률/수익률/PF 값 표시
- 세션 목록 테이블에 행 표시
- 세션 클릭 시 거래 목록 표시, 거래 클릭 시 분봉 차트 표시

---

## 5. 요약

| 항목 | 내용 |
|------|------|
| **원인** | 배포용 JS(`js/desk2-backtest.js`)에 정적 데이터 로직 미반영 → API 미가동 시 데이터 미표시 |
| **조치** | `js/desk2-backtest.js`를 정적 데이터 우선 버전(`desk2-backtest.js`)과 동기화 |
| **배포** | `deploy_static.sh` 실행으로 수정 JS 반영 + `desk2-bt-data.json` 및 차트 JSON 재생성 |
| **참고** | API 서버 기동 시에는 정적 요청 실패 시 자동으로 API로 폴백하므로 기존 동작 유지 |
