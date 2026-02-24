# CUR-GO100-NOTIFICATION-SYSTEM-001 — GO100 알림 시스템 구축

**발행:** 2026-02-24  
**우선순위:** P1  
**프로젝트:** /root/kis-autotrade-v4  
**브랜치:** phase-2c-command-center → feat/CUR-GO100-NOTIFICATION-SYSTEM-001  

---

## 1. 작업 요약

| Phase | 내용 |
|-------|------|
| **Phase A** | 인앱 알림: DB(go100_notifications) + SSE 실시간 스트림(Redis pub/sub) |
| **Phase B** | 이메일 알림: 기존 SMTP(email_service) 활용, 설정 기반 발송 |
| **Phase C** | PWA: manifest.json start_url=/go100, sw.js(push/notificationclick), 브라우저 푸시 구독 |

---

## 2. 변경 파일 목록

### 신규

- `backend/app/services/go100/notification/__init__.py`
- `backend/app/services/go100/notification/notification_service.py`
- `backend/app/routers/go100/notification_router.py`
- `frontend/src/go100/hooks/useNotificationStore.ts`
- `frontend/src/go100/hooks/useNotifications.ts`
- `frontend/src/go100/components/Go100NotificationBell.tsx`
- `frontend/src/go100/components/SettingsNotificationSection.tsx`
- `frontend/src/app/(protected)/go100/notifications/page.tsx`
- `frontend/public/sw.js`

### 수정

- `backend/app/main.py` — go100_notification_router 등록
- `backend/app/services/auto_trade_engine.py` — card_source/trigger_type, GO100 알림 트리거(체결/손절/익절)
- `backend/app/services/go100/backtest/backtest_service.py` — BACKTEST_COMPLETED 알림
- `backend/app/services/go100/optimizer/backtest_optimizer.py` — OPTIMIZE_COMPLETED 알림
- `backend/app/routers/go100/scheduler_router.py` — SCHEDULER_ERROR 알림, imports
- `frontend/src/go100/api/go100Api.ts` — 알림 API·타입 추가
- `frontend/src/go100/components/Go100Layout.tsx` — 헤더에 Go100NotificationBell
- `frontend/src/go100/components/Go100Sidebar.tsx` — 알림 메뉴 추가
- `frontend/src/go100/components/index.ts` — Go100NotificationBell export
- `frontend/src/app/(protected)/go100/settings/page.tsx` — SettingsNotificationSection 추가
- `frontend/public/manifest.json` — start_url "/go100"
- `backend/requirements.txt` — pywebpush 추가

---

## 3. DB 테이블 (3개)

### go100_notifications

- `id` BIGSERIAL PRIMARY KEY  
- `user_id` INTEGER NOT NULL  
- `type` VARCHAR(50) NOT NULL  
- `title` VARCHAR(200), `message` TEXT, `data` JSONB  
- `priority` VARCHAR(10) DEFAULT 'NORMAL'  
- `is_read` BOOLEAN DEFAULT FALSE  
- `is_email_sent`, `is_push_sent` BOOLEAN  
- `channel` VARCHAR(20) DEFAULT 'IN_APP'  
- `created_at` TIMESTAMPTZ, `read_at` TIMESTAMPTZ  
- 인덱스: user_id+is_read+created_at, user_id+type, created_at  

### go100_notification_settings

- `id` BIGSERIAL PRIMARY KEY, `user_id` INTEGER NOT NULL UNIQUE  
- `in_app_enabled`, `email_enabled`, `push_enabled` BOOLEAN  
- 이벤트별: trade_executed, stop_loss_triggered, take_profit_triggered, backtest_completed, optimize_completed, daily_summary, scheduler_error, system_alert  
- `email_override` VARCHAR(200), `created_at`, `updated_at`  

### go100_push_subscriptions

- `id` BIGSERIAL PRIMARY KEY, `user_id` INTEGER NOT NULL  
- `endpoint` TEXT, `p256dh` TEXT, `auth` TEXT  
- `user_agent` VARCHAR(500), `is_active` BOOLEAN DEFAULT TRUE  
- UNIQUE(user_id, endpoint)  

---

## 4. API 스펙 (10개)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | /api/go100/notifications | 알림 목록 (limit, offset, unread_only, type) |
| GET | /api/go100/notifications/unread-count | 읽지 않은 수 |
| PATCH | /api/go100/notifications/{id}/read | 단일 읽음 |
| POST | /api/go100/notifications/read-all | 전체 읽음 |
| GET | /api/go100/notifications/stream | SSE 스트림 (?token= Bearer 생략 가능) |
| GET | /api/go100/notifications/settings | 알림 설정 조회 |
| PUT | /api/go100/notifications/settings | 알림 설정 수정 |
| POST | /api/go100/notifications/push-subscribe | 푸시 구독 등록 |
| DELETE | /api/go100/notifications/push-subscribe | 구독 해제 |
| POST | /api/go100/notifications/test | 테스트 알림 발송 |

---

## 5. 알림 타입 (12종)

TRADE_EXECUTED, STOP_LOSS_TRIGGERED, TAKE_PROFIT_TRIGGERED, BACKTEST_COMPLETED, OPTIMIZE_COMPLETED, OPTIMIZE_SUGGESTION, DAILY_SUMMARY, SCHEDULER_ERROR, TOKEN_EXPIRING, BALANCE_LOW, DAILY_LOSS_LIMIT, SYSTEM_ALERT  

---

## 6. 기존 서비스 트리거 삽입 위치

- **auto_trade_engine.py**: execute_order 성공 시 card_source=="go100"일 때 create_notification (TRADE_EXECUTED / STOP_LOSS_TRIGGERED / TAKE_PROFIT_TRIGGERED). run_strategy, check_stop_loss, check_take_profit에서 card_source·trigger_type 전달.
- **backtest_service.py**: run_backtest 완료(COMPLETED) 후 BACKTEST_COMPLETED 알림.
- **backtest_optimizer.py**: start_optimization 완료 후 OPTIMIZE_COMPLETED 알림.
- **scheduler_router.py**: run-live / run-paper / reconcile 호출 후 result.errors 존재 시 SCHEDULER_ERROR 알림(URGENT).

---

## 7. PWA

- **manifest.json**: start_url "/go100", 기존 아이콘 유지.
- **sw.js**: install/activate, push → showNotification, notificationclick → clients.openWindow(url).
- **VAPID**: 서버 .env에 VAPID_PUBLIC_KEY, VAPID_PRIVATE_KEY, VAPID_SUBJECT=mailto:admin@newtalk.kr 설정. 키 생성: `python3 -c "from py_vapid import Vapid; v=Vapid(); v.generate_keys(); print('PUBLIC:', v.public_key); print('PRIVATE:', v.private_key)"` (pywebpush 설치 시 py_vapid 사용 가능).

---

## 8. 테스트

- Python 문법 검사·tsc·npm run build·pre-commit-check.sh 통과.
- 통합 테스트: 로그인 → /api/go100/notifications/settings → /api/go100/notifications/test → /api/go100/notifications → unread-count → read-all (서버에서 curl 또는 스크립트로 실행 가능).

---

## 9. 검수

- kis-v41-* 서비스 재시작 없음.
- strategy_cards / v4_positions 직접 편집 없음.
- .env 미커밋.
- 변경 파일에 헤더 주석 CUR-GO100-NOTIFICATION-SYSTEM-001, 2026-02-24 적용.
- go100_* 테이블·파일만 추가/수정.

---

## 10. 체크리스트

- [x] STEP 0: 백업, 현황 파악
- [x] STEP 1: DB 테이블 3개 생성
- [x] STEP 2: notification_service.py
- [x] STEP 3: notification_router.py (API 10개)
- [x] STEP 4: main.py 라우터 등록
- [x] STEP 5: 알림 트리거 삽입 (매매/백테스트/옵티마이저/스케줄러)
- [x] STEP 6: go100Api.ts 알림 API
- [x] STEP 7: useNotifications·useNotificationStore
- [x] STEP 8: Go100NotificationBell·레이아웃
- [x] STEP 9: go100/notifications 페이지
- [x] STEP 10: 설정 페이지 알림 섹션
- [x] STEP 11: manifest·sw.js·pywebpush
- [x] STEP 12: compile·tsc·build·pre-commit
- [ ] STEP 13: 통합 테스트 (서버에서 실행)
- [ ] STEP 14: 커밋·병합·push
- [ ] STEP 15: 보고서 GitHub push

---

**보고서 저장:** /root/project-docs/go100/reports/CUR-GO100-NOTIFICATION-SYSTEM-001-20260224.md  
**GitHub:** https://github.com/moongoby/project-docs/blob/master/go100/reports/CUR-GO100-NOTIFICATION-SYSTEM-001-20260224.md
