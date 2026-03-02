# DESK2-BT-CHART-DASHBOARD-HOTFIX-001 — 대시보드 데이터 미표시 수정

**Task ID:** DESK2-BT-CHART-DASHBOARD-HOTFIX-001  
**우선순위:** P0-URGENT  
**일시:** 2026-02-27  
**규칙:** kis-v41-api / monitor / scheduler 재시작 금지

---

## 1. 진단 결과

### STEP 1 — API 진단

| 항목 | 결과 |
|------|------|
| API 라우터 등록 | `main.py` 83행·411행에 `v4_desk2_backtest_router` 등록됨 (`prefix=/api/v4/desk2-backtest`) |
| `GET /api/v4/desk2-backtest/sessions` | `curl` 시 연결 거부 (HTTP_CODE: 000) |
| `systemctl is-active kis-v41-api` | **inactive** |

**결론:** API는 코드 상 등록되어 있으나 **kis-v41-api 서비스가 비가동** 상태라 동적 API 호출 불가.

### STEP 2 — DB 데이터 존재 확인

| 항목 | 결과 |
|------|------|
| DESK2 세션 수 | 37건 (desk_id='2' OR session_id LIKE 'BT-DESK2%' OR strategy_name LIKE 'DESK2%' OR strategy_name LIKE 'P0FIX%') |
| DESK2 거래 수 | 196건 |
| 날짜 범위 | 2026-01-01 ~ 2026-02-25 |

**결론:** DB에 DESK2 백테스트 데이터 충분히 존재. 원인은 **API 서버 미기동**으로 프론트가 데이터를 가져오지 못한 것.

### STEP 3 — 프론트엔드

- `desk2-backtest.html` → `/js/desk2-backtest.js` 로드.
- JS는 `API_BASE = '/api/v4/desk2-backtest'` 로 `fetch('/sessions?limit=100')`, `/summary`, `/sessions/{id}/trades`, `/trades/{id}/chart-data` 호출.
- API 서버가 꺼져 있어 모든 요청 실패 → 대시보드에 데이터 미표시.

---

## 2. 원인

- **근본 원인:** kis-v41-api 서비스 **inactive**.
- **규칙:** 해당 작업 지침에 따라 API/모니터/스케줄러 **재시작 금지**.
- 따라서 **Case B** 적용: API 서버 없이 동작하도록 **정적 JSON 방식**으로 전환.

---

## 3. 수정 내역

### 3.1 정적 데이터 생성 스크립트 (신규)

| 파일 | 설명 |
|------|------|
| `scripts/desk2_static_data_gen.py` | DB에서 DESK2 세션·거래·집계를 읽어 정적 JSON 생성 |

**생성 파일:**

- `{DESK2_STATIC_OUT}/desk2-bt-data.json`  
  - `sessions`: 세션 목록 (API 응답 형식)  
  - `trades`: 전체 거래 목록 (session_id 포함, 프론트에서 필터)  
  - `summary`: 총 세션 수, 총 거래 수, 승률 평균, 총 수익률 합, PF 평균  
- `{DESK2_STATIC_OUT}/desk2-charts/trade_{safe_trade_id}.json`  
  - 거래별 분봉(candles) + 진입/청산 마커(markers), API `/trades/{id}/chart-data` 형식  

**실행:**

```bash
cd /root/kis-autotrade-v4 && source .venv/bin/activate
DESK2_STATIC_OUT=/var/www/trading.newtalk.kr python3 scripts/desk2_static_data_gen.py
```

- 기본 `DESK2_STATIC_OUT`은 `/var/www/trading.newtalk.kr`.
- 생성 결과: sessions=37, trades=196, 차트 JSON 196개.

### 3.2 프론트엔드 JS 수정 (정적 JSON 우선 사용)

| 파일 | 변경 내용 |
|------|-----------|
| `frontend/static/desk2-backtest.js` | 정적 데이터 URL·차트 URL 추가, 정적 우선 로직 |
| `frontend/static/js/desk2-backtest.js` | 위와 동일 내용으로 동기화 (배포 시 복사 대상) |

**로직 요약:**

- `useStaticData = true` 로 시작.
- **세션/집계:** `GET /desk2-bt-data.json` → `data.sessions`, `data.summary` 사용.
- **거래 목록:** 동일 JSON의 `data.trades`를 세션 선택 시 `session_id`로 필터하여 표시.
- **차트:** `GET /desk2-charts/trade_{safeTradeId}.json` (trade_id에서 파일명 부적합 문자 `_`로 치환).
- 정적 요청 실패 시 `useStaticData = false` 로 전환 후 기존 API 호출로 폴백.

### 3.3 배포 스크립트

| 파일 | 변경 내용 |
|------|-----------|
| `scripts/deploy_static.sh` | 배포 후 `DESK2_STATIC_OUT="$DST"` 로 정적 JSON 생성 스크립트 실행 추가. 검증에 `desk2-backtest.html`, `desk2-bt-data.json` 확인 추가. |

---

## 4. 최종 작동 상태

| 검증 항목 | 결과 |
|-----------|------|
| `curl -s -o /dev/null -w "%{http_code}" https://trading41.newtalk.kr/desk2-backtest.html` | **200** |
| `curl -s https://trading41.newtalk.kr/desk2-bt-data.json` → sessions/trades 개수 | **Sessions: 37, Trades: 196** |
| kis-v41-api | **inactive** (재시작 없음) |
| 대시보드 데이터 표시 | 정적 JSON으로 **표시됨** |

---

## 6. URL 및 배포 검증

- **대시보드:** https://trading41.newtalk.kr/desk2-backtest.html  
- **정적 데이터:** https://trading41.newtalk.kr/desk2-bt-data.json  
- **거래 차트 예:** https://trading41.newtalk.kr/desk2-charts/trade_{trade_id_safe}.json  

**배포 후 검증 명령:**

```bash
bash scripts/deploy_static.sh
# 검증
curl -s https://trading41.newtalk.kr/desk2-bt-data.json | python3 -c "import sys,json; d=json.load(sys.stdin); print('Sessions:', len(d['sessions']), 'Trades:', len(d['trades']))"
curl -s -o /dev/null -w "%{http_code}" https://trading41.newtalk.kr/desk2-backtest.html
```

---

## 7. 참고

- API 서버(kis-v41-api)가 다시 기동되면, 현재 JS는 정적 데이터 요청 실패 시 자동으로 기존 `/api/v4/desk2-backtest/*` API로 폴백함.
- 정적 데이터 갱신: 배포 시 `deploy_static.sh` 가 자동 실행하거나, 수동으로 `scripts/desk2_static_data_gen.py` 실행.
