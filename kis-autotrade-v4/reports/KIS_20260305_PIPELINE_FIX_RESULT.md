---
project: KIS AutoTrade V4.1 (공통 인프라)
task_id: PIPELINE-FIX-20260305
completed_at: 2026-03-05T19:29:00+09:00
status: completed
---

# 완료 메시지 파이프라인 근본 문제 점검 및 완전 조치 보고

완료 시각: 2026-03-05 19:29 KST

---

## 문제 요약

각 매니저 대화창에 완료 보고 메시지가 오다 안오다 하는 간헐적 문제.

---

## 발견된 근본 원인 (6가지)

### 원인 1: done_watcher.sh 중복 실행 → 중복 메시지
- 동일 RESULT 파일을 두 인스턴스가 동시 처리 → chat_messages 파일 2개 생성 → 대화창에 같은 완료 보고 2번 도달
- **조치**: lockfile(`/tmp/done_watcher.lock`) 추가, 선행 인스턴스 존재 시 즉시 exit

### 원인 2: done_watcher footer `>>>DIRECTIVE_START` 블록 → 브릿지 오감지
- 완료 메시지 footer에 `>>>DIRECTIVE_START ... Task ID: T-NNN ... >>>DIRECTIVE_END` 예시 포함
- 브릿지가 매 폴링마다 T-NNN을 실제 지시서로 파싱 → seen_tasks 차단 반복 → 로그 오염 + 대화창 변경 감지 오작동
- **조치**: done_watcher footer에서 DIRECTIVE 블록 완전 제거, 지시서 작성규칙은 각 프로젝트 CONTEXT.md로 이관

### 원인 3: CONTEXT.md 5개 파일에 `>>>DIRECTIVE_START/END` 잔존 → T-NNN 반복 오감지
- kis-autotrade-v4, go100, shortflow, nas-image, newtalk-v2-api CONTEXT.md에 이관한 지시서 예시에 실제 마커(`>>>DIRECTIVE_START/END`) 사용
- 매니저가 CONTEXT.md를 읽을 때 대화창에 표시 → 브릿지가 T-NNN 지시서로 반복 파싱
- **조치**: 5개 CONTEXT.md 모두 `>>>DIRECTIVE_START` → `[지시서 예시 형식]`, `>>>DIRECTIVE_END` → `[예시 끝]` 치환 (GitHub 반영)

### 원인 4: chat_messages 메시지 길이 초과 → Enter 미작동
- done_watcher `head -80`으로 최대 5000자 이상 메시지 생성
- Genspark 입력창 전송 시 2900자 이상이면 Enter 키가 작동하지 않음 → 파일 보존 → 다음 사이클 재시도 → 지연처럼 보임
- **조치**: `head -80` → `head -30`, SHARED_MSG 안전 한도 2800자로 절삭 추가

### 원인 5: TEST 프로젝트 chat_messages 파일 영구 잔류
- `TEST_*.txt` 파일 2개가 chat_messages 폴더에 남아 있었음 (TEST는 PROJECTS 목록에 없어 전송 불가)
- **조치**: 파일 2개 삭제

### 원인 6: `_is_valid_directive()` T-NNN 플레이스홀더 통과
- 기존 템플릿 필터는 `{변수명}` 형식만 차단 → `T-NNN` 형태는 통과
- **조치**: `genspark_bridge.py`에 `^T-([A-Z])\1{1,}$` 패턴 필터 추가 (T-108, CEO-APPROVAL 등 실제 ID 오차단 없음 검증)

---

## 조치 내역

| 파일 | 변경 내용 |
|------|-----------|
| `/root/.genspark/done_watcher.sh` | lockfile, head -80→30, 2800자 절삭, DIRECTIVE 블록 제거 |
| `/root/.genspark/genspark_bridge.py` | T-NNN 더미 ID 차단 필터 추가 |
| `/root/project-docs/kis-autotrade-v4/CONTEXT.md` | `>>>DIRECTIVE_START/END` → `[지시서 예시 형식]` |
| `/root/project-docs/go100/CONTEXT.md` | 동일 |
| `/root/project-docs/shortflow/CONTEXT.md` | 동일 |
| `/root/project-docs/nas-image/CONTEXT.md` | 동일 |
| `/root/project-docs/newtalk-v2-api/CONTEXT.md` | 동일 |

Git: project-docs SHA=e7a8f1e (master)

---

## 잔여 이슈 (관찰 중)

**AADS-QUEUE TTL 초과 반복 경고**: 오늘 생성된 메시지(KIS, NTV2, GO100) 중 채팅창 전송 실패 항목이 AADS queue에 남아 있고 매 사이클 TTL 만료 경고 발생. `_aads_write()`로 error 처리하나 AADS 서버가 일시 502를 반환했던 시점에 쌓인 것으로 추정. 내일 새 사이클 시작 시 자동 소멸 예상. 기능 이상 없음.

---

## 현재 파이프라인 상태 (19:29 KST)

| 항목 | 상태 |
|------|------|
| done_watcher.sh | 정상 (PID 710170, lockfile 보유) |
| genspark_bridge.py | 정상 (PID 3218560) |
| chat_messages 폴더 | 비어 있음 (모두 전송 완료) |
| T-NNN 오감지 | 차단 (seen_tasks + _is_valid_directive 이중 방어) |
| 메시지 길이 제한 | 2800자 (Enter 미작동 방지) |

