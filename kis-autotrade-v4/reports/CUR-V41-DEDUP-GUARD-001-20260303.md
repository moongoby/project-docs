---
project: KIS
task_id: CUR-V41-DEDUP-GUARD-001
completed_at: 2026-03-03 12:37 KST
status: completed
---

# CUR-V41-DEDUP-GUARD-001: 중복 작업 방지(Dedup Guard) 구현

## 작업 요약

auto_trigger.sh에 TASK ID 기반 중복 실행 방지 로직을 추가하여, 동일 작업이 여러 세션에서
동시에 실행되는 문제를 해결함.

## 배경

- `CUR-V41-DESK2-ACTIVATE-003` 동일 TASK가 BRIDGE 지시서 3개로 중복 발행
- `collect_ohlcv_daily.py --dates 20260302` 4개 동시 실행 확인
- claude_exec.sh 인스턴스 3개가 동시에 동일 작업 수행 중

## 1단계: 중복 프로세스 즉시 정리

- 12:22/12:28 BRIDGE 세션 강제 종료 (PID: 2405739, 2405740, 2407520, 2413292, 2413293 등)
- `collect_ohlcv_daily.py` 중복 3개 종료 → 1개(12:21 기동, PID 2404122) 유지
- 중복 지시서 2개 → `directives/cancelled/` 이동

## 2단계: auto_trigger.sh 중복 방지 패치

### 추가 함수 (로컬 실행 섹션)

```bash
# TASK ID 추출 (파일 내 "TASK: CUR-V41-..." 라인)
get_task_id() {
    grep -m1 '^TASK:' "$1" 2>/dev/null | awk '{print $2}' | tr -d '[:space:]'
}

# running 디렉터리에 동일 TASK ID 존재 여부 확인
is_task_running() {
    local task_id="$1"
    [ -z "$task_id" ] && return 1
    grep -rl "^TASK:.*${task_id}" "$RUNNING_DIR"/*.md 2>/dev/null | grep -q .
}
```

### pending → running 이동 전 중복 체크

```bash
task_id=$(get_task_id "$file")
if [ -n "$task_id" ] && is_task_running "$task_id"; then
    log "[중복SKIP] TASK=${task_id} 이미 실행 중 — $fname 를 cancelled로 이동"
    mv "$file" "$CANCELLED_DIR/$fname"
    bash /root/.genspark/notify_telegram.sh \
        "⚠️ [${proj_upper}] 중복 TASK 차단: ${task_id} (${fname})" 2>/dev/null
    continue
fi
```

## 3단계: security_scan.sh false positive 수정

- Chrome 버전 `121.0.0.0` 이 IP로 오탐되는 문제 수정
- `user_agent|Mozilla|Chrome|Safari|AppleWebKit|Windows NT` 라인 IP 스캔 제외

## 4단계: 기존 보고서 보안 마스킹

| 파일 | 마스킹 내용 |
|---|---|
| KIS_20260303_094813_BRIDGE_RESULT.md | DB_PASSWORD=[MASKED] |
| KIS_20260303_115637_BRIDGE_RESULT.md | DATABASE_URL 패스워드=[MASKED] |
| GO100_20260303_095745_BRIDGE_RESULT.md | 비밀번호=[MASKED], 이메일=[MASKED_EMAIL] |
| AADS 보고서 2개 | IP=[MASKED_IP] |
| KIS_20260303_094000_KST_RESULT.md | IP=[MASKED_IP] |
| KIS_DBFIX_20260303_115547_RESULT.md | DATABASE_URL 패턴=[MASKED_DB_URL] |

## 배포 현황

| 서버 | auto_trigger.sh | 상태 |
|---|---|---|
| 211서버 (KIS/GO100) | 패치 적용 + 재시작 | PID 2419607 |
| 114서버 (SF/NTV2/NAS) | SCP 배포 + 재시작 | PID 2677637 |

## 검증 결과

- 중복 감지 테스트: `TEST-DEDUP-001` A파일(running) + B파일(pending) → B 차단 ✅
- security_scan.sh: **0건** ✅
- collect_ohlcv_daily: 1개만 실행 중 ✅

## 체크리스트

- [x] 로컬 파일 수정 완료 (auto_trigger.sh, security_scan.sh)
- [x] security_scan 0건
- [x] git commit & push
- [x] HTTP 200 확인
