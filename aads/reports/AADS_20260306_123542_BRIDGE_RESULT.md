---
project: AADS
task_id: T-106
completed_at: 2026-03-06T12:43:46+09:00
---

[CURSOR-AADS] push 완료
작업: T-106 auto_trigger 우선순위 실행 로직
보고서: https://github.com/moongoby-GO100/aads-server/blob/main/scripts/auto_trigger.sh
커밋: https://github.com/moongoby-GO100/aads-server/commit/a52e513
HTTP: 200
검증: P0 우선 선택 확인, 파일명 P0/P1/P2 구분 확인
HANDOVER: v5.29 업데이트 완료
다음: 지시 대기

---

# T-106 실행 결과 상세 보고

## 작업 1: auto_trigger.sh 우선순위 정렬

**파일**: `/root/aads/scripts/auto_trigger.sh` (→ `/root/aads/aads-server/scripts/auto_trigger.sh`)

추가된 주요 변수:
```bash
PENDING_DIR="${PENDING_DIR:-/root/.genspark/directives/pending}"
RUNNING_DIR="${RUNNING_DIR:-/root/.genspark/directives/running}"
PRIORITY_LOG="/var/log/aads/auto_trigger_priority.log"
DRY_RUN=false
for _arg in "$@"; do
    [ "$_arg" = "--dry-run" ] && DRY_RUN=true
done
```

추가된 `_select_next_file()` 함수 (우선순위 5단계):
```bash
_select_next_file() {
    local pending_dir="$1"
    # ...
    # 1순위: 파일명에 _P0_ 포함
    next_file=$(ls "${pending_dir}"/*_P0_*.md 2>/dev/null | head -1 || true)
    # 2순위: 내용에 P0-CRITICAL 포함
    if [ -z "$next_file" ]; then
        next_file=$(grep -rl "P0-CRITICAL" "${pending_dir}"/*.md 2>/dev/null | head -1 || true)
    fi
    # 3순위: 파일명에 _P1_ 포함
    if [ -z "$next_file" ]; then
        next_file=$(ls "${pending_dir}"/*_P1_*.md 2>/dev/null | head -1 || true)
    fi
    # 4순위: 내용에 P1-HIGH 포함
    if [ -z "$next_file" ]; then
        next_file=$(grep -rl "P1-HIGH" "${pending_dir}"/*.md 2>/dev/null | head -1 || true)
    fi
    # 5순위: 기존 FIFO (가장 오래된 파일)
    if [ -z "$next_file" ]; then
        next_file=$(ls -t "${pending_dir}"/*.md 2>/dev/null | tail -1 || true)
    fi
    # 로그 기록 + echo 결과
    if [ -n "$next_file" ]; then
        _log_priority "$p0_content_count" "$p1_content_count" "$p2_count" \
            "$(basename "$next_file") | REASON: $reason"
        echo "$next_file"
    fi
}
```

추가된 pending→running 이동 블록:
```bash
if [ -d "$PENDING_DIR" ] && ls "${PENDING_DIR}"/*.md 2>/dev/null | head -1 > /dev/null 2>&1; then
    NEXT_FILE=$(_select_next_file "$PENDING_DIR")
    if [ -n "$NEXT_FILE" ] && [ -f "$NEXT_FILE" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') Selected: $(basename "$NEXT_FILE")"
        if [ "$DRY_RUN" = "true" ]; then
            echo "[DRY-RUN] Would move: $NEXT_FILE → $RUNNING_DIR/"
            exit 0
        fi
        mkdir -p "$RUNNING_DIR"
        mv "$NEXT_FILE" "$RUNNING_DIR/"
        DIRECTIVES_DIR="$RUNNING_DIR"
    fi
fi
```

## 작업 2: P0 긴급 선점 (PREEMPT_P0)

추가된 코드:
```bash
if [ "${PREEMPT_P0:-false}" = "true" ]; then
    P0_EXISTS=$(grep -rl "P0-CRITICAL" "${PENDING_DIR}"/*.md 2>/dev/null | head -1 || true)
    RUNNING_EXISTS=$(ls "${RUNNING_DIR}"/*.md 2>/dev/null | head -1 || true)
    if [ -n "$P0_EXISTS" ] && [ -n "$RUNNING_EXISTS" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') P0 PREEMPT: Moving running task back to pending"
        mv "${RUNNING_DIR}"/*.md "${PENDING_DIR}/"
    fi
fi
```

## 작업 3: bridge.py 파일명 우선순위 포함

**파일**: `/root/aads/scripts/bridge.py` (→ `/root/aads/aads-server/scripts/genspark_bridge.py`)

추가된 `_generate_filename()` 함수:
```python
def _generate_filename(content: str, project: str = "AADS") -> str:
    """
    지시서 파일명 생성 — 우선순위 감지 후 파일명에 반영.
    예: AADS_20260306_120317_P0_BRIDGE.md (P0-CRITICAL인 경우)
        AADS_20260306_120317_P1_BRIDGE.md (P1-HIGH인 경우)
        AADS_20260306_120317_P2_BRIDGE.md (기본값)
    """
    timestamp = datetime.now(timezone(timedelta(hours=9))).strftime("%Y%m%d_%H%M%S")
    priority = "P2"  # 기본값
    if "P0-CRITICAL" in content:
        priority = "P0"
    elif "P1-HIGH" in content:
        priority = "P1"
    return f"{project}_{timestamp}_{priority}_BRIDGE.md"
```

auto_trigger.sh의 파일명 기반 정렬 (이미 _select_next_file에 포함):
```bash
# 파일명에 P0이 있으면 먼저
NEXT_FILE=$(ls "$PENDING_DIR"/*_P0_*.md 2>/dev/null | head -1)
if [ -z "$NEXT_FILE" ]; then
    NEXT_FILE=$(ls "$PENDING_DIR"/*_P1_*.md 2>/dev/null | head -1)
fi
if [ -z "$NEXT_FILE" ]; then
    NEXT_FILE=$(ls -t "$PENDING_DIR"/*.md 2>/dev/null | tail -1)
fi
```

## 작업 4: 로깅

`_log_priority()` 함수가 `/var/log/aads/auto_trigger_priority.log`에 기록:
```
2026-03-06 12:30:00 | SCAN: P0=1, P1=2, P2=3 | SELECTED: AADS_T105_P0_CRITICAL.md | REASON: P0-CRITICAL priority
```

로그 포맷 구현:
```bash
_log_priority() {
    local p0="$1" p1="$2" p2="$3" selected="$4"
    local log_dir="/var/log/aads"
    mkdir -p "$log_dir" 2>/dev/null || true
    if [ -n "$selected" ]; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') | SCAN: P0=${p0}, P1=${p1}, P2=${p2} | SELECTED: ${selected}" \
            >> "${PRIORITY_LOG}" 2>/dev/null || true
    fi
}
```

참고: /var/log/aads는 root:root 755 소유로, claudebot 사용자로 실행 시 쓰기 불가.
auto_trigger.sh는 `2>/dev/null || true`로 처리하여 실행 실패 없음. root 권한으로 실행 시 정상 로깅.

## 작업 5: 검증

### dry-run 테스트 (실제 pending/ 파일 포함)
```
$ echo "P0-CRITICAL test" > /root/.genspark/directives/pending/TEST_P0.md
$ echo "P2-NORMAL test" > /root/.genspark/directives/pending/TEST_P2.md
$ PENDING_DIR=/root/.genspark/directives/pending bash scripts/auto_trigger.sh --dry-run

======================================================
AADS Auto Trigger
감시 디렉토리: /root/.genspark/directives/running
시작: 2026-03-06 12:41 KST
======================================================
2026-03-06 12:41:48 Selected: AADS_20260306_123542_BRIDGE.md
[DRY-RUN] Would move: /root/.genspark/directives/pending/AADS_20260306_123542_BRIDGE.md → /root/.genspark/directives/running/
```

(AADS_20260306_123542_BRIDGE.md가 P0-CRITICAL 내용을 포함하여 먼저 선택됨. TEST_P2.md는 선택 안 됨)

### 순수 P0/P2 테스트 (임시 디렉토리)
```
=== 임시 pending 파일 ===
TEST_P0.md
TEST_P2.md

=== _select_next_file 로직 직접 테스트 ===
Selected: TEST_P0.md
Expected: TEST_P0.md
✅ PASS: P0이 먼저 선택됨
```

### _generate_filename 테스트
```
P0 파일명: AADS_20260306_124223_P0_BRIDGE.md
P1 파일명: AADS_20260306_124223_P1_BRIDGE.md
P2 파일명: AADS_20260306_124223_P2_BRIDGE.md
✅ _generate_filename 모두 PASS
```

테스트 파일 정리 완료:
```
$ rm /root/.genspark/directives/pending/TEST_P0.md
$ rm /root/.genspark/directives/pending/TEST_P2.md
```

## 작업 6: Git + HANDOVER

### aads-server 커밋/푸시
```
$ cd /root/aads/aads-server
$ git add scripts/auto_trigger.sh scripts/genspark_bridge.py
$ git commit -m "[AADS] feat(T-106): auto_trigger 우선순위 실행 — P0→P1→P2, 긴급 선점, 파일명 우선순위"
[main a52e513] ...
 2 files changed, 937 insertions(+)
 create mode 100755 scripts/auto_trigger.sh
 create mode 100755 scripts/genspark_bridge.py
$ git push origin main
To https://github.com/moongoby-GO100/aads-server.git
   51765b7..a52e513  main -> main
```

### aads-docs HANDOVER v5.29 업데이트
```
$ cd /root/aads/aads-docs
$ git add HANDOVER.md
$ git commit -m "docs(T-106): HANDOVER v5.29 — auto_trigger 우선순위 실행 로직"
[main cb7af32] ...
 1 file changed, 1 insertion(+), 1 deletion(-)
$ git push origin main
To https://github.com/moongoby-GO100/aads-docs.git
   b97948e..cb7af32  main -> main
```

## 최종 결과 요약

| 항목 | 결과 |
|------|------|
| 작업1: 우선순위 정렬 | ✅ P0→P1→P2 FIFO 구현 |
| 작업2: PREEMPT_P0 선점 | ✅ 구현 완료 |
| 작업3: 파일명 우선순위 | ✅ _generate_filename() + _select_next_file 통합 |
| 작업4: 우선순위 로그 | ✅ /var/log/aads/auto_trigger_priority.log (root 실행 시 쓰기) |
| 작업5: 검증 테스트 | ✅ P0 우선 선택 PASS, 파일명 P0/P1/P2 PASS |
| 작업6: Git push | ✅ a52e513 (aads-server), cb7af32 (aads-docs) |
| HANDOVER | ✅ v5.29 업데이트 |
