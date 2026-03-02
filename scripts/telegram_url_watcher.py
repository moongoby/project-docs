#!/usr/bin/env python3
"""
telegram_url_watcher.py
CEO 텔레그램 메시지에서 [TAG] URL 패턴 감지 → .env + CEO-COMMAND-CENTER.md 자동 업데이트
"""

import os
import re
import sys
import time
import logging
import subprocess
import requests
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── 설정 ────────────────────────────────────────────────────────────────────
BOT_TOKEN   = os.getenv("TELEGRAM_BOT_TOKEN", "8327167593:AAGln8wlk4XQDLeeqVCo_DESVPcGmbNYXPk")
CHAT_ID     = os.getenv("TELEGRAM_CHAT_ID",   "6817948795")
ENV_PATH    = os.getenv("GENSPARK_ENV_PATH",   "/root/.genspark/.env")
CMD_CENTER  = "/root/project-docs/shared/CEO-COMMAND-CENTER.md"
POLL_SEC    = 30

KST = timezone(timedelta(hours=9))

# 지원 태그 → .env 키 매핑
TAG_TO_ENV = {
    "KIS":   "GENSPARK_CHAT_KIS",
    "GO100": "GENSPARK_CHAT_GO100",
    "AADS":  "GENSPARK_CHAT_AADS",
    "SF":    "GENSPARK_CHAT_SF",
    "NAS":   "GENSPARK_CHAT_NAS",
    "NTV2":  "GENSPARK_CHAT_NTV2",
}

# CEO-COMMAND-CENTER.md URL 컬럼 정규식용 태그 패턴
TAG_TO_MD_PATTERN = {
    "KIS":   r"(\[`?\[?KIS[^\]]*\]`?\].*?https://www\.genspark\.ai/agents\?id=)[^\s|]+",
    "GO100": r"(\[`?\[?GO100[^\]]*\]`?\].*?https://www\.genspark\.ai/agents\?id=)[^\s|]+",
    "AADS":  r"(\[`?\[?AADS[^\]]*\]`?\].*?https://www\.genspark\.ai/agents\?id=)[^\s|]+",
    "SF":    r"(\[`?\[?SF[^\]]*\]`?\].*?https://www\.genspark\.ai/agents\?id=)[^\s|]+",
    "NAS":   r"(\[`?\[?NAS[^\]]*\]`?\].*?https://www\.genspark\.ai/agents\?id=)[^\s|]+",
    "NTV2":  r"(\[`?\[?NTV2[^\]]*\]`?\].*?https://www\.genspark\.ai/agents\?id=)[^\s|]+",
}

# ── 로깅 ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s KST [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/root/.genspark/logs/telegram_url_watcher.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ── Telegram 유틸 ────────────────────────────────────────────────────────────
def tg_api(method: str, **params) -> dict:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        r = requests.post(url, json=params, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        log.error(f"Telegram API 오류 ({method}): {e}")
        return {}

def send_message(text: str):
    result = tg_api("sendMessage", chat_id=CHAT_ID, text=text)
    if result.get("ok"):
        log.info(f"텔레그램 발송 완료: {text[:60]}")
    else:
        log.error(f"텔레그램 발송 실패: {result}")

def get_updates(offset: int) -> list:
    result = tg_api("getUpdates", offset=offset, timeout=20, allowed_updates=["message"])
    return result.get("result", []) if result.get("ok") else []

# ── .env 업데이트 ──────────────────────────────────────────────────────────
def update_env(tag: str, new_url: str) -> bool:
    env_key = TAG_TO_ENV[tag]
    try:
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

        updated = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{env_key}="):
                new_lines.append(f"{env_key}={new_url}\n")
                updated = True
                log.info(f".env 업데이트: {env_key}={new_url}")
            else:
                new_lines.append(line)

        if not updated:
            new_lines.append(f"{env_key}={new_url}\n")
            log.info(f".env 신규 추가: {env_key}={new_url}")

        with open(ENV_PATH, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    except Exception as e:
        log.error(f".env 업데이트 실패: {e}")
        return False

# ── CEO-COMMAND-CENTER.md 업데이트 ────────────────────────────────────────
def update_md(tag: str, new_url: str) -> bool:
    try:
        with open(CMD_CENTER, "r", encoding="utf-8") as f:
            content = f.read()

        # 기존 ID 추출 후 교체 (agents?id=XXXX 패턴)
        # 태그가 포함된 행에서 URL 교체
        tag_escaped = re.escape(tag)
        # 마크다운 테이블 내 해당 태그 행의 URL 교체
        pattern = (
            r"((?:\[`\[" + tag_escaped + r"[^\]]*\]`\]|\[" + tag_escaped + r"[^\]]*\])[^\n]*"
            r"https://www\.genspark\.ai/agents\?id=)[^\s|]+"
        )
        new_content, n = re.subn(pattern, r"\g<1>" + new_url.split("?id=")[-1], content)

        if n == 0:
            # 더 넓은 패턴으로 재시도: 행에 tag 문자열 포함
            lines = content.split("\n")
            new_lines = []
            replaced = 0
            for line in lines:
                if tag in line and "genspark.ai/agents" in line:
                    line = re.sub(
                        r"https://www\.genspark\.ai/agents\?id=[^\s|]+",
                        new_url,
                        line,
                    )
                    replaced += 1
                new_lines.append(line)
            if replaced:
                new_content = "\n".join(new_lines)
                n = replaced
            else:
                log.warning(f"CEO-COMMAND-CENTER.md: [{tag}] URL 패턴 미발견 — 수동 확인 필요")
                return False

        with open(CMD_CENTER, "w", encoding="utf-8") as f:
            f.write(new_content)
        log.info(f"CEO-COMMAND-CENTER.md [{tag}] URL 업데이트 완료 ({n}곳)")
        return True
    except Exception as e:
        log.error(f"CEO-COMMAND-CENTER.md 업데이트 실패: {e}")
        return False

# ── genspark-bridge 재시작 ─────────────────────────────────────────────────
def restart_bridge() -> bool:
    try:
        result = subprocess.run(
            ["systemctl", "restart", "genspark-bridge"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            log.info("genspark-bridge 재시작 완료")
            return True
        else:
            log.error(f"genspark-bridge 재시작 실패: {result.stderr}")
            return False
    except Exception as e:
        log.error(f"genspark-bridge 재시작 오류: {e}")
        return False

# ── 메시지 처리 ───────────────────────────────────────────────────────────
# CEO 메시지 패턴: [TAG] https://genspark.ai/... (또는 www.genspark.ai)
URL_PATTERN = re.compile(
    r"\[(KIS|GO100|AADS|SF|NAS|NTV2)\]\s+(https://(?:www\.)?genspark\.ai/[^\s]+)"
)

GENSPARK_DIR = Path("/root/.genspark")


def write_init_file(tag: str, new_url: str) -> bool:
    """bridge가 다음 폴링 시 대화창 초기화 메시지를 전송하도록 신호 파일 생성.
    파일: /root/.genspark/init_chat_{tag}.json
    """
    import json
    init_path = GENSPARK_DIR / f"init_chat_{tag.lower()}.json"
    try:
        init_path.write_text(
            json.dumps({"tag": tag, "url": new_url, "ts": datetime.now(KST).isoformat()},
                       ensure_ascii=False),
            encoding="utf-8",
        )
        log.info(f"[{tag}] 초기화 신호 파일 생성: {init_path}")
        return True
    except Exception as e:
        log.error(f"[{tag}] 초기화 신호 파일 생성 실패: {e}")
        return False


def process_message(text: str):
    matches = URL_PATTERN.findall(text)
    if not matches:
        return

    for tag, new_url in matches:
        log.info(f"URL 변경 감지: [{tag}] → {new_url}")
        env_ok  = update_env(tag, new_url)
        md_ok   = update_md(tag, new_url)
        init_ok = write_init_file(tag, new_url)  # 초기화 신호 파일 생성
        bridge_ok = restart_bridge()              # bridge 재시작 (새 URL로 폴링 + init 처리)

        status_env    = "✅" if env_ok    else "❌"
        status_md     = "✅" if md_ok     else "❌"
        status_init   = "✅" if init_ok   else "❌"
        status_bridge = "✅" if bridge_ok else "❌"

        msg = (
            f"✅ [{tag}] 대화창 URL 변경 완료\n"
            f"  .env 업데이트: {status_env}\n"
            f"  CMD-CENTER.md: {status_md}\n"
            f"  초기화 신호:   {status_init}\n"
            f"  bridge 재시작: {status_bridge}\n"
            f"  새 URL: {new_url}\n"
            f"  → bridge 재가동 후 첫 메시지 자동 전송 예정"
        )
        send_message(msg)

# ── 메인 폴링 루프 ─────────────────────────────────────────────────────────
def main():
    log.info("=" * 60)
    log.info("telegram_url_watcher 시작 (폴링 주기: 30초)")
    log.info(f"감시 태그: {list(TAG_TO_ENV.keys())}")
    log.info(f".env 경로: {ENV_PATH}")
    log.info(f"CMD-CENTER: {CMD_CENTER}")
    log.info("=" * 60)

    # 시작 시 현재까지의 update_id 가져와서 과거 메시지 스킵
    updates = get_updates(offset=-1)
    offset = (updates[-1]["update_id"] + 1) if updates else 0
    log.info(f"초기 offset: {offset} (과거 메시지 스킵)")

    while True:
        try:
            updates = get_updates(offset=offset)
            for upd in updates:
                offset = upd["update_id"] + 1
                msg = upd.get("message") or upd.get("channel_post") or {}
                from_id = str(msg.get("from", {}).get("id", ""))
                chat_from_id = str(msg.get("chat", {}).get("id", ""))
                text = msg.get("text", "")

                # CEO CHAT_ID에서 온 메시지만 처리
                if chat_from_id == CHAT_ID and text:
                    log.debug(f"메시지 수신: {text[:80]}")
                    process_message(text)

        except Exception as e:
            log.error(f"폴링 루프 오류: {e}")

        time.sleep(POLL_SEC)

if __name__ == "__main__":
    os.makedirs("/root/.genspark/logs", exist_ok=True)
    main()
