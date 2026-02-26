# CUR-GO100-PHASE6-C4-PROACTIVE-REPORT (2026-02-26)

## 목표
백억이가 사용자 질문을 기다리지 않고, 매일/주간/이벤트 기반으로 능동적으로 브리핑.
"물어보기 전에 알려주는 AI" — 개인 전담 트레이더 경험 제공.

## 구현 요약

### 1. DB 스키마
- **테이블:** `go100_reports`
  - `report_id`, `user_id`, `report_type`, `title`, `content`, `priority`, `is_read`, `created_at`
  - `report_type`: daily_morning, daily_close, weekly, monthly, event_alert
  - `priority`: urgent, high, normal, low
- **인덱스:** `idx_go100_reports_user_unread` (WHERE is_read = FALSE), `idx_go100_reports_user_created`

### 2. 백엔드
- **proactive_reporter.py** (신규)
  - `generate_morning_briefing()` — 글로벌/레짐/포트폴리오 요약 + 오늘의 전략 권고
  - `generate_closing_report()` — 시장 요약, 수급, 포트폴리오 일일 P&L, 레짐 변화
  - `generate_weekly_report()` — 주간 시장·수익률, KOSPI 대비
  - `check_event_alerts()` — MDD 한도 근접, 레짐 전환, 목표 마일스톤 등
  - `save_report()`, `get_unread_reports()`, `get_unread_count()`, `mark_as_read()`
- **scripts/go100/daily_reports.py** (신규)
  - `--type morning|closing|weekly|event`, `--user-id N` (생략 시 ACTIVE 목표 사용자 전체)
  - go100_goals.status='ACTIVE' 사용자 대상 보고 생성 및 저장
- **reports_router.py** (신규)
  - `GET /api/go100/reports/unread-count` — 미읽은 건수
  - `GET /api/go100/reports` — 목록 (unread_only 옵션)
  - `PATCH /api/go100/reports/{report_id}/read` — 읽음 처리
- **ai_router.py**
  - 인텐트 **report_check** (17번째) 추가
  - 키워드: 알림, 브리핑, 리포트, 보고서, 미읽은, 새소식 등
  - "알림 있어?", "브리핑 보여줘", "오늘 리포트" → 미읽은 보고서 목록 표시

### 3. 프런트엔드
- **go100Api.ts:** `getReportsUnreadCount()` 추가
- **ChatWidget.tsx:** 미읽은 보고서 건수 조회, FAB에 빨간 점 뱃지 표시 (count > 0)

### 4. 크론 제안
```
50 8 * * 1-5   모닝 브리핑 (08:50)
40 15 * * 1-5  장마감 리포트 (15:40)
0 9 * * 6      주간 보고 (토 09:00)
*/5 9-15 * * 1-5 이벤트 알림 체크 (장중 5분마다)
```
실제 등록은 운영 환경에서 수행.

## 검증
- 마이그레이션 적용: `031_go100_reports.sql` OK
- 모닝 브리핑 수동 생성: `python scripts/go100/daily_reports.py --type morning --user-id 1` → report_id=1 저장 확인
- DB: `SELECT * FROM go100_reports` 1건 조회 확인

## 파일 목록
- backend/migrations/031_go100_reports.sql
- backend/app/services/go100/ai/proactive_reporter.py
- backend/app/routers/go100/reports_router.py
- backend/app/routers/go100/ai_router.py (report_check 인텐트·핸들러)
- backend/app/services/go100/ai/response_formatter.py (report_check 헤더/푸터)
- backend/app/main.py (go100_reports_router 등록)
- scripts/go100/daily_reports.py
- frontend/src/go100/api/go100Api.ts (getReportsUnreadCount)
- frontend/src/go100/components/ChatWidget.tsx (미읽은 알림 뱃지)
