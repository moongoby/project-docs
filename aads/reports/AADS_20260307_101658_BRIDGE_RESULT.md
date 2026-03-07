---
project: AADS
task_id: AADS-145
completed_at: 2026-03-07 11:10:00 KST
commit_sha_aads_server: 51a544f3809141bdafaf617d6d2a6cc2aa035b6a
commit_sha_aads_docs: 1b28a481a3206bfdceb8e1a0120b504c747c2d84
---

# AADS-145 RESULT — EFFICIENCY Phase1 파이프라인 고도화

## 1. Tasks 시스템 통합

### 변경 파일
- `/root/aads/scripts/claude_exec.sh` (실행본 + aads-server git sync)
- `/root/aads/claude_exec.sh` (main 실행본)
- `/root/aads/scripts/auto_trigger.sh`

### 구현 내용

#### scripts/claude_exec.sh (lines 25-57)
```bash
# === AADS-145: Tasks 시스템 통합 ===
CLAUDEBOT_TASKS_DIR="/home/claudebot/.claude/tasks"
mkdir -p "$CLAUDEBOT_TASKS_DIR" 2>/dev/null || true
TASK_FILE="${CLAUDEBOT_TASKS_DIR}/${TASK_ID}.json"
TASK_LIST_ID="aads-$(echo "$TASK_ID" | tr '[:upper:]' '[:lower:]')-$(date +%s)"

# 세션 복구: Tasks 파일에 이미 done이면 스킵 (PENDING/DONE 이중관리 제거)
if [ -f "$TASK_FILE" ]; then
    _tasks_prev=$(python3 -c "import json; d=json.load(open('${TASK_FILE}')); print(d.get('status',''))" 2>/dev/null || echo "")
    if [ "${_tasks_prev}" = "done" ]; then
        echo "✅ [TASKS] ${TASK_ID} 이미 완료 (Tasks 기록) — 스킵"
        exit 0
    fi
fi

# Tasks 파일 생성 (in_progress 상태)
python3 -c "
import json, time
task = {
    'id': '${TASK_ID}',
    'list_id': '${TASK_LIST_ID}',
    'title': '${TASK_ID}',
    'status': 'in_progress',
    'directive': '${DIRECTIVE_FILE:-none}',
    'created_at': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
}
with open('${TASK_FILE}', 'w') as f:
    json.dump(task, f, ensure_ascii=False, indent=2)
" 2>/dev/null || true

export CLAUDE_CODE_TASK_LIST_ID="${TASK_LIST_ID}"
echo "[TASKS] list_id=${TASK_LIST_ID} file=${TASK_FILE}"
# === Tasks 통합 끝 ===
```

#### claude_exec.sh main (lines 307-345)
- TASK_ID_EXEC 추출: directive 파일 `task_id:` 필드에서 파싱
- TASK_LIST_ID 생성: `aads-{lowercase_task_id}-{epoch}`
- TASK_FILE: `/home/claudebot/.claude/tasks/{TASK_ID_EXEC}.json`
- 세션 복구: Tasks JSON `status == "done"` 시 즉시 exit 0 (RUNNING_DIR 정리 포함)
- Tasks JSON 생성 시 project, result, directive 경로 포함
- `export CLAUDE_CODE_TASK_LIST_ID="${TASK_LIST_ID}"` → claudebot 환경에 주입

#### auto_trigger.sh _process_directive (lines 389-399)
```bash
# ─── AADS-145: Tasks 시스템으로 완료 여부 확인 (PENDING/DONE 이중관리 제거) ───
local _tasks_json="/home/claudebot/.claude/tasks/${task_id}.json"
if [ -f "$_tasks_json" ]; then
    local _ts
    _ts=$(python3 -c "import json; d=json.load(open('${_tasks_json}')); print(d.get('status',''))" 2>/dev/null || echo "")
    if [ "$_ts" = "done" ]; then
        echo "  ✅ [TASKS] 이미 완료 (${task_id}) — 스킵"
        return 0
    fi
fi
```
→ API current_progress 조회 이전에 Tasks JSON 체크. done이면 API 호출 없이 즉시 스킵.

#### Tasks 완료 업데이트 (scripts/claude_exec.sh 끝 부분)
```bash
# === AADS-145: Tasks 완료 상태 업데이트 ===
if [ -n "${TASK_FILE:-}" ] && [ -f "$TASK_FILE" ]; then
    _t_done_status="failed"
    [ $EXEC_EXIT -eq 0 ] && _t_done_status="done"
    python3 -c "
import json, time
try:
    with open('${TASK_FILE}') as f: d = json.load(f)
    d['status'] = '${_t_done_status}'
    d['completed_at'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    d['exit_code'] = ${EXEC_EXIT}
    with open('${TASK_FILE}', 'w') as f: json.dump(d, f, ensure_ascii=False, indent=2)
except: pass
" 2>/dev/null || true
fi
```

---

## 2. 투기적 실행 (AADS-141 확장)

### 구현 내용

#### 하트비트 "type":"final_commit" 이벤트 (scripts/claude_exec.sh lines 295-300)
```bash
# AADS-145: final_commit 하트비트 + 신호 파일 (투기적 실행 트리거)
_fc_sha=$(git -C "${WORK_DIR}" rev-parse HEAD 2>/dev/null | tr -d '[:space:]' || echo "")
if [ -n "$_fc_sha" ]; then
    update_heartbeat "final_commit" "sha=${_fc_sha:0:8}"
    echo "${TASK_ID}" > "/tmp/aads_final_commit_${TASK_ID}.signal"
fi
```
- `update_heartbeat "final_commit" "sha=XXXXXXXX"` → HEARTBEAT_FILE에 JSON 기록
- `/tmp/aads_final_commit_{task_id}.signal` → auto_trigger.sh가 감지하는 신호 파일

#### main claude_exec.sh final_commit 신호 (line 604-609)
```bash
# === AADS-145: final_commit 투기적 실행 신호 ===
if [ -n "${_commit_sha:-}" ]; then
    echo "${TASK_ID_EXEC:-${FILENAME%.md}}" > "/tmp/aads_final_commit_${TASK_ID_EXEC:-exec}.signal"
    echo "[$(date '+%Y-%m-%d %H:%M:%S KST')] [FINAL-COMMIT] 신호 파일 생성 (sha=${_commit_sha:0:8})" >> "$LOG_FILE"
fi
```

#### _speculative_preload() 함수 (auto_trigger.sh lines 201-226)
```bash
# ─── AADS-145: 투기적 실행 — final_commit 기반 다음작업 프리로드 ─
_speculative_preload() {
    local _pend_dir="$1" _fail_flag="$2"
    # 다음 후보 선택
    local _next_file
    _next_file=$(_select_next_file "$_pend_dir" 2>/dev/null) || return 0
    [ -z "$_next_file" ] || [ ! -f "$_next_file" ] && return 0
    echo "[$(date '+%Y-%m-%d %H:%M:%S KST')] [SPEC-PRELOAD] 다음 작업 git pull 시작: $(basename "$_next_file")"
    # 주요 repo git pull 선제 실행 (컨텍스트 준비)
    for _repo_dir in /root/aads/aads-docs /root/aads/aads-server /root/aads/aads-dashboard; do
        if [ -d "${_repo_dir}/.git" ]; then
            git -C "$_repo_dir" pull --quiet 2>/dev/null &
        fi
    done
    wait 2>/dev/null
    # 후처리 실패 확인
    if [ -f "$_fail_flag" ]; then
        echo "[$(date '+%Y-%m-%d %H:%M:%S KST')] [SPEC-PRELOAD] 후처리 실패 감지 — 프리로드 취소"
        rm -f "$_fail_flag"
        return 1
    fi
    echo "[$(date '+%Y-%m-%d %H:%M:%S KST')] [SPEC-PRELOAD] 프리로드 완료: $(basename "$_next_file")"
    return 0
}
```

#### final_commit 감지 및 투기적 프리로드 호출 (auto_trigger.sh lines 443-450)
```bash
# AADS-145: final_commit 신호 감지 → 투기적 프리로드 (후처리와 병렬)
local _fc_signal="/tmp/aads_final_commit_${task_id}.signal"
local _preload_fail="/tmp/aads_preload_fail_${task_id}_$$"
if [ -f "$_fc_signal" ]; then
    rm -f "$_fc_signal"
    echo "  🚀 [SPEC] final_commit 감지 — 다음 작업 프리로드 병렬 시작"
    _speculative_preload "$PENDING_DIR" "$_preload_fail" &
fi
```

#### 후처리 실패시 취소 (auto_trigger.sh lines 529-530)
```bash
# AADS-145: 투기적 프리로드 취소 (실행 실패시)
[ -n "${_preload_fail:-}" ] && touch "$_preload_fail" 2>/dev/null || true
```

---

## 3. 컨텍스트 자동관리

### 구현 내용

#### main claude_exec.sh — _ctx_monitor() 함수 (lines 427-477)

```bash
# === AADS-145: 컨텍스트 모니터링 백그라운드 ===
CTX_MAX_TOKENS=200000
CTX_SIGNAL="/tmp/.ctx_overload_${$}"
CTX_EDIT_FAIL_SIGNAL="/tmp/.ctx_edit_fail_${$}"

_ctx_monitor() {
    local _log="$1" _sig="$2" _edit_sig="$3"
    local _warned_70=false
    while true; do
        sleep 15
        [ -f "$_log" ] || continue
        # 2회 연속 수정 실패 감지 (Edit 오류 패턴)
        local _efail
        _efail=$(grep -c "old_string.*not found\|no match found\|수정 실패\|Edit.*failed" "$_log" 2>/dev/null || echo 0)
        if [ "${_efail:-0}" -ge 2 ] && [ ! -f "$_edit_sig" ]; then
            echo "[$(date '+%Y-%m-%d %H:%M:%S KST')] [CTX-EDIT-FAIL] 2회 연속 수정 실패 → /clear 권고" >> "$_log"
            touch "$_edit_sig"
        fi
        # JSON output-format에서 token usage 파싱
        local _max_t
        _max_t=$(tail -1000 "$_log" 2>/dev/null | python3 -c "
import sys, json
mx=0
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    try:
        d=json.loads(line)
        u=d.get('usage',{}) or {}
        t=u.get('input_tokens',0) or 0
        if t>mx: mx=t
    except: pass
print(mx)
" 2>/dev/null || echo 0)
        [ -z "$_max_t" ] && _max_t=0
        if [ "$_max_t" -gt 0 ] 2>/dev/null; then
            local _pct=$(( _max_t * 100 / CTX_MAX_TOKENS ))
            if [ "$_pct" -ge 90 ]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S KST')] [CTX-90%] 컨텍스트 90% 초과 → 재시작 신호" >> "$_log"
                touch "$_sig"
                break
            elif [ "$_pct" -ge 70 ] && [ "$_warned_70" = "false" ]; then
                echo "[$(date '+%Y-%m-%d %H:%M:%S KST')] [CTX-70%] 컨텍스트 70% — /compact 권고" >> "$_log"
                _warned_70=true
            fi
        fi
    done
}

_ctx_monitor "$LOG_FILE" "$CTX_SIGNAL" "$CTX_EDIT_FAIL_SIGNAL" &
CTX_MONITOR_PID=$!
```

#### 90% 재시작 처리 (main claude_exec.sh lines 497-514)
```bash
# === AADS-145: 컨텍스트 모니터 종료 + 90% 재시작 처리 ===
kill $CTX_MONITOR_PID 2>/dev/null
if [ -f "$CTX_SIGNAL" ]; then
    rm -f "$CTX_SIGNAL" "$CTX_EDIT_FAIL_SIGNAL"
    echo "[CTX-RESTART] 컨텍스트 90% 초과 — 중간 결과 저장 후 재시작" >> "$LOG_FILE"
    # 중간 결과 기록
    cat >> "$RESULT_FILE" <<_MIDRESULT_MARKER 2>/dev/null
## 중간 결과 저장 (컨텍스트 90% 초과)
재시작 시각: $(date '+%Y-%m-%d %H:%M:%S KST')
_MIDRESULT_MARKER
    # 재시작: 짧은 컨텍스트 요약으로
    timeout ${MAX_TIMEOUT} su - claudebot -c \
      "cd ${WORKDIR} && $(which claude) -p \
      --dangerously-skip-permissions --max-turns ${MAX_TURNS} --model ${MODEL} --output-format json \
      '이전 세션 컨텍스트 한계로 재시작. 작업 디렉토리: ${WORKDIR}. cat ${DIRECTIVE_FILE} 읽고 미완성 작업 이어서 완료. 결과를 ${RESULT_FILE} 에 이어 저장.'" \
      >> "$LOG_FILE" 2>&1
    EXIT_CODE=$?
fi
```

#### scripts/claude_exec.sh — 행 수 기반 추정 모니터링
```bash
# AADS-145: 컨텍스트 모니터링용 임시 로그
CTX_TMPLOG="/tmp/claude_ctx_${TASK_ID}_$$.log"
CTX_SIGNAL="/tmp/.ctx_sig_${TASK_ID}_$$.flag"
CTX_EDIT_FAIL="/tmp/.ctx_edit_${TASK_ID}_$$.flag"

_ctx_monitor_bg() {
    ...
    # 행 수 기반 토큰 추정 (~50자/행 × 행 수 ÷ 4 ≈ 토큰)
    local _lines
    _lines=$(wc -l < "$_tmplog" 2>/dev/null || echo 0)
    local _est_tokens=$(( _lines * 50 / 4 ))
    if [ "$_est_tokens" -ge $(( _ctx_max * 90 / 100 )) ]; then
        touch "$_sig"
        break
    elif [ "$_est_tokens" -ge $(( _ctx_max * 70 / 100 )) ] && [ "$_warned_70" = "false" ]; then
        ...
    fi
    ...
}

# tee로 출력 캡처
timeout "$HARD_TIMEOUT" bash -c 'echo "$FULL_PROMPT" | claude --print 2>&1' | tee -a "$CTX_TMPLOG" || EXEC_EXIT=$?
```

---

## 4. git-push 감시 (AADS-143 검증)

이미 구현 완료 (AADS-143):
- `auto_trigger.sh`: `verify_git_push()` — GitHub raw URL curl 3회 backoff 재시도 + Telegram 알림 + recovery_logs DB 기록
- `claude_exec.sh`: commit SHA RESULT_FILE YAML 헤더에 자동 삽입

AADS-145에서 추가:
- `final_commit` 신호 파일로 auto_trigger.sh가 push 검증과 동시에 다음 작업 프리로드 병렬 실행

---

## 커밋 정보

| 레포 | SHA | 내용 |
|------|-----|------|
| aads-server | 51a544f | feat(AADS-145): scripts sync (claude_exec.sh + auto_trigger.sh) |
| aads-docs | 1b28a48 | docs(AADS-145): HANDOVER v8.1 |

---

## success_criteria 검증

| 항목 | 구현 | 상태 |
|------|------|------|
| Tasks 통합 동작 | CLAUDE_CODE_TASK_LIST_ID export + ~/.claude/tasks/{id}.json 생성/복구/완료 | ✅ |
| final_commit→즉시프리로드 동작 | update_heartbeat("final_commit") + signal 파일 + _speculative_preload() 병렬 | ✅ |
| 컨텍스트 자동관리 동작 | _ctx_monitor() 백그라운드 70%/90% + CTX-EDIT-FAIL 2회 감지 | ✅ |
| push감시 3회재시도+알림 동작 | verify_git_push() AADS-143 이미 완료 + final_commit 연계 | ✅ |

---

## 변경 파일 목록

1. `/root/aads/scripts/claude_exec.sh` — Tasks 통합, final_commit 하트비트, ctx 모니터링
2. `/root/aads/scripts/auto_trigger.sh` — _speculative_preload, Tasks 상태 체크, final_commit 감지
3. `/root/aads/claude_exec.sh` — Tasks 통합, ctx 모니터링 (_ctx_monitor JSON token), final_commit 신호
4. `/root/aads/aads-server/scripts/claude_exec.sh` — git sync (위 #1 내용)
5. `/root/aads/aads-server/scripts/auto_trigger.sh` — git sync (위 #2 내용)
6. `/root/aads/aads-docs/HANDOVER.md` — v8.1, AADS-145 반영
7. `/root/aads/aads-docs/HANDOVER-HISTORY.md` — AADS-145 완료 사항 추가
