---
project: AADS
task_id: AADS-168
completed_at: "2026-03-08T09:22:00+09:00"
---

# AADS-168 RESULT: 멀티서버 클로드봇 프로세스 감시 데몬 (claude_watchdog.py)

완료일: 2026-03-08 KST | 담당: Claude (서버 68, /root/aads) | 우선순위: P0-CRITICAL | 크기: L

---

## 1. 실행 요약

서버 68/211/114에서 claude_exec 좀비·headless 교착 프로세스가 파이프라인을 차단하는 장애에 대응하여,
멀티서버 자동 감시·정리·알림 시스템(`claude_watchdog.py`)을 구현하고 AADS API에 3개 엔드포인트를 추가했다.

### 완료 항목

| 항목 | 상태 | 비고 |
|------|------|------|
| claude_watchdog.py (파트 1~6) | 완료 | Python 3.6 호환, 488줄 |
| 자동 정리 CRITICAL kill -PGID | 완료 | TERM→3초→9+DB error |
| bridge.py 자동 재시작 | 완료 | SSH nohup |
| 고스트 PID 삭제 | 완료 | 경로 화이트리스트 보안 |
| Telegram 알림 | 완료 | CRITICAL/HIGH 분리 |
| JSON 보고서 저장 (30일 자동 삭제) | 완료 | /root/aads/logs/watchdog_reports/ |
| GET /ops/claude-processes | 완료 | 최근 20건 조회 |
| POST /ops/claude-cleanup | 완료 | dry_run 지원 |
| POST /ops/bridge-restart | 완료 | SSH 재시작 + 생존 확인 |
| systemd .service/.timer 파일 | 스테이징 완료 | root 설치 필요 |
| install_claude_watchdog.sh | 완료 | 설치 헬퍼 스크립트 |
| HANDOVER.md v11.2 | 완료 | AADS-168 섹션 |
| STATUS.md | 완료 | last_completed=AADS-168 |

### 미완료 항목 (root 권한 필요)

| 항목 | 사유 | 해결 방법 |
|------|------|----------|
| systemd timer 활성화 | /etc/systemd/system/ root 전용 (755) | `sudo bash /root/aads/scripts/install_claude_watchdog.sh` |
| 서버 211/114 SSH 감시 | claudebot SSH 키 미등록 | 서버 211/114에 claudebot 공개키 등록 |

---

## 2. 파일별 상세 실행 내용

### 2-1. /root/aads/scripts/claude_watchdog.py (신규 생성)

```
파일 크기: ~488줄
Python 버전: 3.6.8 호환 (list[dict] 등 PEP 585 제거, capture_output → PIPE)
```

**구조:**
- `_ssh_run()`: SSH 명령 실행 (허용 prefix 화이트리스트, 10초 타임아웃)
- `_ps_scan_local()`: 로컬 `ps -eo pid,ppid,pgid,etimes,stat,args`
- `_ps_scan_remote()`: SSH로 원격 ps 스캔
- `_zombie_count_local()` / `_zombie_count_remote()`: 좀비 수 조회
- `_classify_procs()`: claude_exec/claude_headless/session_watchdog 분류
- `_detect_issues()`: 임계값 기반 이슈 목록 생성
- `_check_211_services()`: bridge.py/auto_trigger/PID 파일 확인
- `_db_running_slots()`: psycopg2로 DB running 슬롯 조회
- `_db_fix_running()`: 정리된 PID의 running 레코드 error 업데이트
- `_kill_pgid_local()` / `_kill_pgid_remote()`: PGID kill (TERM→9)
- `_pkill_claude_stream_local()`: pkill 'claude.*stream-json'
- `_delete_ghost_pid_remote()`: 고스트 PID 파일 삭제 (경로 검증 포함)
- `_restart_bridge_211()`: SSH nohup bridge.py 재시작
- `_send_telegram()`: Telegram sendMessage API
- `_api_post()` + `_record_bridge_log()`: AADS API 연동
- `_save_report()`: JSON 보고서 저장 + 30일 이상 삭제
- `_scan_server_68/211/114()`: 서버별 스캔
- `_auto_cleanup()`: CRITICAL 자동 정리 + HIGH 보고
- `run_watchdog()`: 메인 함수 (스캔→이슈→정리→알림→보고서→API)

**보안 구현:**
```python
# SSH 명령 허용 prefix 화이트리스트
_ALLOWED_SSH_PREFIXES = (
    "ps ", "pgrep ", "wc ", "cat ", "echo ", "test ",
    "kill ", "pkill ", "nohup ", "python3 "
)

# 경로 이스케이프 차단
def _safe_path(p):
    if ".." in p:
        raise ValueError(f"경로 이스케이프 차단됨: {p}")
    return p

# PID 파일 허용 패턴
if not re.match(r"^/root/\.genspark/pids/[a-zA-Z0-9_\-\.]+\.pid", pid_file.split(" ")[0]):
    # 차단
```

---

### 2-2. /root/aads/aads-server/app/api/ops.py (수정)

기존 1220줄 → 1392줄 (172줄 추가). 기존 엔드포인트 무변경.

**추가된 3개 엔드포인트:**

```python
# (1) GET /api/v1/ops/claude-processes
@router.get("/ops/claude-processes")
async def get_claude_processes(limit: int = Query(5, le=20)):
    """최근 watchdog JSON 보고서 조회 (기본 5건, 최대 20건)."""
    # /root/aads/logs/watchdog_reports/*.json glob → JSON 파싱 → 요약 반환

# (2) POST /api/v1/ops/claude-cleanup
@router.post("/ops/claude-cleanup")
async def claude_cleanup(req: ClaudeCleanupRequest):
    """수동 claude_watchdog.py 정리 트리거. dry_run=True시 최신 보고서만 반환."""
    # python3 /root/aads/scripts/claude_watchdog.py 실행
    # env_file에서 TELEGRAM_BOT_TOKEN 등 환경변수 주입

# (3) POST /api/v1/ops/bridge-restart
@router.post("/ops/bridge-restart")
async def bridge_restart(req: BridgeRestartRequest):
    """bridge.py 원격 재시작 (서버 211 SSH) + 생존 확인."""
    # SSH nohup python3 .../bridge.py ... &
    # 2초 후 pgrep -f bridge.py로 확인
```

**백업**: `/root/aads/aads-server/app/api/ops.py.bak_AADS168`

---

### 2-3. systemd 파일 (스테이징)

**/root/aads/scripts/systemd/claude-watchdog.service:**
```ini
[Unit]
Description=AADS-168 Claude Bot Process Watchdog (oneshot)
After=network.target

[Service]
Type=oneshot
User=root
WorkingDirectory=/root/aads
EnvironmentFile=/root/aads/aads-server/.env
Environment=WATCHDOG_DB_HOST=localhost
Environment=WATCHDOG_DB_PORT=5433
Environment=WATCHDOG_DB_NAME=aads
Environment=WATCHDOG_DB_USER=aads
Environment=WATCHDOG_DB_PASS=aads_dev_local
Environment=SERVER_211_HOST=211.188.51.113
Environment=SERVER_114_HOST=116.120.58.155
Environment=SSH_KEY_PATH=/root/.ssh/id_ed25519_newtalk
ExecStart=/usr/bin/python3 /root/aads/scripts/claude_watchdog.py
TimeoutSec=60
StandardOutput=journal
StandardError=journal
SyslogIdentifier=claude-watchdog

[Install]
WantedBy=multi-user.target
```

**/root/aads/scripts/systemd/claude-watchdog.timer:**
```ini
[Unit]
Description=AADS-168 Claude Bot Process Watchdog Timer (2분 주기)
Requires=claude-watchdog.service

[Timer]
OnBootSec=30
OnUnitActiveSec=120
Unit=claude-watchdog.service

[Install]
WantedBy=timers.target
```

**설치 명령 (root):**
```bash
sudo bash /root/aads/scripts/install_claude_watchdog.sh
# 또는 직접:
sudo cp /root/aads/scripts/systemd/claude-watchdog.service /etc/systemd/system/
sudo cp /root/aads/scripts/systemd/claude-watchdog.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now claude-watchdog.timer
```

---

## 3. 테스트 실행 결과

### 실행 1 (Python 3.6 오류 수정 전)
```
TypeError: 'type' object is not subscriptable
```
원인: Python 3.6.8 — list[dict] 등 PEP 585 미지원

### 실행 2 (수정 후 — 최종 성공)
```
2026-03-08 09:10:11,058 [CLAUDE-WATCHDOG] INFO === Claude Watchdog 시작 (2026-03-08T09:10:11.058257+09:00) ===
2026-03-08 09:10:12,597 [CLAUDE-WATCHDOG] INFO 스캔 완료 — 68:True 211:False 114:False
2026-03-08 09:10:12,598 [CLAUDE-WATCHDOG] INFO 이슈 집계 — CRITICAL:0 HIGH:5
2026-03-08 09:10:12,598 [CLAUDE-WATCHDOG] WARNING [HIGH] session_watchdog_overtime 서버 68 — 보고만
2026-03-08 09:10:12,598 [CLAUDE-WATCHDOG] WARNING [HIGH] session_watchdog_overtime 서버 68 — 보고만
2026-03-08 09:10:12,598 [CLAUDE-WATCHDOG] WARNING [HIGH] session_watchdog_overtime 서버 68 — 보고만
2026-03-08 09:10:12,598 [CLAUDE-WATCHDOG] WARNING [HIGH] ssh_unreachable 서버 211 — 보고만
2026-03-08 09:10:12,598 [CLAUDE-WATCHDOG] WARNING [HIGH] ssh_unreachable 서버 114 — 보고만
2026-03-08 09:10:12,602 [CLAUDE-WATCHDOG] INFO 보고서 저장: /root/aads/logs/watchdog_reports/20260308_091012.json
2026-03-08 09:10:12,757 [CLAUDE-WATCHDOG] INFO === Claude Watchdog 완료 — 경과:1540ms CRITICAL:0 HIGH:5 CLEANUP:5 ===
{
  "total_issues": 5,
  "critical": 0,
  "high": 5,
  "cleanup_actions": 5,
  "elapsed_ms": 1540
}
```

**서버 68 로컬 스캔 결과:**
- claude_exec: 9개 (현재 실행 중인 태스크들)
- claude headless (-p): 9개
- session_watchdog: 3개 (overtime HIGH 감지, 3600초 초과 → 보고)
- zombies: 0개
- DB running 슬롯: 7개

**서버 211/114:** SSH 미연결 (claudebot 공개키 미등록) → ssh_unreachable HIGH (예상된 동작)

**JSON 보고서:** `/root/aads/logs/watchdog_reports/20260308_091012.json` 생성 확인

### ops.py 문법 검증
```
python3 -c "import ast; ast.parse(...)" → syntax OK
wc -l: 1392줄 (기존 1220 + 172 추가)
```

---

## 4. git 커밋 정보

| 리포 | 커밋 SHA | 메시지 |
|------|----------|--------|
| aads-server | afed71b | [AADS] feat: AADS-168 멀티서버 클로드봇 감시 데몬 API 엔드포인트 |
| aads-docs | dfb1254 | [AADS] feat: AADS-168 멀티서버 클로드봇 감시 데몬 |

### HTTP 200 확인
```
curl -s -o /dev/null -w "%{http_code}" https://raw.githubusercontent.com/moongoby-GO100/aads-docs/main/reports/AADS-168-RESULT.md
→ 200
```

**보고서 URL**: https://github.com/moongoby-GO100/aads-docs/blob/main/reports/AADS-168-RESULT.md

---

## 5. HANDOVER.md v11.2 업데이트 내용

```diff
+ # AADS HANDOVER v11.2
+ ## AADS-168 멀티서버 클로드봇 프로세스 감시 데몬 (2026-03-08)
+ | v11.2 | 2026-03-08 | AADS-168 | 멀티서버 클로드봇 감시 데몬: ...
```

---

## 6. STATUS.md 업데이트

```yaml
last_completed: AADS-168
completed_at: "2026-03-08T09:20:00+09:00"
result: SUCCESS
commit_sha: afed71b
report_url: https://github.com/moongoby-GO100/aads-docs/blob/main/reports/AADS-168-RESULT.md
```

---

## 7. 교훈

- **L-011**: Python 3.6 호환성 — `list[dict]`, `tuple[int,str]` (PEP 585, 3.9+), `capture_output=True` (3.7+) 는 Python 3.6에서 동작 불가. 기존 `watchdog_daemon.py` 스타일(subprocess.PIPE, no type hints)로 작성 필요.
- **L-012**: systemd 파일 설치 — claudebot은 `/etc/systemd/system/` 쓰기 불가 (755 root:root). 파일 스테이징(/root/aads/scripts/systemd/) + 설치 헬퍼 스크립트 패턴으로 대응.
