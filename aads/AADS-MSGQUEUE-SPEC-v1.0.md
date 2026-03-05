# AADS DB 기반 메시지 큐 시스템 설계 문서 v1.0

> 작성일: 2026-03-05 | Task ID: CUR-BRIDGE-AADS-MSGQUEUE-001
> 상태: 구현 완료

---

## 1. 배경 및 목적

### 기존 파일 기반 방식의 한계
- claude_exec.sh가 원격 서버(68/114)에서 실행 시 RESULT 파일이 원격에 생성
- server-211의 done_watcher가 원격 RESULT 파일을 감지 불가 → 대화창 완료보고 누락
- 파일 SCP 백폴러(30초 간격)로 임시 해결했으나 근본적 해결 필요

### DB 기반 방식의 장점
- 모든 서버(211/68/114)에서 AADS API로 직접 메시지 큐 write 가능
- 작업 이력 영구 보존 (AADS PostgreSQL)
- 브릿지가 AADS API 폴링 → 중앙집중 메시지 배달

---

## 2. 아키텍처

```
[모든 서버] claude_exec.sh 완료
    │
    ├─ POST /context/system (category=message_queue)
    │   {target, type, message, status="pending", created_at}
    │
    ▼
AADS DB (PostgreSQL, server-68)
    │
    ├─ genspark_bridge.py 폴링 (매 90초 사이클)
    │   GET /context/system?category=message_queue
    │   status=pending 항목 필터
    │
    ├─ type=chat → _send_chat_message(page, msg) → Genspark 대화창
    ├─ type=telegram → send_telegram(msg) → 텔레그램
    │
    └─ POST 상태 업데이트: status=sent
```

---

## 3. 메시지 큐 스키마

### AADS Context API
- **Category**: `message_queue`
- **Key**: `{PROJECT}_{epoch}_{type}` (예: `KIS_1772670000_chat`)

### Value 필드
```json
{
  "target": "KIS",          // 대상 프로젝트 채팅 (KIS/GO100/AADS/SF/NTV2/NAS/SALES)
  "type": "chat",           // "chat" | "telegram"
  "message": "완료 보고...",
  "status": "pending",      // "pending" | "sent" | "error"
  "created_at": "2026-03-05 09:00 KST",
  "source": "claude_exec"   // 메시지 발신 출처
}
```

---

## 4. 구현 위치

### claude_exec.sh
- 작업 완료(성공/실패/타임아웃) 시 AADS message_queue POST
- AADS_API_URL, AADS_MONITOR_KEY → /root/.env.aads 읽기

### genspark_bridge.py
- `_poll_aads_message_queue(proj_key)` 함수 추가
- 기존 chat_messages 파일 감시 블록 직후에 호출
- type=chat → `_send_chat_message()` 재사용
- type=telegram → `send_telegram()` 호출
- 처리 후 status="sent" 업데이트

---

## 5. claude_exec.sh write 함수

```bash
aads_queue_msg() {
    local target="$1" type="$2" message="$3" status="$4"
    local url key epoch
    url=$(grep '^AADS_API_URL=' /root/.env.aads 2>/dev/null | cut -d= -f2-)
    key_h=$(grep '^AADS_MONITOR_KEY=' /root/.env.aads 2>/dev/null | cut -d= -f2-)
    [ -z "$url" ] && return 1
    epoch=$(date +%s)
    key="${target}_${epoch}_${type}"
    curl -s -X POST "${url}/context/system" \
        -H "Content-Type: application/json" \
        -H "X-Monitor-Key: ${key_h}" \
        -d "{\"category\":\"message_queue\",\"key\":\"${key}\",\"value\":{\"target\":\"${target}\",\"type\":\"${type}\",\"message\":$(python3 -c "import json,sys; print(json.dumps(sys.stdin.read()))" <<< "${message}"),\"status\":\"${status}\",\"created_at\":\"$(date '+%Y-%m-%d %H:%M KST')\",\"source\":\"claude_exec\"}}" \
        > /dev/null 2>&1
}
```

---

## 6. 브릿지 폴링 함수

```python
def _poll_aads_message_queue(proj_key: str) -> list[dict]:
    """AADS message_queue에서 해당 프로젝트 pending 메시지 조회 후 sent 마킹"""
    _load_aads_env()
    if not _AADS_API_URL or not _AADS_MONITOR_KEY:
        return []
    try:
        req = urllib.request.Request(
            f"{_AADS_API_URL}/context/system?category=message_queue",
            headers={"X-Monitor-Key": _AADS_MONITOR_KEY},
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        items = data.get("data", {}).get("message_queue", [])
        result = []
        for it in items:
            val = it.get("value", {})
            if isinstance(val, str):
                val = json.loads(val)
            if val.get("target", "").upper() == proj_key.upper() and val.get("status") == "pending":
                result.append({"key": it["key"], **val})
                # sent 마킹
                val["status"] = "sent"
                _aads_write("message_queue", it["key"], val)
        return result
    except Exception as e:
        logger.debug("message_queue 조회 실패: %s", e)
        return []
```

---

## 7. 적용 서버
- claude_exec.sh: server-211 (KIS/GO100), server-68 (AADS), server-114 (SF/NTV2/NAS)
- genspark_bridge.py: server-211 (중앙 배달)

---

## 8. 완료 기준
- [x] 기술 문서 작성
- [x] claude_exec.sh AADS write 추가
- [x] genspark_bridge.py message_queue 폴링 추가
- [x] 원격 서버(114, 68) claude_exec.sh 동기화
- [x] 동작 검증
