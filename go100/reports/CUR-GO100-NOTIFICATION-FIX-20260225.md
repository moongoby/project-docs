# GO100 알림시스템 실동작 테스트 및 수정 보고서

**일시:** 2026-02-25 KST
**작업자:** Claude Opus 4.6
**브랜치:** phase-2c-command-center
**커밋:** `3575566b`

---

## 1. 이메일 발송 수정

### 발견된 문제
| 문제 | 원인 |
|------|------|
| 이메일 발송 안 됨 | `SMTP_PASSWORD=__APP_PASSWORD_HERE__` (플레이스홀더) |
| SMTP 연결 에러 | aiosmtplib `async with` + `starttls()` 중복 TLS |
| `is_email_sent` 오표시 | SMTP 미설정 시 `send_email()` 이 `True` 반환 |

### 수정 내용
| 파일 | 변경 |
|------|------|
| `.env` | SMTP_PASSWORD에 Gmail 앱 비밀번호 설정 |
| `email_service.py` L111 | `SMTP(hostname, port)` + `starttls()` → `SMTP(hostname, port, start_tls=True)` |
| `email_service.py` L154-156 | SMTP 미설정 시 `return True` → `return False` |

### 테스트 결과
- SMTP 로그인: smtp.gmail.com:587 성공
- 이메일 발송: [CEO-EMAIL-GM] 수신 확인 ✅

---

## 2. DB INSERT SQL 수정

### 문제
- `notification_service.py`의 INSERT문에서 `:data::jsonb` 구문이 asyncpg와 호환 안 됨
- `PostgresSyntaxError: syntax error at or near ":"`

### 수정
- `VALUES (:data::jsonb)` → `VALUES (CAST(:data AS jsonb))`

---

## 3. 푸시 알림 설정 페이지 수정

### 발견된 문제
| 문제 | 원인 |
|------|------|
| `/settings` 페이지에 푸시 토글 없음 | GO100 알림 컴포넌트가 `/go100/settings`에만 있음 |
| 사이드바 링크가 `/settings`로 연결 | 메인 네비(Sidebar, BottomNav) → `/settings` (V4 알림만) |
| `pushSupported` 조건부 렌더링 | 푸시 미지원으로 판단되면 토글 자체가 안 보임 |
| 프론트엔드 VAPID 키 누락 | `.env.local`에 `NEXT_PUBLIC_VAPID_PUBLIC_KEY` 미설정 |

### 수정 내용
| 파일 | 변경 |
|------|------|
| `settings/page.tsx` | `SettingsNotificationSection` import 및 profile/notifications 탭에 추가 |
| `SettingsNotificationSection.tsx` | `pushSupported &&` 조건 제거, 항상 표시 + 미지원 시 disabled+안내 |
| `frontend/.env.local` | `NEXT_PUBLIC_VAPID_PUBLIC_KEY` 추가 |

### 테스트 결과
- 푸시 구독 등록: FCM 엔드포인트 2건 DB 저장 ✅
- 푸시 발송: `is_push_sent = true`, 브라우저 알림 수신 확인 ✅

---

## 4. 전체 알림 채널 테스트 결과

| 채널 | 상태 | 확인 |
|------|------|------|
| 인앱 (DB) | ✅ 정상 | 알림 4건 생성, 목록/읽음 처리 정상 |
| SSE 실시간 | ✅ 정상 | Redis pub/sub → EventSource 즉시 수신 |
| 이메일 (SMTP) | ✅ 정상 | Gmail 앱 비밀번호 설정, [CEO-EMAIL-GM] 수신 확인 |
| 브라우저 푸시 | ✅ 정상 | VAPID 키 + FCM 엔드포인트, 시스템 알림 수신 확인 |

---

## 서비스 상태
- go100 (백엔드): active ✅
- go100-frontend: active ✅
