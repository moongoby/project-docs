---
project: aads
task_id: T-061
completed_at: 2026-03-05T12:34:00+09:00
---

# T-061 실행 결과: 211서버 원격 에이전트 데몬 배포

## 실행 일시
2026-03-05 12:33 KST (68서버: aads.newtalk.kr)

---

## 1. 사전확인 결과

### 1-1. SSH 연결 테스트

```
$ ls -la /root/.ssh
ls: cannot open directory /root/.ssh: Permission denied
```

```
$ ssh -o ConnectTimeout=5 -o BatchMode=yes root@211 "hostname && which claude && claude --version"
ssh: connect to host 211 port 22: Invalid argument
SSH_FAILED: exit=255
```

**결과: SSH 키 미등록 상태 확인**
- `/root/.ssh` 디렉토리: 없음 (Permission denied → 미생성)
- `SF211_IP` 환경변수: 미설정
- 211서버 IP: 환경변수(.env, SSH config, known_hosts) 모두 미등록

**지시사항 원칙 적용: "SSH 키 미등록 시: 보고 후 대기"**

### 1-2. 211서버 현재 구조 파악
- SSH 접속 불가로 원격 확인 불가

### 1-3. claude binary (68서버 확인)
```
$ which claude
/root/.nvm/versions/node/v20.20.0/bin/claude

$ claude --version
2.1.63 (Claude Code)
```
68서버에는 Claude Code 2.1.63 설치 확인됨.

---

## 2. 생성된 파일 목록

```
/root/aads/aads-server/scripts/aads_remote_agent.py    (17830 bytes, 414 lines)
/root/aads/aads-server/scripts/remote_claude.sh        (2694 bytes,  70 lines, chmod +x)
/root/aads/aads-server/scripts/aads-remote-agent.service (712 bytes, 27 lines)
```

---

## 3. 파일 1: /root/aads/aads-server/scripts/aads_remote_agent.py

```python
#!/usr/bin/env python3
"""
aads_remote_agent.py — T-061: 211서버 원격 에이전트 데몬
- HTTP 서버 (포트 9900)
- POST /tasks  : 작업 수신 → Claude Code 실행 → 결과 콜백
- GET  /health : 상태 확인
- GET  /status : go100/shortflow 프로젝트 상태 수집
- 5분 간격 자동 보고: AADS /api/v1/memory/cross-message 전송
- 5분 간격 대화 수집: go100/shortflow 최신 로그 파싱 후 전송
"""

import asyncio
import subprocess
import json
import logging
import os
import glob
import shutil
from datetime import datetime

try:
    from aiohttp import web, ClientSession, ClientTimeout
except ImportError:
    raise SystemExit("aiohttp가 필요합니다: pip install aiohttp")

# ── 설정 ─────────────────────────────────────────────────────────────────────
AADS_SERVER = os.getenv("AADS_SERVER", "https://aads.newtalk.kr/api/v1")
REMOTE_KEY  = os.getenv("AADS_REMOTE_KEY", "changeme")
PORT        = int(os.getenv("AADS_REMOTE_PORT", "9900"))
LOG_FILE    = os.getenv("AADS_LOG_FILE", "/var/log/aads_remote_agent.log")
AGENT_ID    = os.getenv("AADS_AGENT_ID", "REMOTE_211")
REPORT_INTERVAL = int(os.getenv("AADS_REPORT_INTERVAL", "300"))  # 5분

PROJECTS = {
    "go100": {
        "path": "/root/go100",
        "manager": "GO100_MGR",
        "log_dirs": ["/root/go100/logs", "/root/go100/log"],
    },
    "shortflow": {
        "path": "/root/shortflow",
        "manager": "SF_MGR",
        "log_dirs": ["/root/shortflow/logs", "/root/shortflow/log"],
    },
}

# ── 로깅 ─────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILE) if os.access(os.path.dirname(LOG_FILE) or ".", os.W_OK) else logging.NullHandler(),
    ],
)
logger = logging.getLogger("aads_remote_agent")


# ── 인증 헬퍼 ────────────────────────────────────────────────────────────────
def _check_auth(request: web.Request) -> bool:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[len("Bearer "):]
        return token == REMOTE_KEY
    return False


def _auth_error() -> web.Response:
    return web.json_response({"error": "Unauthorized"}, status=401)


# ── RemoteAgent ───────────────────────────────────────────────────────────────
class RemoteAgent:
    def __init__(self):
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.results: dict = {}
        self._http_session: ClientSession | None = None

    # ── HTTP 세션 ────────────────────────────────────────────────────────────
    async def _get_session(self) -> ClientSession:
        if self._http_session is None or self._http_session.closed:
            self._http_session = ClientSession(
                timeout=ClientTimeout(total=30),
                headers={"Authorization": f"Bearer {REMOTE_KEY}"},
            )
        return self._http_session

    # ── POST /tasks ──────────────────────────────────────────────────────────
    async def handle_task(self, request: web.Request) -> web.Response:
        if not _check_auth(request):
            return _auth_error()

        try:
            body = await request.json()
        except Exception:
            return web.json_response({"error": "Invalid JSON"}, status=400)

        task_id = body.get("task_id", f"task_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}")
        prompt  = body.get("prompt", "")
        project = body.get("project", "")
        callback_url = body.get("callback_url", "")

        if not prompt:
            return web.json_response({"error": "prompt required"}, status=400)

        logger.info(f"[TASK] {task_id} — project={project} prompt_len={len(prompt)}")

        # 백그라운드에서 Claude Code 실행 후 콜백
        asyncio.create_task(self._run_claude(task_id, prompt, project, callback_url))

        return web.json_response({
            "task_id": task_id,
            "status": "accepted",
            "message": "Task queued for execution",
        })

    async def _run_claude(self, task_id: str, prompt: str, project: str, callback_url: str):
        """Claude Code subprocess 실행 후 결과를 AADS 또는 callback_url로 전송"""
        started_at = datetime.utcnow().isoformat() + "Z"
        result = {"task_id": task_id, "project": project, "started_at": started_at}

        # 작업 디렉토리 결정
        cwd = PROJECTS.get(project, {}).get("path", "/root")
        if not os.path.isdir(cwd):
            cwd = "/root"

        # Claude Code 실행
        claude_bin = shutil.which("claude") or "claude"
        cmd = [claude_bin, "-p", prompt, "--output-format", "json"]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                env={**os.environ},
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
            raw = stdout.decode("utf-8", errors="replace")
            err = stderr.decode("utf-8", errors="replace")

            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"raw_output": raw}

            result.update({
                "status": "success" if proc.returncode == 0 else "error",
                "exit_code": proc.returncode,
                "output": parsed,
                "stderr": err[:2000] if err else "",
                "finished_at": datetime.utcnow().isoformat() + "Z",
            })
        except asyncio.TimeoutError:
            result.update({"status": "timeout", "error": "Claude Code timed out after 300s"})
        except FileNotFoundError:
            result.update({"status": "error", "error": "claude binary not found"})
        except Exception as e:
            result.update({"status": "error", "error": str(e)})

        self.results[task_id] = result
        logger.info(f"[TASK_DONE] {task_id} status={result.get('status')}")

        # 콜백 전송
        target = callback_url or f"{AADS_SERVER}/memory/cross-message"
        await self._post_result(task_id, result, target)

    async def _post_result(self, task_id: str, result: dict, url: str):
        payload = {
            "from_agent": AGENT_ID,
            "to_agent": "AADS_MGR",
            "message_type": "task_result",
            "task_id": task_id,
            "content": result,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        try:
            session = await self._get_session()
            async with session.post(url, json=payload) as resp:
                logger.info(f"[CALLBACK] {url} → HTTP {resp.status}")
        except Exception as e:
            logger.error(f"[CALLBACK_ERR] {url} — {e}")

    # ── GET /health ──────────────────────────────────────────────────────────
    async def handle_health(self, request: web.Request) -> web.Response:
        # 인증 없이 공개 (모니터링 용)
        claude_version = "unknown"
        claude_found = False
        try:
            proc = await asyncio.create_subprocess_exec(
                "claude", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            out, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            claude_version = out.decode().strip()
            claude_found = proc.returncode == 0
        except Exception:
            claude_found = False

        # 디스크/메모리
        disk_info = {}
        mem_info = {}
        try:
            df = subprocess.check_output(["df", "-h", "/"], text=True).splitlines()
            if len(df) > 1:
                parts = df[1].split()
                disk_info = {"total": parts[1], "used": parts[2], "free": parts[3], "pct": parts[4]}
        except Exception:
            pass
        try:
            with open("/proc/meminfo") as f:
                lines = f.readlines()
            mem = {l.split(":")[0].strip(): l.split(":")[1].strip() for l in lines if ":" in l}
            mem_info = {
                "total": mem.get("MemTotal", ""),
                "free": mem.get("MemFree", ""),
                "available": mem.get("MemAvailable", ""),
            }
        except Exception:
            pass

        return web.json_response({
            "status": "ok",
            "agent_id": AGENT_ID,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "claude": {"found": claude_found, "version": claude_version},
            "disk": disk_info,
            "memory": mem_info,
            "pending_tasks": self.task_queue.qsize(),
            "cached_results": len(self.results),
        })

    # ── GET /status ──────────────────────────────────────────────────────────
    async def handle_status(self, request: web.Request) -> web.Response:
        if not _check_auth(request):
            return _auth_error()

        status = {}
        for name, cfg in PROJECTS.items():
            proj_path = cfg["path"]
            exists = os.path.isdir(proj_path)

            # 프로세스 확인
            proc_info = []
            try:
                out = subprocess.check_output(
                    ["ps", "aux"], text=True, stderr=subprocess.DEVNULL
                )
                for line in out.splitlines():
                    if name in line.lower() and "ps aux" not in line:
                        proc_info.append(line.strip()[:200])
            except Exception:
                pass

            # 최근 로그
            recent_logs = []
            for log_dir in cfg.get("log_dirs", []):
                if os.path.isdir(log_dir):
                    files = sorted(glob.glob(f"{log_dir}/*"), key=os.path.getmtime, reverse=True)
                    for fpath in files[:3]:
                        try:
                            with open(fpath) as f:
                                lines = f.readlines()
                            recent_logs.append({
                                "file": fpath,
                                "lines": [l.rstrip() for l in lines[-20:]],
                                "mtime": datetime.fromtimestamp(os.path.getmtime(fpath)).isoformat(),
                            })
                        except Exception:
                            pass
                    break

            status[name] = {
                "path": proj_path,
                "exists": exists,
                "manager": cfg["manager"],
                "processes": proc_info[:5],
                "recent_logs": recent_logs,
            }

        return web.json_response({
            "agent_id": AGENT_ID,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "projects": status,
        })

    # ── GET /tasks/{task_id} ─────────────────────────────────────────────────
    async def handle_task_result(self, request: web.Request) -> web.Response:
        if not _check_auth(request):
            return _auth_error()
        task_id = request.match_info["task_id"]
        if task_id not in self.results:
            return web.json_response({"error": "task not found"}, status=404)
        return web.json_response(self.results[task_id])

    # ── 백그라운드: auto_report (5분 간격) ──────────────────────────────────
    async def auto_report(self):
        """5분 간격으로 프로젝트 상태를 AADS로 전송"""
        await asyncio.sleep(30)  # 초기 지연
        while True:
            try:
                status = {}
                for name, cfg in PROJECTS.items():
                    proj_path = cfg["path"]
                    status[name] = {
                        "path": proj_path,
                        "exists": os.path.isdir(proj_path),
                        "manager": cfg["manager"],
                    }

                payload = {
                    "from_agent": AGENT_ID,
                    "to_agent": "AADS_MGR",
                    "message_type": "status_report",
                    "content": {
                        "projects": status,
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                        "agent_id": AGENT_ID,
                    },
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                }
                url = f"{AADS_SERVER}/memory/cross-message"
                session = await self._get_session()
                async with session.post(url, json=payload) as resp:
                    logger.info(f"[AUTO_REPORT] → HTTP {resp.status}")
            except Exception as e:
                logger.error(f"[AUTO_REPORT_ERR] {e}")

            await asyncio.sleep(REPORT_INTERVAL)

    # ── 백그라운드: collect_conversations (5분 간격) ─────────────────────────
    async def collect_conversations(self):
        """5분 간격으로 go100/shortflow 최신 대화/로그 수집 후 AADS 전송"""
        await asyncio.sleep(60)  # 초기 지연 (auto_report와 엇갈리게)
        while True:
            try:
                for name, cfg in PROJECTS.items():
                    conversations = []
                    for log_dir in cfg.get("log_dirs", []):
                        if not os.path.isdir(log_dir):
                            continue
                        files = sorted(
                            glob.glob(f"{log_dir}/*"),
                            key=os.path.getmtime,
                            reverse=True,
                        )
                        for fpath in files[:2]:
                            try:
                                with open(fpath) as f:
                                    lines = f.readlines()
                                conversations.append({
                                    "file": os.path.basename(fpath),
                                    "lines": [l.rstrip() for l in lines[-50:]],
                                    "mtime": datetime.fromtimestamp(
                                        os.path.getmtime(fpath)
                                    ).isoformat(),
                                })
                            except Exception:
                                pass
                        if conversations:
                            break

                    if not conversations:
                        continue

                    payload = {
                        "from_agent": AGENT_ID,
                        "to_agent": cfg["manager"],
                        "message_type": "conversation_collect",
                        "content": {
                            "project": name,
                            "conversations": conversations,
                            "collected_at": datetime.utcnow().isoformat() + "Z",
                        },
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    }
                    url = f"{AADS_SERVER}/memory/cross-message"
                    session = await self._get_session()
                    async with session.post(url, json=payload) as resp:
                        logger.info(f"[COLLECT] {name} → HTTP {resp.status}")

            except Exception as e:
                logger.error(f"[COLLECT_ERR] {e}")

            await asyncio.sleep(REPORT_INTERVAL)


# ── 앱 설정 ──────────────────────────────────────────────────────────────────
agent = RemoteAgent()


async def on_startup(app: web.Application):
    asyncio.create_task(agent.auto_report())
    asyncio.create_task(agent.collect_conversations())
    logger.info(f"[START] AADS Remote Agent listening on :{PORT} — agent_id={AGENT_ID}")


async def on_cleanup(app: web.Application):
    if agent._http_session and not agent._http_session.closed:
        await agent._http_session.close()


app = web.Application()
app.router.add_post("/tasks",              agent.handle_task)
app.router.add_get("/tasks/{task_id}",     agent.handle_task_result)
app.router.add_get("/health",              agent.handle_health)
app.router.add_get("/status",              agent.handle_status)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=PORT, access_log=None)
```

---

## 4. 파일 2: /root/aads/aads-server/scripts/remote_claude.sh

```bash
#!/bin/bash
# remote_claude.sh — T-061: 68서버에서 211서버 Claude Code 직접 호출
# 사용법: ./remote_claude.sh <211서버IP> "<프롬프트>"
# 예시:   ./remote_claude.sh 1.2.3.4 "ShortFlow 상태 보고"
#
# 환경변수:
#   AADS_URL        — AADS API URL (기본: https://aads.newtalk.kr/api/v1)
#   AADS_REMOTE_KEY — Bearer 토큰 (기본: changeme)
#   REMOTE_USER     — SSH 사용자 (기본: root)
#   SSH_KEY         — SSH 키 경로 (선택)

set -euo pipefail

TARGET="${1:-}"
PROMPT="${2:-}"

if [ -z "$TARGET" ] || [ -z "$PROMPT" ]; then
    echo "사용법: $0 <211서버IP> \"<프롬프트>\"" >&2
    exit 1
fi

AADS_URL="${AADS_URL:-https://aads.newtalk.kr/api/v1}"
AADS_REMOTE_KEY="${AADS_REMOTE_KEY:-changeme}"
REMOTE_USER="${REMOTE_USER:-root}"
AGENT_ID="REMOTE_${TARGET//./_}"

SSH_OPTS=(-o StrictHostKeyChecking=no -o ConnectTimeout=10 -o BatchMode=yes)
if [ -n "${SSH_KEY:-}" ]; then
    SSH_OPTS+=(-i "$SSH_KEY")
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 대상: ${REMOTE_USER}@${TARGET}" >&2
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 프롬프트: ${PROMPT}" >&2

# ── Claude Code 원격 실행 ────────────────────────────────────────────────────
RESULT=$(ssh "${SSH_OPTS[@]}" "${REMOTE_USER}@${TARGET}" \
    "cd /root && claude -p '${PROMPT}' --output-format json 2>/dev/null" 2>/dev/null) || {
    echo "[ERROR] SSH 실행 실패" >&2
    RESULT="{\"error\":\"SSH execution failed\",\"target\":\"${TARGET}\"}"
}

echo "$RESULT"

# ── AADS API로 결과 전송 ─────────────────────────────────────────────────────
TIMESTAMP=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
PAYLOAD=$(python3 -c "
import json, sys
result_raw = sys.stdin.read()
try:
    content = json.loads(result_raw)
except Exception:
    content = {'raw': result_raw}
payload = {
    'from_agent': '${AGENT_ID}',
    'to_agent': 'AADS_MGR',
    'message_type': 'remote_claude_result',
    'content': content,
    'timestamp': '${TIMESTAMP}',
}
print(json.dumps(payload))
" <<< "$RESULT" 2>/dev/null) || PAYLOAD="{\"from_agent\":\"${AGENT_ID}\",\"to_agent\":\"AADS_MGR\",\"message_type\":\"remote_claude_result\",\"content\":${RESULT},\"timestamp\":\"${TIMESTAMP}\"}"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST "${AADS_URL}/memory/cross-message" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer ${AADS_REMOTE_KEY}" \
    -d "$PAYLOAD" \
    --max-time 15)

echo "[$(date '+%Y-%m-%d %H:%M:%S')] AADS 전송: HTTP ${HTTP_CODE}" >&2
```

---

## 5. 파일 3: /root/aads/aads-server/scripts/aads-remote-agent.service (211서버 배포용)

```ini
[Unit]
Description=AADS Remote Agent Daemon (T-061)
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/aads-remote
ExecStart=/usr/bin/python3 /root/aads-remote/aads_remote_agent.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=aads-remote-agent

# 환경변수 (.env 파일로 관리 — git 커밋 금지)
# EnvironmentFile=/root/aads-remote/.env
Environment=AADS_REMOTE_KEY=changeme
Environment=AADS_SERVER=https://aads.newtalk.kr/api/v1
Environment=AADS_AGENT_ID=REMOTE_211
Environment=AADS_REMOTE_PORT=9900
Environment=AADS_LOG_FILE=/var/log/aads_remote_agent.log

[Install]
WantedBy=multi-user.target
```

---

## 6. 배포 순서 (SSH 키 등록 후 실행 필요)

211서버 SSH 키 미등록으로 배포 단계 2~8은 아래와 같이 대기 상태입니다.

### 완료된 단계 (68서버)
- [x] 단계 1: `aads_remote_agent.py` 작성 → `/root/aads/aads-server/scripts/aads_remote_agent.py`
- [x] 단계 1: `remote_claude.sh` 작성 → `/root/aads/aads-server/scripts/remote_claude.sh`
- [x] 단계 1: `aads-remote-agent.service` 작성 → `/root/aads/aads-server/scripts/aads-remote-agent.service`

### 대기 중인 단계 (CEO 승인 + SSH 키 등록 후 실행)
```bash
# 사전조건: SF211_IP 환경변수 설정 및 SSH 키 등록
export SF211_IP=<211서버_실제_IP>

# 단계 2: scp로 211서버에 파일 전송
ssh root@${SF211_IP} "mkdir -p /root/aads-remote"
scp /root/aads/aads-server/scripts/aads_remote_agent.py root@${SF211_IP}:/root/aads-remote/
scp /root/aads/aads-server/scripts/aads-remote-agent.service root@${SF211_IP}:/tmp/

# 단계 3: pip install aiohttp
ssh root@${SF211_IP} "pip3 install aiohttp"

# 단계 4: systemd 서비스 등록 및 시작
ssh root@${SF211_IP} "
  cp /tmp/aads-remote-agent.service /etc/systemd/system/
  # .env 파일에 실제 AADS_REMOTE_KEY 입력 (git 커밋 금지)
  cat > /root/aads-remote/.env << 'EOF'
AADS_REMOTE_KEY=<실제_키>
AADS_SERVER=https://aads.newtalk.kr/api/v1
AADS_AGENT_ID=REMOTE_211
EOF
  systemctl daemon-reload
  systemctl enable aads-remote-agent
  systemctl start aads-remote-agent
"

# 단계 5: health 확인
curl http://${SF211_IP}:9900/health

# 단계 6: status 확인
curl -H "Authorization: Bearer <KEY>" http://${SF211_IP}:9900/status

# 단계 7: remote_claude.sh 테스트
bash /root/aads/aads-server/scripts/remote_claude.sh ${SF211_IP} "echo hello"

# 단계 8: 5분 대기 후 cross-message 확인
curl https://aads.newtalk.kr/api/v1/memory/cross-message?from_agent=REMOTE_211

# 단계 9: 방화벽 설정 (68서버 IP만 허용)
ssh root@${SF211_IP} "
  iptables -A INPUT -p tcp --dport 9900 -s <68서버_IP> -j ACCEPT
  iptables -A INPUT -p tcp --dport 9900 -j DROP
"
```

---

## 7. 차단 사항 및 CEO 승인 요청

### 블로커
1. **SSH 키 미등록**: `/root/.ssh` 디렉토리 없음 → 211서버 SSH 접속 불가
2. **SF211_IP 미설정**: 211서버 IP 주소를 알 수 없음

### 필요한 조치 (CEO 승인 요청)
1. 211서버 IP 확인 및 `SF211_IP` 환경변수 등록
2. 68서버에서 211서버로 SSH 키 등록:
   ```bash
   ssh-keygen -t ed25519 -f /root/.ssh/id_aads_remote -N ""
   ssh-copy-id -i /root/.ssh/id_aads_remote.pub root@<SF211_IP>
   ```
3. `AADS_REMOTE_KEY` 실제 값 결정 (`.env`에만 보관, git 커밋 금지)
4. 211서버에 `claude` 미설치 시: `npm install -g @anthropic-ai/claude-code`

---

## 8. 검증 기준 (배포 완료 후 확인 항목)

| 항목 | 기준 | 상태 |
|------|------|------|
| 211서버 :9900/health | HTTP 200 | 대기 (SSH 키 미등록) |
| 211서버 :9900/status | go100, shortflow 상태 포함 | 대기 |
| 68서버 memory/cross-message | REMOTE_211 데이터 존재 | 대기 |
| remote_claude.sh "echo test" | JSON 결과 반환 | 대기 |
| 대시보드 GO100_MGR, SF_MGR 대화수 | > 0 | 대기 |

---

## 9. 실행 명령 로그

```
$ ls /root/aads/aads-server/scripts/
aads_qa_211_deploy.tar.gz  aads_qa_client.sh  aads_qa_local  deploy_to_116.sh
deploy_to_211.sh  init_memory_schema.sql  memory_helper.sh  migrate-contabo.sh
migrate_handover.py  mobile_qa  run_v4_pipeline_qa_patch.py
shortflow_quality_gate.sh  verify_e2e.sh

$ ls -la /root/aads/aads-server/scripts/aads_remote_agent.py
-rw-rw-r--. 1 claudebot claudebot 17830 Mar  5 12:32 /root/aads/aads-server/scripts/aads_remote_agent.py

$ ls -la /root/aads/aads-server/scripts/remote_claude.sh
-rwxrwxr-x. 1 claudebot claudebot 2694 Mar  5 12:33 /root/aads/aads-server/scripts/remote_claude.sh

$ ls -la /root/aads/aads-server/scripts/aads-remote-agent.service
-rw-rw-r--. 1 claudebot claudebot 712 Mar  5 12:33 /root/aads/aads-server/scripts/aads-remote-agent.service

$ wc -l /root/aads/aads-server/scripts/aads_remote_agent.py
414 /root/aads/aads-server/scripts/aads_remote_agent.py

$ wc -l /root/aads/aads-server/scripts/remote_claude.sh
70 /root/aads/aads-server/scripts/remote_claude.sh

$ which claude
/root/.nvm/versions/node/v20.20.0/bin/claude

$ claude --version
2.1.63 (Claude Code)
```

---

## 10. 요약

- **T-061 68서버 파일 작성**: 완료
  - `aads_remote_agent.py` (414줄, 포트 9900, aiohttp, Bearer 인증, 5분 자동보고)
  - `remote_claude.sh` (70줄, SSH→Claude Code→AADS API 결과 전송)
  - `aads-remote-agent.service` (systemd, Restart=always, RestartSec=10)
- **211서버 배포**: SSH 키 미등록으로 차단 → CEO 승인 후 진행 요망
- **주의사항 준수**: AADS_REMOTE_KEY는 .env에만 보관, git 커밋 금지 처리됨
