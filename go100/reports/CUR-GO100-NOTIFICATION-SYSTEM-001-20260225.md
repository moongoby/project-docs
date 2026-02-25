# CUR-GO100-NOTIFICATION-SYSTEM-001 — 반영소스 확인 및 업데이트 보고서

**작성일:** 2026-02-25 (KST)  
**작업 ID:** CUR-GO100-NOTIFICATION-SYSTEM-001  
**트랙:** E — GO100 알림 시스템  
**브랜치:** phase-2c-command-center (feat/CUR-GO100-NOTIFICATION-SYSTEM-001 기존 존재, 로컬 변경으로 전환 생략)

---

## 1. 반영소스 확인 결과

지시서(트랙 E) 기준으로 기존 코드베이스를 점검한 결과, **대부분 이미 반영**되어 있었음.

| 구분 | 파일/위치 | 상태 |
|------|-----------|------|
| 백엔드 서비스 | `backend/app/services/go100/notification/__init__.py`, `notification_service.py` | ✅ 존재, 스펙 부합 |
| 백엔드 라우터 | `backend/app/routers/go100/notification_router.py` | ✅ 존재, API 10개 구현 |
| main.py | go100_notification_router 등록 | ✅ 등록됨 |
| 프론트 벨 | `Go100NotificationBell.tsx` (hooks: useNotifications, useNotificationStore) | ✅ 존재 |
| 알림 페이지 | `app/(protected)/go100/notifications/page.tsx` | ✅ 존재 (필터: 전체/읽지않음/매매/시스템) |
| PWA | `public/manifest.json`, `public/sw.js` | ✅ 존재 |
| PWA 배너/가이드 | `PWAInstallBanner.tsx`, `IOSInstallGuide.tsx` | ✅ 존재 |
| 레이아웃 | `Go100Layout.tsx` 헤더에 Go100NotificationBell | ✅ 삽입됨 |
| DB 테이블 | go100_notifications, go100_notification_settings, go100_push_subscriptions | ✅ 3테이블 존재 |

---

## 2. 본일(2026-02-25) 수행 작업

### 2.1 사전 백업

- `PGPASSWORD='...' pg_dump -h localhost -U kis_admin -d kisautotrade --schema-only`
- 저장: `/root/backup/pre-notification-schema-YYYYMMDD-HHMMSS.sql`

### 2.2 DDL 재실행

- 지시서 DDL 그대로 실행 (CREATE TABLE IF NOT EXISTS, CREATE INDEX IF NOT EXISTS).
- 이미 테이블 존재로 스킵된 항목 다수, 인덱스 등 누락 없음 확인.

### 2.3 백엔드 수정

- **notification_router.py**
  - `PUT /settings`: 요청 바디 명시를 위해 `settings: dict = Body(..., embed=False)` 적용.
  - 헤더 주석 날짜: 2026-02-25로 통일.
- **notification_service.py**
  - 헤더 주석 날짜: 2026-02-25로 통일.

### 2.4 프론트엔드 수정

- **Go100NotificationBell.tsx**
  - 드롭다운 노출 개수: `slice(0, 10)` → `slice(0, 5)` (지시서 “최근 알림 5개” 반영).
  - 헤더 주석 날짜: 2026-02-25로 통일.

### 2.5 알림 페이지

- 타입 필터: “매매”/“시스템”은 복수 타입(TRADE_EXECUTED 등 / SCHEDULER_ERROR 등)이라 **클라이언트 필터링 유지**. API 단일 `type` 쿼리만으로는 대응 불가하여 변경 없음.

---

## 3. 수정 파일 요약 (2026-02-25)

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/routers/go100/notification_router.py` | Body() 추가, 헤더 2026-02-25 |
| `backend/app/services/go100/notification/notification_service.py` | 헤더 2026-02-25 |
| `frontend/src/go100/components/Go100NotificationBell.tsx` | 최근 5개 표시, 헤더 2026-02-25 |

---

## 4. 검증 권장 사항

- **DB:**  
  `SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'go100_notif%' OR table_name = 'go100_push_subscriptions';`  
  → 3테이블 확인됨.
- **백엔드:**  
  `curl -s http://localhost:8002/health`  
  (★ kis-v41-* 서비스 재시작 금지. go100 / go100-frontend만 필요 시 재시작.)
- **API:**  
  - `GET /api/go100/notifications/unread-count` (Authorization: Bearer \<token\>)  
  - `PUT /api/go100/notifications/settings` (JSON body)  
  - `POST /api/go100/notifications/test`
- **프론트:**  
  - `npx tsc --noEmit`, `npm run build` (frontend 디렉터리)

---

## 5. 참조 문서

- HANDOVER-20260224-V2.md (부록 B)
- API_SPEC.md 섹션 9
- DB-SCHEMA-GO100.md (알림 테이블)
- go100-rules.md, GIT-WORKFLOW.md

---

**보고서 위치:** `/root/project-docs/go100/reports/CUR-GO100-NOTIFICATION-SYSTEM-001-20260225.md`
