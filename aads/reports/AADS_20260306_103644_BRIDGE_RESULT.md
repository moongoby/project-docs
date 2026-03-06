---
project: AADS
task_id: T-100
completed_at: 2026-03-06 10:40 KST
---

# T-100 실행 결과: 브릿지 완료보고 재감지 방지 — 무한루프 차단

## 지시서 원문

Task ID: T-100
Title: 브릿지 완료보고 메시지 재감지 방지 — 무한루프 차단
Project: AADS
Server: 68 (aads.newtalk.kr)
Priority: P0-CRITICAL
예상 시간: 15분
의존성: 없음

필수 문서:
- HANDOVER 읽기: https://raw.githubusercontent.com/moongoby-GO100/aads-docs/main/HANDOVER.md
- CEO-DIRECTIVES 읽기: https://raw.githubusercontent.com/moongoby-GO100/aads-docs/main/CEO-DIRECTIVES.md

백업:
cd /root/aads && cp scripts/genspark_bridge.py scripts/genspark_bridge.py.bak.T100
cd /root/aads/aads-docs && git tag pre-T100

---

## 실행 내역

### 파일 위치 확인

지시서에 명시된 `scripts/genspark_bridge.py`는 실제로 `/root/aads/scripts/bridge.py`로 존재함을 확인.
(genspark_bridge.py 별도 파일 없음 — bridge.py가 동일 역할)

---

### 백업 수행

```
$ cp /root/aads/scripts/bridge.py /root/aads/scripts/bridge.py.bak.T100
Backup done

$ cd /root/aads/aads-docs && git tag pre-T100
fatal: tag 'pre-T100' already exists
(이전 실행 시 이미 태그 생성됨 — 정상)
```

---

### Part A — bridge.py 수정 결과

파일: `/root/aads/scripts/bridge.py`

이전 실행(부분 적용)에서 이미 상수 및 로직이 완전히 적용되어 있음을 확인:

#### 수정 1: SKIP_PATTERNS + 메시지 스킵 로직 (lines 46-57, 362-369)

```python
SKIP_PATTERNS = [
    "작업 완료",
    "push 완료",
    "에러 종료",
    "BRIDGE_RESULT",
    "현재 작업 현황",
    "다음 지시서 작성 전 필수 확인",
    "맥락유지 필수문서",
    "HANDOVER.md 반드시 갱신",
    "지시서 작성규칙",
    "auto_trigger 자동 실행",
]
```

process_message() 내 스킵 로직:
```python
# T-100: 완료보고 패턴 스킵
for pattern in SKIP_PATTERNS:
    if pattern in message:
        return {"detected": False, "skipped": True, "reason": f"skip_pattern: {pattern}"}
```

#### 수정 2: 자기발송 마커 (lines 59-60, 362-364)

```python
BRIDGE_SENT_MARKER = "[BRIDGE-SENT]"

# T-100: 자기 발송 마커 체크
if BRIDGE_SENT_MARKER in message:
    return {"detected": False, "skipped": True, "reason": "bridge-sent marker"}
```

#### 수정 3: 중복 처리 방지 (lines 62-65, 371-379)

```python
_processed_ids: set = set()
_processed_ids_order: list = []
_MAX_PROCESSED_IDS = 1000

# T-100: 중복 처리 방지
msg_hash = hashlib.md5(message.encode()).hexdigest()
if msg_hash in _processed_ids:
    return {"detected": False, "skipped": True, "reason": "duplicate"}
_processed_ids.add(msg_hash)
_processed_ids_order.append(msg_hash)
if len(_processed_ids_order) > _MAX_PROCESSED_IDS:
    old = _processed_ids_order.pop(0)
    _processed_ids.discard(old)
```

#### 수정 4: DIRECTIVE_START 감지 강화 (lines 381-406)

```python
# T-100 수정4: "지시서 작성규칙" 또는 "작성규칙"이 같은 메시지에 있으면 규칙 설명 → 스킵
if "지시서 작성규칙" in message or "작성규칙" in message:
    continue

# T-100 수정4: Task ID가 실제 숫자(T-NNN)가 아니면 템플릿 → 스킵
task_id_match_inner = re.search(r'Task ID\s*:\s*T-(\d+)', block_text)
if not task_id_match_inner:
    continue

# T-100 수정4: done/ 폴더에 이미 완료된 task면 스킵
task_num = task_id_match_inner.group(1)
done_files = (
    _glob.glob(f"{done_dir}/*T{task_num}*")
    + _glob.glob(f"{done_dir}/*T-{task_num}*")
)
if done_files:
    continue
```

---

### Part B — auto_trigger.sh 수정 결과

파일: `/root/aads/scripts/auto_trigger.sh`

이전 실행에서 이미 적용되어 있음을 확인 (lines 50-54):

```bash
# T-100: RESULT 파일은 지시서가 아니므로 스킵
if [[ "$filename" == *"RESULT"* ]]; then
    echo "SKIP: Result file, not a directive — ${filename}"
    return 0
fi
```

---

### Part C — 테스트 결과

#### 테스트 1: SKIP_PATTERNS — 완료보고 메시지 무시

```
$ python3 bridge.py --text "작업 완료: T-099 처리됨"
{
  "detected": false,
  "skipped": true,
  "reason": "skip_pattern: 작업 완료"
}
```
→ PASS

#### 테스트 2: 자기발송 마커 [BRIDGE-SENT] 무시

```
$ python3 bridge.py --text "push 완료 T-099 [BRIDGE-SENT]"
{
  "detected": false,
  "skipped": true,
  "reason": "bridge-sent marker"
}
```
→ PASS

#### 테스트 3: 실제 DIRECTIVE 정상 처리

```
$ python3 bridge.py --text ">>>DIRECTIVE_START\nTask ID: T-200\nTitle: 테스트 지시서\n내용: 신규 작업\n>>>DIRECTIVE_END"
{
  "detected": false,
  "summary": null,
  "keywords": [],
  "saved": null,
  "result": null,
  "conversation_saved": {
    "status": "ok",
    "saved": "go100_user_memory/741",
    "id": 741,
    "created_at": "2026-03-06 01:39:31.148030"
  },
  "directive_blocks_saved": [
    {
      "status": "ok",
      "saved": "go100_user_memory/740",
      "id": 740,
      "created_at": "2026-03-06 01:39:31.043625"
    }
  ]
}
```
→ PASS (directive_blocks_saved에 실제 저장됨)

#### 테스트 4: 지시서 작성규칙 포함 메시지의 DIRECTIVE_START 무시

```
$ python3 bridge.py --text "지시서 작성규칙 예시:\n>>>DIRECTIVE_START\nTask ID: T-NNN\nTitle: 템플릿\n>>>DIRECTIVE_END"
{
  "detected": false,
  "skipped": true,
  "reason": "skip_pattern: 지시서 작성규칙"
}
```
→ PASS

#### 테스트 5: 중복 메시지 처리 방지

```
1차: False processed
2차: True duplicate
```
→ PASS (동일 메시지 두 번째 처리 시 "duplicate"로 스킵)

---

### Part D — Git Push 결과

```
$ cd /root/aads/aads-docs
$ git add HANDOVER.md reports/T-100-RESULT.md
$ git commit -m "fix(T-100): 브릿지 완료보고 재감지 방지 — SKIP_PATTERNS + 중복처리 차단"
[main b5347a9] fix(T-100): 브릿지 완료보고 재감지 방지 — SKIP_PATTERNS + 중복처리 차단
 2 files changed, 60 insertions(+), 1 deletion(-)
 create mode 100644 reports/T-100-RESULT.md

$ git push origin main
To https://github.com/moongoby-GO100/aads-docs.git
   42d3a53..b5347a9  main -> main
```

커밋 SHA: b5347a9

---

### HANDOVER v5.24 업데이트

HANDOVER.md 첫 줄에 v5.24 추가:
"T-100: genspark_bridge.py 완료보고 메시지 재감지 방지 — SKIP_PATTERNS 10개, 자기발송 마커[BRIDGE-SENT], processed_ids 중복차단, DIRECTIVE 템플릿/규칙설명 구분, auto_trigger RESULT파일 스킵"

---

## 보고

[CURSOR-AADS] push 완료
작업: T-100 브릿지 완료보고 재감지 방지
보고서: https://github.com/moongoby-GO100/aads-docs/blob/main/reports/T-100-RESULT.md
커밋: https://github.com/moongoby-GO100/aads-docs/commit/b5347a9
HTTP: 200
HANDOVER: 업데이트 완료 (v5.24)
다음: T-095 재실행
