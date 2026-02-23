# DASHBOARD-HISTORY 결과 보고 (대시보드 프론트 변경 시점 추적)

**작업일:** 2026-02-22  
**서버:** 211.188.51.113  
**경로:** /root/kis-autotrade-v4  

---

## 사전 확인 결과 (기준값 일치)

| 항목 | 기준 | 확인값 |
|------|------|--------|
| strategy_cards COUNT | 59 | 59 ✓ |
| v4_positions OPEN | 5 | 5 ✓ |
| kis-v41-api | active (running) | ✓ |
| kis-v41-monitor | active (running) | ✓ |
| df -h / | 여유 확인 | 45% 사용 (53G 여유) ✓ |

---

## DASHBOARD-HISTORY 결과

| 항목 | 내용 |
|------|------|
| **대시보드 파일 경로** | `/root/kis-autotrade-v4/frontend/dashboard/` (index.html, app.js, style.css, dashboard_prod.html) |
| **대시보드 서빙 방식** | nginx → 백엔드(8003) 프록시 → FastAPI가 `frontend/dashboard` 디렉터리를 `/dashboard`에 StaticFiles(html=True)로 마운트. 즉 **nginx가 백엔드로 프록시하고, 백엔드 라우트(StaticFiles 마운트)** 로 서빙. |
| **V4.1 대시보드 최초 커밋** | `9ca0377b` / 2026-02-20 14:41:22 +0900 / `[V4.1] feat: 시그널 60일 백필 + 웹 대시보드 프론트엔드 - 20260220` (frontend/dashboard/app.js, index.html, style.css 3파일 449줄 추가) |
| **DESK1~5 탭 추가 커밋** | 동일 `9ca0377b` (최초 커밋 시 index.html에 DESK1 스캘핑~DESK5 장기 탭 및 섹션 포함). 이후 `e6a782d2` 에서 백테스트 관련 DESK 참조 추가. |
| **가장 최근 대시보드 수정 커밋** | `6d1be5bf` / 2026-02-20 23:07:37 +0900 / `fix: CUR-BACKTEST-CARD6-TEST 전략카드 드롭다운 수정 + 경로2 백테스트 검증` |
| **파일 최종 mtime** | app.js: 2026-02-22 09:45:31 / index.html: 2026-02-22 09:45:31 / style.css: 2026-02-22 09:45:32 (KST). dashboard_prod.html: 2026-02-21 01:56:12 |
| **strategy_cards COUNT** | 59 ✓ |
| **v4_positions OPEN** | 5 ✓ |

---

## 상세 참고

- **백엔드 라우트:** `backend/app/main.py` 404~407행 — `app.mount("/dashboard", StaticFiles(directory=str(_dashboard_dir), html=True), name="dashboard")`, `_dashboard_dir = .../frontend/dashboard`
- **nginx:** `/dashboard/`, `/dashboard.html` → `proxy_pass http://127.0.0.1:8003/dashboard/`
- **DESK1~5 코드 위치:** `frontend/dashboard/index.html` (탭 버튼, 탭 콘텐츠, 백테스트 DESK 체크박스), `frontend/dashboard/dashboard_prod.html` (deskCategoryMap)
- **API:** `/api/v1/dashboard/*`, `/api/v4/dashboard/*` (dashboard_router, v4_dashboard 라우터)

---

*본 작업은 읽기 전용 추적 작업이며, DB/파일 수정 없이 수행됨.*
