---
project: AADS
task_id: CUR-BRIDGE-AADS-MSGQUEUE-001
completed_at: 2026-03-05 09:05 KST
status: done
commit: project-docs 1dea316
---

## CUR-BRIDGE-AADS-MSGQUEUE-001 완료 보고
## DB 기반 메시지 큐 시스템 구현

### 배경
기존 파일 기반 방식: 원격 서버(68/114)에서 claude_exec.sh 실행 시
RESULT 파일이 원격에 생성 → server-211 done_watcher가 감지 불가
→ 대화창 완료보고 미전달 (근본 원인 해결)

### 구현 내용

#### 1. /root/.genspark/claude_exec.sh ✅
- `aads_queue_msg()` 함수 추가
- 작업 완료(성공/실패/타임아웃) 시 AADS message_queue POST
- target={PROJECT}, type=chat|telegram, status=pending

#### 2. /root/.genspark/genspark_bridge.py ✅
- `_poll_aads_message_queue(proj_key)` 함수 추가 (라인 748)
- 기존 chat_messages 파일 감시 블록 직후 DB 큐 폴링 추가
- type=chat → _send_chat_message() → Genspark 대화창
- type=telegram → telegram_report.send() → 텔레그램
- 처리 후 status=sent 자동 마킹

#### 3. 원격 서버 동기화 ✅
- server-114: scp 완료
- server-68(AADS): scp 완료

#### 4. 기술 문서 ✅
- /root/project-docs/aads/AADS-MSGQUEUE-SPEC-v1.0.md
- GitHub: project-docs commit 1dea316

### 검증
- AADS message_queue POST → 200 ok
- bridge.py syntax OK
- genspark-bridge 재시작 → active (running)

### 아키텍처
```
[모든 서버] claude_exec.sh 완료
    ↓ POST /context/system (message_queue)
AADS DB (PostgreSQL, server-68)
    ↓ genspark_bridge.py 폴링 90초
    ├─ type=chat → Genspark 대화창
    └─ type=telegram → 텔레그램
```

### 기존 파일 기반 방식과 병행 운영
- chat_messages 파일 방식 유지 (done_watcher 흐름 보존)
- DB 방식 추가 → 원격 서버 완료보고 누락 해결
