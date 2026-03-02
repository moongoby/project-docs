# DESK2-BT-CHART-DASHBOARD-001 — 백테스트 메뉴 라우팅 수정 + Plotly HTML 차트 + DESK2 대시보드

**일시:** 2026-02-27  
**서버:** [SERVER-IP]  
**브랜치:** phase-2c-command-center  
**작업 ID:** DESK2-BT-CHART-DASHBOARD-001 (P0)

---

## Phase 0: 백테스트 메뉴 라우팅 수정

### 문제
- admin.html 좌측 메뉴 "백테스트 분석" 클릭 시 `https://go100.newtalk.kr/admin/backtest`로 이동됨.

### 수정 내역
| 항목 | Before | After |
|------|--------|--------|
| 링크 | `https://go100.newtalk.kr/admin/backtest` | `/admin/desk2-backtest.html` |
| 파일 | `frontend/static/admin.html` (184행) | 동일 파일, href만 변경 |

### 백업
- `admin.html.bak.(YYYYMMDDHHMM)` 생성 후 수정.

### 검증
- 수정 후 해당 링크는 현재 도메인 기준 `/admin/desk2-backtest.html`을 가리킴 (trading41.newtalk.kr에서 서빙 시 동일 도메인 페이지로 이동).

---

## Phase A: Plotly HTML 차트 생성 (즉시 조회용)

### 생성 파일
- **스크립트:** `scripts/backtest/desk2_trade_chart.py`

### 기능
- `v4_bt_trades` + `v4_ohlcv_minute` 조합으로 **종목당 1개 HTML** 생성.
- 메인: 당일 분봉 캔들, 진입/청산 화살표, stop_loss/target_price/first_target_price/trailing_stop 수평선, VWAP(주황 점선), 볼린저 밴드, 진입~청산 구간 배경 하이라이트.
- 서브: 거래량 바.
- 정보 패널: 종목, 전략, 발굴조건, DESK/CS Score, 진입/청산 시각·가격, PnL, 보유시간, 청산 후 30분 고가, 기회손실.

### 사용법
```bash
# 전체 거래 차트 생성
python3 scripts/backtest/desk2_trade_chart.py --session-name "P0FIX" --output /tmp/desk2_charts/ --all

# 특정 거래만
python3 scripts/backtest/desk2_trade_chart.py --session-name "P0FIX" --output /tmp/desk2_charts/ --trade-id "T-xxx"
```

### 출력
- `{output}/index.html` — 거래 목록 테이블(날짜, 종목, 전략, PnL, 링크).
- `{output}/trade_001_{stock_code}_{YYYYMMDD}.html` — 종목별 차트.

### 웹 접근 (배포 시)
```bash
cp -r /tmp/desk2_charts/ /var/www/trading.newtalk.kr/desk2-charts/
```
- **접근 URL:** `https://trading41.newtalk.kr/desk2-charts/index.html` (배포 후 검증: `curl -s -o /dev/null -w "%{http_code}" https://trading41.newtalk.kr/desk2-charts/index.html` → 200)

### 라이브러리
- plotly (pip install plotly), psycopg2-binary.

---

## Phase B: DESK2 백테스트 대시보드

### B-1. 백엔드 API (prefix: `/api/v4/desk2-backtest`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/sessions` | v4_bt_sessions (DESK2 세션) 목록, `started_at DESC` |
| GET | `/sessions/{session_id}/trades` | v4_bt_trades 목록 |
| GET | `/sessions/{session_id}/discoveries` | v4_bt_discoveries 목록 |
| GET | `/trades/{trade_id}/chart-data` | v4_ohlcv_minute 분봉 + 진입/청산 마커 |
| GET | `/summary` | 전체 집계(총 세션, 거래수, 승률, 총 수익률, PF) |

- **파일:** `backend/app/api/v4_desk2_backtest.py` (신규).
- **main.py:** `include_router(v4_desk2_backtest_router)` 1줄 추가.

### B-2. 프론트엔드

| 파일 | 설명 |
|------|------|
| `frontend/static/desk2-backtest.html` | 대시보드 페이지 구조(헤더, 툴바, 요약 카드, 세션/거래 테이블, 차트 영역) |
| `frontend/static/js/desk2-backtest.js` | API 호출, 테이블 렌더링, Plotly.js 캔들+마커 차트 |
| `frontend/static/css/desk2-backtest.css` | admin 스타일 통일(보라 그라데이션 카드, 흰색 배경) |

- 차트: Plotly.js CDN (`https://cdn.plot.ly/plotly-2.27.0.min.js`).

### B-3. admin 메뉴 연동
- Phase 0에서 "백테스트 분석" → `/admin/desk2-backtest.html` 로 이미 변경됨.

### B-4. 배포
```bash
bash scripts/deploy_static.sh
```
- `deploy_static.sh`에 `desk2-backtest.html`, `desk2-backtest.js`, `desk2-backtest.css` 복사 및 백업 추가됨.

### 검증
- `curl -s -o /dev/null -w "%{http_code}" https://trading41.newtalk.kr/admin/desk2-backtest.html` → 200 (배포 및 nginx 설정 후).

---

## 수정/추가된 파일 전체 목록

| 경로 | 변경 |
|------|------|
| `frontend/static/admin.html` | 백테스트 메뉴 링크 수정 |
| `frontend/static/admin.html.bak.(timestamp)` | 백업(Phase 0) |
| `scripts/backtest/desk2_trade_chart.py` | 신규 |
| `backend/app/api/v4_desk2_backtest.py` | 신규 |
| `backend/app/main.py` | import 1줄, include_router 1줄 추가 |
| `frontend/static/desk2-backtest.html` | 신규 |
| `frontend/static/js/desk2-backtest.js` | 신규 |
| `frontend/static/css/desk2-backtest.css` | 신규 |
| `scripts/deploy_static.sh` | desk2-backtest 관련 복사/백업/검증 추가 |

---

## 검증 결과

- **Phase 0:** admin.html 내 백테스트 링크 → `/admin/desk2-backtest.html` 확인.
- **Phase A:** 스크립트 실행 시 HTML/ index 생성 가능 (DB에 v4_bt_sessions/v4_bt_trades/v4_ohlcv_minute 데이터 필요).
- **Phase B:** API 엔드포인트 5개 정의, 프론트 3파일 추가, main.py 2줄 추가만 수행. 배포 스크립트 실행 후 정적 파일 서빙 및 대시보드 URL 접근 확인 권장.

---

## 주의사항

- kis-v41-api / monitor / scheduler **재시작하지 않음**.
- strategy_cards **ALTER/DROP/DELETE 없음**. v4_positions 직접 수정 없음.
- go100_* 테이블 **SELECT 전용**. v4_bt_* 테이블에만 INSERT.
- admin.html 백업 보존, 문제 시 `.bak` 복원 가능.
- main.py 기존 코드 변경 없이 **라우터 1줄 추가만** 적용.
