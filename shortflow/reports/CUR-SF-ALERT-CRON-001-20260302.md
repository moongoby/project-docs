# CUR-SF-ALERT-CRON-001-20260302
작성일시: 2026-03-02 21:20 KST
작성자: Cursor Agent (ShortFlow)
커밋 SHA: d747175

---

## 1. 작업 개요
- **Directive**: ALERT-CRON — send_alert_email.py cron 및 daily_report.sh 연동
- **우선순위**: P2 (독립 실행)
- **실행 내용**: 에러 알림 자동화 강화 (Python 우선 발송, 일일 리포트 이상 감지)

---

## 2. 변경 내역

### 2-1. `scripts/alert_on_error.sh`
| 항목 | 변경 전 | 변경 후 |
|------|---------|---------|
| 발송 우선순위 | mail 명령 우선 → Python fallback | **Python(send_alert_email.py) 우선 → mail fallback** |
| .env 로드 | 없음 | `source .env` 추가 (ALERT_EMAIL_PASSWORD 로드) |
| 발송 함수 | 인라인 조건문 | `send_alert_python()` / `send_alert_mail()` 함수 분리 |
| 실행 시간 (crontab) | 09:10, 13:10, 18:10 | **09:25, 13:25, 18:25** (v4 파이프라인 완료 대기) |

### 2-2. `scripts/daily_report.sh`
- `.env` 로드 추가 (상단)
- 리포트 생성 후 **이상 감지 → send_alert_email.py 자동 호출** 추가
  - 조건 1: `ERROR > 0` (업로드 에러 발생)
  - 조건 2: `ROOT_USED > 85` (디스크 사용률 임계)
  - 조건 3: `SUCCESS == 0` (오늘 업로드 0건)
- 중복 방지: `.daily_alert_sent_YYYYMMDD` 플래그 파일 사용

### 2-3. crontab 변경
```
# 변경 전
10 9,13,18 * * * /bin/bash /data/shortflow/scripts/alert_on_error.sh >> /data/shortflow/logs/maintenance.log 2>&1

# 변경 후
25 9,13,18 * * * /bin/bash /data/shortflow/scripts/alert_on_error.sh >> /data/shortflow/logs/maintenance.log 2>&1
```
> 이유: economy(09:00) + health(09:10) 파이프라인 완료 후 에러 감지 보장

### 2-4. `.env` 추가
```
ALERT_EMAIL_FROM=moongoby@gmail.com
ALERT_EMAIL_TO=moongoby@gmail.com
# ALERT_EMAIL_PASSWORD=<Gmail_App_Password_여기_입력>
```
> Gmail App Password 설정 필요: https://myaccount.google.com/apppasswords

---

## 3. 알림 발동 조건 요약

| 스크립트 | 실행 시간 | 알림 조건 |
|---------|----------|----------|
| alert_on_error.sh | 09:25, 13:25, 18:25 | 업로드 로그에 error/fail/exception/traceback 감지 |
| daily_report.sh | 23:30 | 에러>0 OR 디스크>85% OR 업로드0건 |

---

## 4. 보안 스캔
- `211.188.*` IP 패턴: CLEAN
- `genspark_dev@` 패턴: CLEAN
- `kill.switch` 패턴: CLEAN
- `.env`, `youtube_token_*.json` 미커밋 확인: OK

---

## 5. 커밋 정보
| 항목 | 내용 |
|------|------|
| 커밋 SHA | d747175 |
| 메시지 | `[SF] ALERT-CRON: send_alert_email.py cron/daily_report 연동` |
| 변경 파일 | `scripts/alert_on_error.sh`, `scripts/daily_report.sh` |
| 레포 | https://github.com/moongoby/shortflow |
| 브랜치 | main |

---

## 6. 후속 필요 작업
- [ ] `ALERT_EMAIL_PASSWORD` 실제 Gmail App Password 입력 후 알림 활성화
- [ ] 알림 수신 테스트: `python3 scripts/send_alert_email.py "[테스트]" "알림 테스트"`

---

## 7. 저장 정보
완료일시: 2026-03-02 21:20 KST
보고서 경로: /data/project-docs/shortflow/reports/CUR-SF-ALERT-CRON-001-20260302.md
