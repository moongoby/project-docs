---
project: AADS
task_id: AADS-148
completed_at: 2026-03-07 13:52 KST
---

# AADS-148 실행 결과 보고서

## 작업 개요

/proc grep 고아 프로세스 CPU 독점 장애(2026-03-04~07, 3일, 서버 211) 대응:
Wrap 보고서 작성 + 교훈 L-010 등록 + 재발 방지 코드 변경

---

## 작업 1: Wrap 보고서 작성 ✅

**파일**: `/root/aads/aads-docs/reports/AADS-148-WRAP_proc-grep-blocking-incident.md`

### 작성 내용

```
# AADS-148 WRAP 보고서 — /proc grep 고아 프로세스 블로킹 장애

작성: 2026-03-07 | 작성자: Claude (AADS-148) | FLOW: D-016 Wrap up

## 1. 장애 요약
| 항목 | 내용 |
| 장애 발생 | 2026-03-04 |
| 장애 해소 | 2026-03-07 kill -9 20812 |
| 지속 시간 | 약 3일 (72시간+) |
| 영향 서버 | 서버 211 (211.188.51.113) |
| 원인 프로세스 | grep -r 73340093 /proc/*/fd/* (PID 20812) |
| 부모 세션 | PID 20810 (claude_exec.sh → claude --print) |
| CPU 영향 | 1코어 100% 독점 |
| 후속 영향 | postgres INSERT 작업 큐 적체 (자연 해소) |

## 2. 장애 타임라인
2026-03-04: claude_exec.sh 세션(PID 20810) 실행 → Claude Code가
/proc/*/fd/* grep -r 실행 → 소켓·파이프 fd read 블로킹 → PID 20812 CPU 100% 점유
부모 PID 20810 종료 → PID 20812가 PPID=1 고아로 잔존
2026-03-04~06: 3일간 CPU 1코어 100% 독점, session_watchdog 탐지 실패
2026-03-07: CEO 수동 kill -9 20812 → 정상화

## 3. 근본 원인 분석
직접 원인: /proc/*/fd/* grep -r → 소켓/파이프 fd I/O 무한 블로킹
구조적 원인:
  1. /proc, /sys grep 금지 규칙 부재 (Claude Code 프롬프트)
  2. 프로세스 그룹 단위 kill 미적용 (개별 PID만 kill)
  3. session_watchdog 고아(PPID=1) 프로세스 탐지 없음
  4. 장기 실행 고아 프로세스 자동 kill 로직 없음

## 4. 영향 범위
CPU: 서버 211 1코어 100% × 72시간+
서비스: KIS, GO100 작업 처리 지연
PostgreSQL: INSERT 큐 적체 → 자연 해소
재정: $0.5~$1 추정

## 5. 조치 내역 (AADS-148)
1. /proc, /sys grep -r 금지 규칙 → CONTEXT_HEADER 주입 ✅
2. 세션 종료 시 프로세스 그룹 전체 kill (kill -- -$PGID) ✅
3. cleanup에 고아 프로세스 정리 로직 ✅
4. session_watchdog 고아 프로세스 탐지+kill 로직 ✅
5. 교훈 L-010 등록 ✅
```

---

## 작업 2: 교훈 L-010 등록 ✅

**파일**: `/root/aads/aads-docs/shared/lessons/infra/L-010_proc-grep-orphan-process.md`

### 작성 내용 (YAML 프론트매터 + 핵심 교훈 형식)

```markdown
---
id: L-010
title: /proc grep 블로킹 + 고아 프로세스 CPU 독점 방지
category: infra
severity: critical
task_ref: AADS-148
created_at: 2026-03-07
---

## 핵심 교훈
Claude Code에서 /proc, /sys 경로에 grep -r을 실행하면
소켓·파이프 fd가 무한 블로킹되어 CPU 100%를 수일간 독점할 수 있다.
...

## 문제
- grep -r 73340093 /proc/*/fd/* 실행 → I/O 블로킹
- 부모 세션 종료 후 grep 자식이 PPID=1 고아로 잔존
- 3일간 CPU 1코어 100% 독점

## 해결책
규칙 1: Claude Code /proc, /sys grep 금지 → pgrep, ps, lsof 사용
규칙 2: 프로세스 그룹 단위 kill (kill -- -$PGID)
규칙 3: session_watchdog 고아 프로세스 탐지 (ppid=1 AND elapsed>3600s)

## 결과
Before: grep /proc 블로킹 → CPU 100% × 3일
After: 컨텍스트 규칙 주입 + PGID kill + 고아 탐지 자동화
```

**INDEX.md 업데이트** (`/root/aads/aads-docs/shared/lessons/INDEX.md`):

```diff
-# 공유 교훈 INDEX (최종: 2026-03-06, 8건)
+# 공유 교훈 INDEX (최종: 2026-03-07, 10건)

 ## infra (서버·디스크·Docker·네트워크)
 ...
+- L-009: 4계층 자기치유 아키텍처 패턴 [AADS-134] → infra/L-009.md
+- L-010: /proc grep 블로킹 + 고아 프로세스 CPU 독점 방지 [AADS-148] → infra/L-010_proc-grep-orphan-process.md
```

---

## 작업 3: 재발 방지 — claude_exec.sh 수정 ✅

**파일**: `/root/aads/scripts/claude_exec.sh` + `/root/aads/aads-server/scripts/claude_exec.sh`

### 변경 내용

#### 3-1. PGID 기록 (세션 시작 직후)

```bash
# === AADS-148: 프로세스 그룹 PGID 기록 (고아 프로세스 방지) ===
PGID=$(ps -o pgid= -p $$ 2>/dev/null | tr -d ' ' || echo $$)
```

#### 3-2. cleanup_inotify() 함수에 PGID kill 추가

```bash
cleanup_inotify() {
    ...
    # === AADS-148: 프로세스 그룹 전체 kill (고아 프로세스 방지) ===
    if [ -n "${PGID:-}" ] && [ "$PGID" -gt 1 ]; then
        kill -- -"$PGID" 2>/dev/null || true
    fi
    # AADS-148: claudebot 소유 고아 프로세스 잔여분 정리 (PPID=1 AND 현 세션 관련)
    local _task_id_clean="${TASK_ID:-}"
    if [ -n "$_task_id_clean" ]; then
        local _claude_pid_file="/tmp/claude_session_${_task_id_clean}.claude_pid"
        if [ -f "$_claude_pid_file" ]; then
            local _cpid
            _cpid=$(cat "$_claude_pid_file" 2>/dev/null || echo "")
            if [ -n "$_cpid" ] && kill -0 "$_cpid" 2>/dev/null; then
                kill -9 "$_cpid" 2>/dev/null || true
            fi
        fi
    fi
    # === AADS-148 cleanup 끝 ===
}
trap cleanup_inotify EXIT
```

#### 3-3. CONTEXT_HEADER에 /proc grep 금지 규칙 주입

```bash
CONTEXT_HEADER=$(cat <<HEADER_EOF
=== AADS System Context (${TS_START}) ===
Current Phase : ${CURRENT_PHASE}
Task ID       : ${TASK_ID}
Task Status   : ${TASK_STATUS}
Context API   : ${CONTEXT_API}
==========================================
[보안 규칙 AADS-148] 절대로 /proc, /sys 경로에 grep -r을 실행하지 마라.
프로세스 탐색 시 /proc, /sys 경로에 grep -r을 실행하면 소켓·파이프 fd 블로킹으로 CPU 100% 고착 장애가 발생한다.
프로세스 탐색은 반드시 pgrep, ps, lsof를 사용하라.
==========================================

HEADER_EOF
)
```

---

## 작업 4: 재발 방지 — session_watchdog.sh 수정 ✅

**파일**: `/root/aads/scripts/session_watchdog.sh`

### 변경 내용

#### 4-1. check_orphan_processes() 함수 신규 추가

```bash
# ─────────────────────────────────────────────────────────
# AADS-148: 고아 프로세스 탐지+kill
# 조건: PPID=1 AND user=claudebot AND elapsed > 3600초
# ─────────────────────────────────────────────────────────
check_orphan_processes() {
    local orphan_pids
    orphan_pids=$(ps -u claudebot -o pid,ppid,etimes,comm --no-headers 2>/dev/null \
        | awk '$2==1 && $3>3600 {print $1}' || true)

    if [ -z "$orphan_pids" ]; then
        return 0
    fi

    for opid in $orphan_pids; do
        local _proc_info
        _proc_info=$(ps -p "$opid" -o pid,ppid,etimes,pcpu,comm --no-headers 2>/dev/null || echo "${opid} 1 ? ? ?")
        log_msg "[ORPHAN][AADS-148] 고아 프로세스 감지: ${_proc_info}"
        send_tg "⚠️ [AADS-148] 고아 프로세스 감지 (ppid=1, >1h): pid=${opid} | ${_proc_info} → kill -9"
        kill -9 "$opid" 2>/dev/null && log_msg "[ORPHAN] killed pid=${opid}" || log_msg "[ORPHAN] kill 실패 pid=${opid} (이미 종료?)"
    done
}
```

#### 4-2. 메인 루프에 고아 탐지 호출 추가 (60초마다)

```bash
    # AADS-148: 고아 프로세스 탐지 (60초마다 — sleep 10 × 6회)
    _orphan_check_counter=$(( ${_orphan_check_counter:-0} + 1 ))
    if [ "${_orphan_check_counter}" -ge 6 ]; then
        check_orphan_processes
        _orphan_check_counter=0
    fi

    sleep 10
done
```

#### 4-3. 시작 로그 버전 업데이트

```bash
-log_msg "session_watchdog started (pid=$$) — AADS-140+141"
+log_msg "session_watchdog started (pid=$$) — AADS-140+141+148"
```

---

## Git 커밋 및 Push

### aads-docs (reports + lessons + INDEX + HANDOVER)

```
커밋 1: feat(AADS-148): /proc grep 고아 프로세스 블로킹 장애 Wrap + 교훈 + 재발방지
  SHA: b96e6f7
  파일: reports/AADS-148-WRAP_proc-grep-blocking-incident.md (신규)
        shared/lessons/infra/L-010_proc-grep-orphan-process.md (신규)
        shared/lessons/INDEX.md (수정: L-009, L-010 추가, 10건)

커밋 2: chore(AADS-148): HANDOVER v8.4 — AADS-148 완료 반영
  SHA: 45af9ca
  파일: HANDOVER.md (v8.3 → v8.4, AADS-148 완료 섹션 추가)

Push: c48695d → 45af9ca (origin/main)
```

### aads-server (claude_exec.sh)

```
커밋: feat(AADS-148): claude_exec.sh 프로세스 그룹 kill + /proc grep 금지 주입
  SHA: 2b7b16d
  파일: scripts/claude_exec.sh (수정: PGID kill + CONTEXT_HEADER 규칙 주입)

Push: 1024f7b → 2b7b16d (origin/main)
```

---

## 성공 기준 검증

| # | 기준 | 결과 |
|---|------|------|
| 1 | reports/AADS-148-WRAP_proc-grep-blocking-incident.md GitHub push | ✅ b96e6f7 push |
| 2 | shared/lessons/infra/L-010_proc-grep-orphan-process.md 생성 + INDEX.md 등록 | ✅ 완료 |
| 3 | claude_exec.sh 프로세스 그룹 kill 로직 추가 | ✅ kill -- -$PGID 추가 |
| 4 | Claude Code 프롬프트 /proc grep 금지 규칙 주입 | ✅ CONTEXT_HEADER 주입 |
| 5 | session_watchdog.sh 고아 프로세스 탐지+kill 로직 추가 | ✅ check_orphan_processes() 추가 |
| 6 | 전체 프로젝트 공통 적용 (aads-server/scripts/claude_exec.sh 동기화) | ✅ 완료 |

---

## GitHub 브라우저 경로

- WRAP 보고서: https://github.com/moongoby-GO100/aads-docs/blob/main/reports/AADS-148-WRAP_proc-grep-blocking-incident.md
- 교훈 L-010: https://github.com/moongoby-GO100/aads-docs/blob/main/shared/lessons/infra/L-010_proc-grep-orphan-process.md
- INDEX.md: https://github.com/moongoby-GO100/aads-docs/blob/main/shared/lessons/INDEX.md
- claude_exec.sh (aads-server): https://github.com/moongoby-GO100/aads-server/blob/main/scripts/claude_exec.sh

---

## 최종 상태

- aads-docs: `45af9ca` (main, pushed)
- aads-server: `2b7b16d` (main, pushed)
- session_watchdog.sh: `/root/aads/scripts/session_watchdog.sh` (수정, git 미추적 — 로컬 적용)
- HANDOVER: v8.4 (2026-03-07)
