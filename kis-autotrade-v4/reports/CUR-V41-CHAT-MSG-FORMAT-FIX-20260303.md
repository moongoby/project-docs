---
project: KIS
task_id: CUR-V41-CHAT-MSG-FORMAT-FIX-001
completed_at: "2026-03-03 11:50 KST"
status: COMPLETED
---

## 대화창 완료 메시지 형식 통일 (텔레그램 동일 + 브라우저 URL)

---

## 문제

1. `write_done.py` — done 파일만 생성, 대화창 미발송
2. `done_watcher.sh` — 대화창(`chat_messages`) 형식이 텔레그램보다 단순
3. 보고서 URL이 커밋 해시만 표기, 브라우저 접근 불가

---

## 수정 내용

### 1. `write_done.py` — pending_send 자동 생성 + 형식 통일

**변경 전** (done 파일만 생성, 대화창 미발송):
```
[CURSOR-KIS] ✅ TASK-001 완료 (2026-03-03 11:15 KST)
▶ 요약
▶ 커밋: abc1234 | HTTP: 200
▶ 보고서: project-docs 9bd8973  ← 브라우저 접근 불가
```

**변경 후** (pending_send 자동 생성, 텔레그램 동일 형식):
```
[재발송] ✅ KIS 작업 완료 보고

태스크: TASK-001
프로젝트: KIS
완료 시각: 2026-03-03 11:15 KST

📄 결과 보고서(브라우저):
https://github.com/moongoby/project-docs/blob/master/kis-autotrade-v4/reports/TASK-001-20260303.md

요약:
작업 내용 요약

커밋: abc1234 | HTTP: 200
```

- `--report-url` 미입력 시 프로젝트별 기본 경로로 추정 URL 자동 생성
- 실행 즉시 `pending_send_{project}.txt` 생성 → bridge 10초 내 대화창 발송

### 2. `done_watcher.sh` — 대화창/텔레그램 형식 통일 + 브라우저 URL

**변경 전**:
- 대화창(`chat_messages`): 단순 5줄 요약
- 텔레그램: 구분선 포함 상세 형식
- URL: `raw.githubusercontent.com` (raw 텍스트)

**변경 후**:
- 대화창 = 텔레그램 = 동일한 `SHARED_MSG` 변수 사용
- URL: `github.com/blob/master/...` (브라우저 접근 가능)
- 파일 전체 내용(헤더 제외 80줄) 포함

---

## 적용 대상 파일

| 파일 | 위치 |
|------|------|
| `write_done.py` | `/root/.genspark/write_done.py` |
| `done_watcher.sh` | `/root/.genspark/done_watcher.sh` |

---

## 모든 프로젝트 적용 범위

| 프로젝트 | GitHub reports 경로 |
|---------|-------------------|
| KIS | `kis-autotrade-v4/reports` |
| GO100 | `go100/reports` |
| NAS | `nas-image/reports` |
| NTV2 | `newtalk-v2-api/reports` |
| SF | `shortflow/reports` |
| AADS | `aads/reports` |

---

## 동작 검증

- TEST-FORMAT-001 테스트 실행 → pending_send_kis.txt 생성 ✅
- bridge 11:45:20 감지 → KIS 대화창 발송 ✅
- 파일 삭제(소비) 확인 ✅
