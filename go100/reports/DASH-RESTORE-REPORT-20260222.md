# DASH-RESTORE 결과 보고 (STEP 2·3 완료, 복구 실행 대기)

**작업일**: 2026-02-22  
**서버**: 211.188.51.113  
**경로**: /root/kis-autotrade-v4  

---

## ★ 사전 확인 결과 (기준 충족)

| 항목 | 기준 | 결과 |
|------|------|------|
| strategy_cards COUNT | 59 | **59** ✓ |
| v4_positions OPEN | 5 | **5** ✓ |
| kis-v41-api | active (running) | **running** ✓ |
| kis-v41-monitor | active (running) | **running** ✓ |
| kis-v41-scheduler | active (running) | **running** ✓ |
| df -h / | 여유 확인 | **45% 사용, 53G 여유** ✓ |

---

## STEP 1: 백업 완료

- 디렉터리: `/root/backups/dashboard_restore_20260222/`
- 백업 내용:
  - `frontend_dashboard_new/` — `frontend/dashboard/` 전체 복사
  - `main.py.bak` — `backend/app/main.py` 복사

---

## STEP 2: 레거시 대시보드 파일 위치 및 서빙 방식

### (A) 레거시 dashboard 파일 위치

| 위치 | 설명 |
|------|------|
| **/var/www/trading.newtalk.kr/dashboard.html** | **실제 서빙되는 레거시 파일** (nginx root). 포트폴리오/실시간 거래/전략 관리/WaveRider v5/리포트/관리자 메뉴 포함. |
| **/root/kis-autotrade-v4/frontend/dashboard/dashboard_prod.html** | 레거시 UI와 동일한 내용의 소스 파일 (같은 레거시 UI). |
| frontend/.next/server/app/dashboard.html | Next.js 빌드 산출물(새 UI). 레거시 아님. |

### (B) 9ca0377b 이전 main.py

- `dashboard` 관련: `dashboard_v1_router`, `v4_dashboard` 라우터, `/static/v4-dashboard` 마운트만 존재.
- **/dashboard 경로 마운트 없음.**

### (C) 8001(kis-webapp-api)에서 dashboard.html

- `curl http://localhost:8001/dashboard.html` → **404** (해당 경로 없음).
- 레거시는 **8001에서 서빙되지 않음**.

### (D) 레거시 서빙 방식 (결론)

- **원래(20260221 백업 설정 기준)**: nginx **root 직접 서빙**.  
  - `root /var/www/trading.newtalk.kr;` + `try_files $uri $uri/ /index.html;`  
  - `/dashboard.html` 요청 → `/var/www/trading.newtalk.kr/dashboard.html` 정적 파일로 응답.  
  - **location /dashboard.html, /dashboard/ 없음** (백업 설정에는 이 location들이 없음).
- **현재**: nginx에 `location = /dashboard.html` 및 `location /dashboard/` 가 **8003으로 프록시**되도록 추가됨.  
  - 따라서 `/dashboard.html`, `/dashboard/` 접근 시 **8003** → FastAPI의 `app.mount("/dashboard", frontend/dashboard)` → **새 UI**(index.html)가 응답함.  
  - 레거시 파일은 **nginx root에 그대로 있으나**, 현재 설정 때문에 **요청이 8003으로 가서 새 UI가 나오는 상태**.

---

## STEP 3: 9ca0377b 변경 내용

### git show --stat 9ca0377b

- **backend/app/main.py**: +8줄 (v4_alert_api 라우터 추가 + **/dashboard 마운트 추가**).
- **frontend/dashboard/**: app.js, index.html, style.css 신규 추가.
- 기타: v4_signal_api, backfill_signals, 리포트 등.

### git diff 9ca0377b^..9ca0377b -- backend/app/main.py

**추가된 블록:**

```python
# V4.1 웹 대시보드 (작업지시서 #2026-0220-N 작업B): /dashboard → frontend/dashboard
_dashboard_dir = Path(__file__).resolve().parent.parent.parent / "frontend" / "dashboard"
if _dashboard_dir.is_dir():
    app.mount("/dashboard", StaticFiles(directory=str(_dashboard_dir), html=True), name="dashboard")
```

- 즉, **9ca0377b에서** FastAPI에 `app.mount("/dashboard", ... frontend/dashboard)` 가 추가되어, `/dashboard`·`/dashboard/` 요청이 **새 UI**(frontend/dashboard/index.html)로 가게 됨.
- nginx가 `/dashboard.html` → `8003/dashboard/` 로 보내고 있어, **레거시가 아닌 새 UI**가 노출됨.

---

## 복구 방법 제안 (CEO 승인 후 적용)

- **레거시 파일 위치**: 이미 **nginx root** (`/var/www/trading.newtalk.kr/dashboard.html`)에 있음.  
- **복구**: 9ca0377b에서 바뀐 **경로를 되돌려** `/dashboard.html`·`/dashboard/` 가 다시 **레거시**로 가도록 하면 됨.

### 권장: **경로 A + nginx 복구**

1. **main.py**  
   - 9ca0377b에서 추가한 **/dashboard 마운트 4줄 제거** (주석 또는 삭제).  
   - 그러면 8003에는 `/dashboard` 마운트가 없어지고, nginx가 8003으로 보내도 404가 남 (또는 아래 2에서 8003으로 안 보내면 됨).

2. **nginx**  
   - **제거할 location**:  
     - `location = /dashboard.html { ... proxy_pass http://127.0.0.1:8003/dashboard/; ... }`  
     - `location /dashboard/ { ... proxy_pass http://127.0.0.1:8003/dashboard/; ... }`  
     - (선택) 대시보드용 `location = /style.css`, `location = /app.js` → 8003/dashboard 로 가는 두 블록.  
   - 이렇게 제거하면 `try_files $uri $uri/ /index.html` 에 의해  
     - `/dashboard.html` → **/var/www/trading.newtalk.kr/dashboard.html** (레거시) 서빙.  
     - `/dashboard/` 는 root에 디렉터리가 없으면 `index.html`로 폴백될 수 있음.  
   - 레거시 진입이 **/dashboard.html** 이라면 위만으로도 레거시 UI 복구 완료.

3. **frontend/dashboard/ (새 UI) 비활성화**  
   - **경로 C** 참고: 필요 시 `mv frontend/dashboard frontend/dashboard_v41_new_backup` 으로 이름 변경하여, 향후 main.py에 다시 마운트하지 않으면 새 UI는 사용 중지.  
   - 복구 목적이 “레거시만 다시 보이게”이면 **main.py 마운트 제거 + nginx location 제거**만으로 가능하고, 디렉터리 이름 변경은 선택 사항.

### 요약

| 구분 | 내용 |
|------|------|
| **레거시 대시보드 파일 위치** | `/var/www/trading.newtalk.kr/dashboard.html` (동일 소스: `frontend/dashboard/dashboard_prod.html`) |
| **레거시 서빙 방식** | **원래**: nginx root 직접 서빙. **현재**: 8003 프록시로 인해 새 UI가 나옴. |
| **9ca0377b 변경 내용** | main.py에 `/dashboard` → `frontend/dashboard` StaticFiles 마운트 추가. |
| **복구 방법** | **경로 A + nginx**: main.py에서 /dashboard 마운트 제거 + nginx에서 /dashboard.html, /dashboard/ (및 필요 시 /style.css, /app.js) location 제거 → /dashboard.html은 root의 레거시 파일로 다시 서빙. |
| **복구 실행 여부** | **CEO 승인 대기** (STEP 4~6 미실행). |
| **검증 결과** | 복구 실행 후 진행 예정. |
| **strategy_cards COUNT** | 59 ✓ |
| **v4_positions OPEN** | 5 ✓ |
| **커밋** | 복구 실행 후 커밋 예정. |

---

## ★ 다음 단계 (CEO 승인 후)

1. **STEP 4**: 위 복구 방법(경로 A + nginx)으로 수정 적용.  
2. **STEP 5**: main.py 수정 시 `python -m py_compile backend/app/main.py` 실행, 커밋 전 `git diff --cached | grep -i "\.env|\.bak"` 확인, DB 무결성 재확인.  
3. **STEP 6**: **kis-v41-api 재시작은 CEO 명시적 허가 시에만** (main.py 변경 시 필요하므로 보고 후 허가 받을 것).  
4. **STEP 7**:  
   - `curl -s http://localhost:8003/dashboard/` (필요 시),  
   - `curl -s https://trading41.newtalk.kr/dashboard.html | head -50`  
   - 레거시 UI 키워드 확인: "포트폴리오", "실시간 거래", "전략 관리", "WaveRider", "리포트", "관리자".

--- 보고 끝 ---

---

# DASH-RESTORE-EXEC 결과 (실행 완료)

**실행일시**: 2026-02-22  
**서버**: 211.188.51.113  
**경로**: /root/kis-autotrade-v4  

---

## 실행 결과 요약

| 항목 | 결과 |
|------|------|
| main.py /dashboard 마운트 | **제거완료** (주석처리) |
| nginx dashboard location | **제거완료** (80·443 서버블록 모두) |
| nginx -t | **ok** |
| frontend/dashboard | **이동완료** → frontend/dashboard_v41_new_backup |
| kis-v41-api 재시작 | **성공**, active (running) |
| nginx reload | **성공** |
| 레거시 UI 복구 확인 | **Y** |
| curl /dashboard.html 키워드 | **포트폴리오/실시간거래/전략관리/WaveRider/리포트** — 확인됨 |
| localhost:8003/health | **200** (status ok) |
| strategy_cards COUNT | **59** ✓ |
| v4_positions OPEN | **5** ✓ |
| 커밋 해시 | **7b75221e** |
| 이슈 사항 | **없음** |

---

## 상세

- **백업**: `/root/backups/dashboard_restore_20260222/` 에 `nginx_kis-autotrade.bak` 추가 보관.
- **대시보드 API** `GET /api/v4/dashboard/overview`: 401 (미인증 시 정상).
- **kis-v41-monitor, kis-v41-scheduler**: 재시작 없음 (지시 준수).

--- DASH-RESTORE-EXEC 보고 끝 ---
