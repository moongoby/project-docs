"""
Genspark Bridge V1 — KIS-V41 대화창 자동 폴링 및 지시 실행 데몬
- 60초 간격 폴링, [DIRECTIVE_START]~[DIRECTIVE_END] 또는 >>>DIRECTIVE_START~>>>DIRECTIVE_END 블록 감지 시 실행
- /tmp/genspark_bridge.lock PID lockfile로 중복 실행 방지
- /root/.genspark/logs/bridge.log 일자별 로테이션 로깅
- playwright-stealth 적용으로 Cloudflare 봇 차단 우회
- --test-once 플래그: 1회 폴링 후 종료 (통합 테스트용)
- 30분 정기 통합 현황 보고 (6개 프로젝트 전체) → 텔레그램 + CEO 지휘소
"""
import argparse
import asyncio
import datetime
import json
import logging
import os
import re
import subprocess
import sys
import urllib.request
import urllib.parse
import zoneinfo
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

# -------------------------------------------------------------------
# 경로 상수
# -------------------------------------------------------------------
BASE_DIR = Path("/root/.genspark")
LOG_DIR = BASE_DIR / "logs"
SESSION_PATH = BASE_DIR / "session.json"
LOCK_FILE = Path("/tmp/genspark_bridge.lock")
PENDING_DIR = BASE_DIR / "pending"
RUNNING_DIR = BASE_DIR / "running"
DONE_DIR = BASE_DIR / "done"

GITHUB_REPO = "moongoby/project-docs"
KST = zoneinfo.ZoneInfo("Asia/Seoul")
PERIODIC_REPORT_INTERVAL_SEC = 1800  # 30분 간격 정기 보고
IDLE_WAIT_SEC = 120  # 2분 대기 후 지시 요청 메시지 전송


def _load_project_config() -> dict:
    """PROJECTS 설정 — .env에서 채팅 URL 및 SSH 명령 로드"""
    env_path = BASE_DIR / ".env"
    env_vars: dict = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env_vars[k.strip()] = v.strip()

    def _get(key: str, default: str = "") -> str:
        return env_vars.get(key, default)

    return {
        "KIS": {
            "chat_url": _get("GENSPARK_CHAT_KIS",
                             "https://www.genspark.ai/agents?id=77de652f-ca8c-4edb-b841-4ca3726b7bb4"),
            "services": ["kis-v41-api", "kis-v41-monitor", "kis-v41-scheduler"],
            "tag": "KIS",
            "whitelist": ["security_scan", "path_check", "sync_kis", "Protocol D", "프로토콜 D"],
            "cursor_prefix": "[CURSOR-KIS]",
            "ssh": _get("SSH_CMD_KIS"),
        },
        "GO100": {
            "chat_url": _get("GENSPARK_CHAT_GO100"),
            "services": ["go100"],
            "tag": "GO100",
            "whitelist": ["security_scan", "path_check", "sync_go100", "Protocol D", "프로토콜 D"],
            "cursor_prefix": "[CURSOR-GO100]",
            "ssh": _get("SSH_CMD_GO100"),
        },
        "AADS": {
            "chat_url": _get("GENSPARK_CHAT_AADS"),
            "services": [],
            "tag": "AADS",
            "whitelist": ["security_scan", "path_check", "Protocol D", "프로토콜 D"],
            "cursor_prefix": "[CURSOR-AADS]",
            "ssh": _get("SSH_CMD_AADS"),
        },
        "SF": {
            "chat_url": _get("GENSPARK_CHAT_SF"),
            "services": [],
            "tag": "SF",
            "whitelist": ["security_scan", "path_check", "Protocol D", "프로토콜 D"],
            "cursor_prefix": "[CURSOR-SF]",
            "ssh": _get("SSH_CMD_SF"),
        },
        "NAS": {
            "chat_url": _get("GENSPARK_CHAT_NAS"),
            "services": [],
            "tag": "NAS",
            "whitelist": ["security_scan", "path_check", "Protocol D", "프로토콜 D"],
            "cursor_prefix": "[CURSOR-NAS]",
            "ssh": _get("SSH_CMD_NAS"),
        },
        "NTV2": {
            "chat_url": _get("GENSPARK_CHAT_NTV2"),
            "services": [],
            "tag": "NTV2",
            "whitelist": ["security_scan", "path_check", "Protocol D", "프로토콜 D"],
            "cursor_prefix": "[CURSOR-NTV2]",
            "ssh": _get("SSH_CMD_NTV2"),
        },
    }


PROJECTS = _load_project_config()

# 기본 URL (하위 호환성)
KIS_V41_CHAT_URL = PROJECTS["KIS"]["chat_url"]
CEO_CHAT_URL = "https://www.genspark.ai/agents?id=6d5b75b6-452d-452b-beef-eab368e3e6bf"

# -------------------------------------------------------------------
# 로거 설정
# -------------------------------------------------------------------
LOG_DIR.mkdir(parents=True, exist_ok=True)
PENDING_DIR.mkdir(parents=True, exist_ok=True)
RUNNING_DIR.mkdir(parents=True, exist_ok=True)
DONE_DIR.mkdir(parents=True, exist_ok=True)


def _kst_time(*args):
    """logging.Formatter.converter — %(asctime)s를 KST로 고정"""
    return datetime.datetime.now(KST).timetuple()


log_handler = TimedRotatingFileHandler(
    str(LOG_DIR / "bridge.log"),
    when="midnight",
    backupCount=30,
    encoding="utf-8",
)
_fmt = logging.Formatter("%(asctime)s KST [%(levelname)s] %(message)s")
_fmt.converter = _kst_time
log_handler.setFormatter(_fmt)

_stream_handler = logging.StreamHandler(sys.stdout)
_stream_fmt = logging.Formatter("%(asctime)s KST [%(levelname)s] %(message)s")
_stream_fmt.converter = _kst_time
_stream_handler.setFormatter(_stream_fmt)

logger = logging.getLogger("genspark_bridge")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(_stream_handler)


# -------------------------------------------------------------------
# PID lockfile 관리
# -------------------------------------------------------------------
def acquire_lock():
    if LOCK_FILE.exists():
        try:
            pid = int(LOCK_FILE.read_text().strip())
            # 프로세스 존재 확인
            os.kill(pid, 0)
            logger.error("이미 실행 중 (PID %d). 종료.", pid)
            sys.exit(1)
        except (ProcessLookupError, ValueError):
            pass
    LOCK_FILE.write_text(str(os.getpid()))


def release_lock():
    try:
        LOCK_FILE.unlink()
    except FileNotFoundError:
        pass


# -------------------------------------------------------------------
# 화이트리스트 판별
# -------------------------------------------------------------------
def is_whitelisted(directive_text: str, project: str = "KIS") -> bool:
    # FINAL_GO_CONFIRMED 지시는 모든 프로젝트에서 완료 확인으로 자동 통과 처리
    if "FINAL_GO_CONFIRMED" in directive_text or "ACTION: VIRTUAL_RUN_COMPLETE" in directive_text:
        return True
    keywords = PROJECTS.get(project, PROJECTS["KIS"])["whitelist"]
    return any(kw.lower() in directive_text.lower() for kw in keywords)


# -------------------------------------------------------------------
# 지시 블록 파싱
# -------------------------------------------------------------------
def parse_directive(text: str) -> str | None:
    """Directive 블록 추출 — 두 가지 구분자 형식 지원 (최소 20자 + 줄바꿈 필수 시만 유효)

    지원 형식:
      [DIRECTIVE_START] ... [DIRECTIVE_END]   ← 신규 기본 형식
      >>>DIRECTIVE_START ... >>>DIRECTIVE_END ← 구형 호환 형식
    가장 마지막 블록을 우선 처리 (최신 지시).
    """
    # 신규 [] 형식 우선 검색 후, 없으면 구형 >>> 형식 검색
    bracket_pattern = r"\[DIRECTIVE_START\](.*?)\[DIRECTIVE_END\]"
    arrow_pattern = r">>>DIRECTIVE_START(.*?)>>>DIRECTIVE_END"

    matches = re.findall(bracket_pattern, text, re.DOTALL)
    if not matches:
        matches = re.findall(arrow_pattern, text, re.DOTALL)
    if not matches:
        return None

    content = matches[-1].strip()
    # 너무 짧거나 단순 구분자("/", 공백)는 false positive로 필터링
    # 줄바꿈(\n) 없는 한 줄 텍스트는 시스템 프롬프트 예시 텍스트로 간주 → 무시
    if len(content) < 20 or "\n" not in content:
        return None
    return content


# -------------------------------------------------------------------
# Directive 영속화 (pending 폴더 저장)
# -------------------------------------------------------------------
def _save_directive_to_pending(project_tag: str, directive: str) -> Path | None:
    """감지된 Directive를 pending 폴더에 마크다운으로 저장 후 경로 반환"""
    try:
        PENDING_DIR.mkdir(parents=True, exist_ok=True)
        now_kst = datetime.datetime.now(KST)
        ts = now_kst.strftime("%Y%m%d_%H%M%S")
        fname = PENDING_DIR / f"{project_tag}_{ts}.md"
        content = (
            f"# Directive [{project_tag}] {now_kst.strftime('%Y-%m-%d %H:%M KST')}\n\n"
            f"```\n{directive}\n```\n"
        )
        fname.write_text(content, encoding="utf-8")
        logger.info("[%s] Directive → pending 저장: %s", project_tag, fname.name)
        return fname
    except Exception as e:
        logger.warning("[%s] pending 저장 실패: %s", project_tag, e)
        return None


# -------------------------------------------------------------------
# 허용된 지시 실행
# -------------------------------------------------------------------
def execute_whitelist_directive(directive: str) -> str:
    """화이트리스트 작업 실행 후 결과 요약 반환"""
    results = []

    if "security_scan" in directive.lower():
        try:
            r = subprocess.run(
                ["bash", "/root/project-docs/scripts/security_scan.sh"],
                capture_output=True, text=True, timeout=60,
                cwd="/root/project-docs"
            )
            line = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else "완료"
            results.append(f"security_scan: {line[:100]}")
        except Exception as e:
            results.append(f"security_scan 실패: {e}")

    if "path_check" in directive.lower():
        match = re.search(r"path_check\.sh\s+([\w\-\.]+\.md)", directive)
        filename = match.group(1) if match else ""
        try:
            cmd = ["bash", "/root/project-docs/scripts/path_check.sh"]
            if filename:
                cmd.append(filename)
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                               cwd="/root/project-docs")
            ok = "PASS" if r.returncode == 0 else "FAIL"
            results.append(f"path_check: {ok}")
        except Exception as e:
            results.append(f"path_check 실패: {e}")

    if "sync_kis" in directive.lower():
        try:
            r = subprocess.run(
                ["bash", "/root/project-docs/scripts/sync_kis.sh"],
                capture_output=True, text=True, timeout=120,
                cwd="/root/project-docs"
            )
            results.append(f"sync_kis: {'완료' if r.returncode == 0 else '실패'}")
        except Exception as e:
            results.append(f"sync_kis 실패: {e}")

    return "\n".join(results) if results else "whitelist 작업 실행 완료"


# -------------------------------------------------------------------
# 정기 현황 보고 헬퍼
# -------------------------------------------------------------------
def _get_latest_commit() -> str:
    """GitHub API로 project-docs 최신 커밋 SHA+시간 조회 (KST 표시)"""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/commits?per_page=1"
        req = urllib.request.Request(url, headers={"User-Agent": "genspark-bridge/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            sha = data[0]["sha"][:7]
            # GitHub API는 UTC ISO 8601 반환 → KST(+9) 변환
            utc_str = data[0]["commit"]["committer"]["date"]  # e.g. "2026-03-02T10:00:00Z"
            utc_dt = datetime.datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
            kst_dt = utc_dt.astimezone(zoneinfo.ZoneInfo("Asia/Seoul"))
            date_str = kst_dt.strftime("%Y-%m-%d %H:%M KST")
            return f"{sha} ({date_str})"
    except Exception:
        return "조회 실패"


def _get_service_status(service_name: str) -> str:
    """systemctl is-active 결과 반환"""
    try:
        r = subprocess.run(
            ["systemctl", "is-active", service_name],
            capture_output=True, text=True, timeout=5
        )
        return r.stdout.strip()
    except Exception:
        return "unknown"


def _count_pending_for_project(project_tag: str) -> int:
    """pending/ 폴더에서 특정 프로젝트의 파일 수 반환"""
    try:
        return len(list(PENDING_DIR.glob(f"{project_tag}_*.md")))
    except Exception:
        return 0


def build_unified_status_report() -> str:
    """6개 프로젝트 전체 상태 30분 정기 보고 (KST 기준)"""
    now_kst = datetime.datetime.now(KST).strftime("%Y-%m-%d %H:%M KST")
    commit = _get_latest_commit()
    lines = [f"[통합현황] {now_kst}"]

    for proj_key, proj_cfg in PROJECTS.items():
        tag = proj_cfg["tag"]
        services = proj_cfg.get("services", [])
        pending_n = _count_pending_for_project(tag)
        pending_str = f"pending: {pending_n}건"

        if services:
            svc_status = " ".join(
                f"{s}:{_get_service_status(s)}" for s in services
            )
            lines.append(f"{tag}: {svc_status} | 최근커밋: {commit} | {pending_str}")
        else:
            lines.append(f"{tag}: 최근커밋: {commit} | {pending_str}")

    # 전체 running/done 현황
    try:
        running_n = len(list(RUNNING_DIR.glob("*.md")))
        done_n = len(list(DONE_DIR.glob("*.md")))
        lines.append(f"running: {running_n}건 | done(미처리): {done_n}건")
    except Exception:
        pass

    return "\n".join(lines)


# -------------------------------------------------------------------
# Playwright 브라우저 기반 폴링
# -------------------------------------------------------------------
async def polling_loop(test_once: bool = False, project_filter: str | None = None):
    from playwright.async_api import async_playwright
    try:
        from playwright_stealth import Stealth
        HAS_STEALTH = True
    except ImportError:
        HAS_STEALTH = False
        logger.warning("playwright-stealth 미설치 — stealth 미적용")

    # genspark_common 환경변수 로드
    sys.path.insert(0, str(BASE_DIR))
    from genspark_common import load_env

    env = load_env()

    # 폴링 대상 프로젝트 결정
    active_projects = {}
    if project_filter:
        p_upper = project_filter.upper()
        if p_upper in PROJECTS and PROJECTS[p_upper]["chat_url"]:
            active_projects = {p_upper: PROJECTS[p_upper]}
        else:
            logger.error("알 수 없거나 URL 미설정 프로젝트: %s", project_filter)
            return False
    else:
        active_projects = {k: v for k, v in PROJECTS.items() if v["chat_url"]}

    logger.info("활성 프로젝트: %s", list(active_projects.keys()))

    # 프로젝트별 상태 추적
    last_directive_hash: dict[str, int | None] = {k: None for k in active_projects}
    last_periodic_report_time: datetime.datetime | None = None  # 30분 정기 보고 타임스탬프
    # 피드백 루프 방지: CEO 승인 대기 메시지 전송 후 30분 쿨다운
    # Bug Fix: 브릿지가 CEO 승인 대기를 보내면 AI가 DIRECTIVE로 응답 → 브릿지가 재검출 → 무한 루프
    last_ceo_approval_sent: dict[str, datetime.datetime | None] = {k: None for k in active_projects}
    CEO_APPROVAL_COOLDOWN_SEC = 1800  # 30분
    # 2분 대기 지시 요청: 마지막 지시 처리 시각 + 마지막 대기 메시지 전송 시각
    _now0 = datetime.datetime.now(KST)
    last_directive_time: dict[str, datetime.datetime] = {k: _now0 for k in active_projects}
    last_idle_msg_time: dict[str, datetime.datetime | None] = {k: None for k in active_projects}

    async with async_playwright() as p:
        # session.json 있으면 재사용, 없으면 신규
        storage_state = str(SESSION_PATH) if SESSION_PATH.exists() else None
        browser = await p.chromium.launch(
            headless=False,  # Xvfb 가상 디스플레이 사용
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = await browser.new_context(
            storage_state=storage_state,
            viewport={"width": 1280, "height": 900},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        )
        page = await context.new_page()
        if HAS_STEALTH:
            stealth = Stealth()
            await stealth.apply_stealth_async(page)
            logger.info("playwright-stealth 적용 완료 (apply_stealth_async)")

        logger.info("브라우저 기동 완료. 폴링 시작. test_once=%s", test_once)

        while True:
            for proj_key, proj_cfg in active_projects.items():
                chat_url = proj_cfg["chat_url"]
                cursor_prefix = proj_cfg["cursor_prefix"]
                tag = proj_cfg["tag"]
                try:
                    await page.goto(chat_url, wait_until="domcontentloaded", timeout=30_000)
                    await asyncio.sleep(5)  # 페이지 완전 로딩 대기

                    # test_once: 접속 확인 + 테스트 메시지 전송 후 종료
                    if test_once:
                        if "login" in page.url or "sign" in page.url.lower():
                            logger.error("[test-once][%s] 세션 만료 — 수동 로그인 필요", proj_key)
                            await browser.close()
                            return False
                        try:
                            body_text = await page.evaluate("() => document.body.innerText")
                        except Exception as e:
                            logger.error("[test-once][%s] 페이지 평가 실패: %s", proj_key, e)
                            await browser.close()
                            return False
                        if len(body_text) > 100:
                            logger.info("[test-once][%s] 접속 성공 (%d자)", proj_key, len(body_text))
                            await _send_chat_message(page, f"{cursor_prefix} 브릿지 통합 테스트 — 연결 확인", project=tag)
                            logger.info("[test-once][%s] 테스트 메시지 전송 완료", proj_key)
                        else:
                            logger.error("[test-once][%s] 페이지 내용 없음 — Cloudflare 차단 의심", proj_key)
                            await browser.close()
                            return False
                        continue  # test_once 시 다음 프로젝트로

                    # 로그인 만료 감지
                    if "login" in page.url or "sign" in page.url.lower():
                        logger.warning("[%s] 세션 만료 감지 — session.json 재로드 시도", proj_key)
                        if SESSION_PATH.exists():
                            await context.close()
                            context = await browser.new_context(
                                storage_state=str(SESSION_PATH),
                                viewport={"width": 1280, "height": 900},
                            )
                            page = await context.new_page()
                            await page.goto(chat_url, wait_until="domcontentloaded", timeout=30_000)
                            await asyncio.sleep(3)
                        if "login" in page.url:
                            logger.error("[%s] 세션 복원 실패 — 수동 로그인 필요", proj_key)
                            continue

                    # Pending 파일 큐 처리 (Cursor 직접 전송용)
                    # 파일: /root/.genspark/pending_send_{proj_key.lower()}.txt
                    pending_file = BASE_DIR / f"pending_send_{proj_key.lower()}.txt"
                    if pending_file.exists():
                        try:
                            pending_msg = pending_file.read_text(encoding="utf-8").strip()
                            if pending_msg:
                                logger.info("[%s] Pending 메시지 발견 — 즉시 전송 (%d자)", proj_key, len(pending_msg))
                                await _send_chat_message(page, pending_msg, project=tag)
                                # Cursor 보고 전송 = 활동으로 간주, 대기 타이머 리셋
                                last_directive_time[proj_key] = datetime.datetime.now(KST)
                                last_idle_msg_time[proj_key] = None
                            pending_file.unlink(missing_ok=True)
                        except Exception as e:
                            logger.error("[%s] Pending 메시지 처리 실패: %s", proj_key, e)

                    # 페이지 텍스트 추출
                    body_text = await page.evaluate("() => document.body.innerText")

                    # DIRECTIVE 블록 파싱
                    directive = parse_directive(body_text)
                    _now = datetime.datetime.now(KST)
                    _no_new_directive = (not directive) or (hash(directive) == last_directive_hash[proj_key])

                    if _no_new_directive:
                        # 2분 이상 지시 없으면 대기 메시지 전송 (이후 2분마다 반복)
                        elapsed_idle = (_now - last_directive_time[proj_key]).total_seconds()
                        last_idle = last_idle_msg_time[proj_key]
                        elapsed_since_idle_msg = (
                            (_now - last_idle).total_seconds() if last_idle is not None
                            else elapsed_idle  # 아직 한 번도 안 보냈으면 경과 시간 그대로
                        )
                        if elapsed_idle >= IDLE_WAIT_SEC and elapsed_since_idle_msg >= IDLE_WAIT_SEC:
                            now_str = _now.strftime("%Y-%m-%d %H:%M KST")
                            idle_msg = f"[CURSOR-{proj_key}] {now_str} 지시 대기 중 — 다음 작업을 알려주세요"
                            logger.info("[%s] 2분 대기 초과 — 지시 요청 메시지 전송", proj_key)
                            await _send_chat_message(page, idle_msg, project=tag)
                            last_idle_msg_time[proj_key] = _now
                        elif not directive:
                            logger.debug("[%s] 지시 없음 — 대기 중 (idle %.0fs)", proj_key, elapsed_idle)
                        else:
                            logger.debug("[%s] 동일 지시 — 스킵", proj_key)
                        continue

                    # 중복 실행 방지
                    directive_hash = hash(directive)
                    if directive_hash == last_directive_hash[proj_key]:
                        logger.debug("[%s] 동일 지시 — 스킵", proj_key)
                        continue

                    last_directive_hash[proj_key] = directive_hash
                    last_directive_time[proj_key] = datetime.datetime.now(KST)  # 지시 처리 → 타이머 리셋
                    last_idle_msg_time[proj_key] = None  # 대기 메시지 타이머 리셋
                    logger.info("[%s] 지시 감지:\n%s", proj_key, directive[:300])

                    # Directive를 pending 폴더에 저장 (처리 전 스냅샷)
                    _save_directive_to_pending(tag, directive)

                    # 화이트리스트 판별
                    if not is_whitelisted(directive, project=proj_key):
                        # 피드백 루프 방지: 쿨다운 기간 내라면 재전송 금지
                        now_dt = datetime.datetime.now(KST)
                        last_sent = last_ceo_approval_sent[proj_key]
                        if last_sent is not None:
                            elapsed = (now_dt - last_sent).total_seconds()
                            if elapsed < CEO_APPROVAL_COOLDOWN_SEC:
                                logger.debug(
                                    "[%s] CEO 승인 대기 쿨다운 중 (%.0f초 남음) — 스킵",
                                    proj_key, CEO_APPROVAL_COOLDOWN_SEC - elapsed
                                )
                                continue
                        # 지시 내용 첫 줄만 발췌 (줄바꿈 이후 생략)
                        directive_preview = directive.split("\n")[0].strip()[:80]
                        msg = f"{cursor_prefix} CEO 승인 대기 — {directive_preview}"
                        logger.warning("[%s] whitelist 외 작업 — 승인 대기 메시지 전송", proj_key)
                        await _send_chat_message(page, msg, project=tag)
                        last_ceo_approval_sent[proj_key] = now_dt
                        continue

                    # FINAL_GO_CONFIRMED / 완료 확인 지시는 조용히 스킵 (응답 불필요)
                    if "FINAL_GO_CONFIRMED" in directive or "ACTION: VIRTUAL_RUN_COMPLETE" in directive:
                        logger.info("[%s] FINAL_GO_CONFIRMED 확인 — 응답 없이 대기", proj_key)
                        continue

                    # 화이트리스트 실행
                    result_summary = execute_whitelist_directive(directive)
                    logger.info("[%s] 실행 결과: %s", proj_key, result_summary)

                    report = (
                        f"{cursor_prefix} push 완료\n"
                        f"작업: Genspark 브릿지 자동 지시 실행\n"
                        f"결과: {result_summary}\n"
                        f"다음: 지시 대기"
                    )
                    await _send_chat_message(page, report, project=tag)

                except Exception as e:
                    logger.exception("[%s] 폴링 사이클 예외 — 다음 사이클 계속: %s", proj_key, e)

            # ── 30분 정기 통합 현황 보고 ──
            if not test_once:
                now_dt = datetime.datetime.now(KST)
                elapsed = (
                    (now_dt - last_periodic_report_time).total_seconds()
                    if last_periodic_report_time is not None
                    else PERIODIC_REPORT_INTERVAL_SEC  # 최초 실행 시 즉시 발송
                )
                if elapsed >= PERIODIC_REPORT_INTERVAL_SEC:
                    last_periodic_report_time = now_dt
                    unified_msg = build_unified_status_report()
                    logger.info("30분 통합 현황 보고 발송 → CEO 지휘소 + 텔레그램")
                    try:
                        await page.goto(CEO_CHAT_URL, wait_until="domcontentloaded", timeout=30_000)
                        await asyncio.sleep(5)
                        await _send_chat_message(page, unified_msg, project="CEO")
                    except Exception as e:
                        logger.exception("통합 현황 보고 전송 실패: %s", e)

            # test_once 모드 종료
            if test_once:
                await browser.close()
                return True

            await asyncio.sleep(60)


async def _send_chat_message(page, message: str, project: str = "KIS"):
    """채팅 입력창에 메시지 전송 + 텔레그램 병행 발송"""
    # 텔레그램 발송 (비동기 없음 — 동기 라이브러리 사용)
    try:
        sys.path.insert(0, str(BASE_DIR))
        import telegram_report as tg
        tg_ok = tg.send(message, project=project)
        logger.info("텔레그램 발송: %s", "성공" if tg_ok else "실패(설정 없음)")
    except Exception as e:
        logger.warning("텔레그램 발송 오류: %s", e)

    # Genspark 대화창 전송 — pressSequentially 방식 (실제 키보드 입력 시뮬레이션)
    # Bug Fix: fill()/nativeInputValueSetter 방식은 Genspark React 컴포넌트 내부 상태를
    # 갱신하지 못해 메시지가 잘리거나 빈 메시지가 제출되는 문제 발생.
    # pressSequentially()는 keydown/keypress/keyup 이벤트를 순서대로 발생시켜 React state를
    # 정확히 갱신한다.
    try:
        ta = page.locator('textarea[name="query"]')
        await ta.wait_for(state="visible", timeout=5000)
        await ta.click()
        # 기존 내용 전체 삭제
        await ta.press("Control+a")
        await ta.press("Delete")
        await asyncio.sleep(0.2)
        # 실제 키보드 타이핑 시뮬레이션 (React 이벤트 정상 발생)
        await ta.press_sequentially(message, delay=15)
        await asyncio.sleep(0.5)
        await ta.press("Enter")
        logger.info("Genspark 메시지 전송 완료 (%d자)", len(message))
    except Exception as e:
        logger.error("Genspark 메시지 전송 실패: %s", e)


# -------------------------------------------------------------------
# 진입점
# -------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genspark Bridge V1 (멀티 프로젝트)")
    parser.add_argument("--test-once", action="store_true",
                        help="1회 폴링 후 종료 (통합 테스트용)")
    parser.add_argument("--project", type=str, default=None,
                        help="단일 프로젝트 지정 (KIS/GO100). 미입력 시 전체 폴링")
    args = parser.parse_args()

    if not args.test_once:
        acquire_lock()

    try:
        result = asyncio.run(polling_loop(
            test_once=args.test_once,
            project_filter=args.project,
        ))
        if args.test_once:
            sys.exit(0 if result else 1)
    finally:
        if not args.test_once:
            release_lock()
