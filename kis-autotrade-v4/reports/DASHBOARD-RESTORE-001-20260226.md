# DASHBOARD-RESTORE-001-20260226

**제목**: 관리자 백테스트 대시보드 2차 덮어쓰기 복구 및 격리  
**일자**: 2026-02-26  
**유형**: 긴급 복구 + 규칙 반영

---

## 1. 원인 요약

- **BT-DASHBOARD-L1-VISUAL-001** 작업 과정에서 `admin.html`의 `#section-backtest`를 L1-1/L1-2/L1-3/L2 뷰용 div 구조로 **직접 교체**하고, `backtest-dashboard.js`를 **전면 재작성**함.
- **kis-v41-rules.md** 실패 교훈(2/20): *「신규 UI 별도 파일, 레거시 보존」* 위반 — 동일 실수 반복.
- 결과: 관리자 백테스트 메뉴가 기존 라우팅(GO100 링크 또는 KIS V4.1 자체 뷰) 대신 인라인 L1/L2 대시보드로 덮어씌워져, 기존 기능 소실 및 GO100 쪽으로 이동하는 현상으로 이어질 수 있는 상태 발생.

---

## 2. 복구 조치

### STEP 1 – 배포 경로 백업 복구 (완료)

| 항목 | 조치 |
|------|------|
| **admin.html** | `/var/www/trading.newtalk.kr/admin.html.bak.20260226_090211` → `admin.html` 로 복구 |
| **backtest-dashboard.js** | 배포 경로에 `.bak` 백업 없음 → 복구 생략 (레거시 admin이 해당 스크립트를 로드하지 않음) |

- 복구된 admin.html: 백테스트 메뉴는 **GO100 외부 링크**(`https://go100.newtalk.kr/admin/backtest`)만 포함, `#section-backtest` 인라인 섹션 없음.

### STEP 2 – 신규 대시보드 별도 파일 격리 (완료)

**배포 경로 (`/var/www/trading.newtalk.kr`)**  
- 복구 전 admin.html을 `admin-bt-v2.html`로 보존 시도했으나, 복구 전 서버 파일이 이미 레거시와 동일한 상태였음.  
- `backtest-dashboard.js` → `backtest-dashboard-v2.js` 로 복사하여 L1 시각화 스크립트 보존.

**워크스페이스 (`webapp/frontend`)**  
- **admin-bt-v2.html** 생성: 기존 admin.html(L1/L2 구조 포함)을 복사 후, `backtest-dashboard-v2.js` 로드하도록 수정.
- **backtest-dashboard-v2.js** 생성: 현재 `backtest-dashboard.js`(BT-DASHBOARD-L1-VISUAL-001 버전) 복사.
- **admin.html** 레거시 복구:
  - `#section-backtest` div 전체 제거.
  - 백테스트 메뉴를 **GO100 링크** + **백테스트 시각화 (V2)**(`admin-bt-v2.html`) 링크로 정리.
  - `backtest-dashboard.js` 스크립트 태그 제거.

### STEP 3 – nginx 라우팅 확인 (완료)

- **trading41.newtalk.kr** → `root /var/www/trading.newtalk.kr`, `/api/v4/` → **8003** (kis-v41-api), `/api/` → 8001.
- backtest/admin 전용 location은 없음. 정적 파일(admin.html, admin-bt-v2.html)은 동일 root에서 서빙.
- **KIS V4.1 라우팅이 GO100으로 빠지지 않음** 확인.

---

## 3. 확인 결과

| 확인 항목 | 결과 |
|-----------|------|
| admin.html 레거시 복구 | ✅ 백테스트 인라인 섹션 제거, GO100 링크 + V2 링크 유지 |
| 신규 L1/L2 대시보드 격리 | ✅ admin-bt-v2.html, backtest-dashboard-v2.js 별도 파일로 보존 |
| 배포 경로 admin 복구 | ✅ 백업(20260226_090211)으로 복구 완료 |
| backtest-dashboard.js 백업 | ⚠ 배포 경로에 백업 없음 — 레거시 JS는 미복구(admin이 로드하지 않음) |

---

## 4. 향후 규칙 반영 (kis-v41-rules.md)

다음 규칙을 **프론트엔드 수정 금지 규칙 (2026-02-26 CEO 지시)** 로 추가함:

1. **admin.html** 직접 교체/전면 재작성 **절대 금지**.
2. 기존 JS 파일(**backtest-dashboard.js** 등) 전면 재작성 금지 — 신규 기능은 **별도 파일**로 생성.
3. 공유 파일(`admin.html`, `backtest-dashboard.js`, `layout.tsx`, `page.tsx` 등) 수정 시 **반드시 CEO + Claude PM 사전 승인**.
4. 위반 시 **즉시 백업 복구 후 작업 롤백**.

---

## 5. 배포 시 참고

- **admin-bt-v2.html**, **backtest-dashboard-v2.js** 를 배포 스크립트/체크리스트에 포함할 것.
- `trading41.newtalk.kr/admin.html` → 레거시(GO100 링크 + V2 링크).
- `trading41.newtalk.kr/admin-bt-v2.html` → L1/L2 시각화 대시보드.

---

**보고서 작성**: DASHBOARD-RESTORE-001  
**상태**: 복구 및 격리 완료, 규칙 반영 완료
