"""
QC 승인된 이미지를 114서버로 rsync 전송하는 모듈.
NAS _processed/{goods_code}/114/ → 114서버 상품코드 폴더 동기화.
"""
import logging
import subprocess
from pathlib import Path
from typing import Any

from app.config import get_settings

logger = logging.getLogger(__name__)


class Rsync114:
    """NAS _processed/ → 114서버 동기화."""

    def __init__(self) -> None:
        s = get_settings()
        self._enabled = getattr(s, "sync_114_enabled", True)
        self._user = getattr(s, "sync_114_user", "nasync")
        self._host = getattr(s, "sync_114_host", "114.207.244.86")
        self._port = getattr(s, "sync_114_port", 7916)
        self._ssh_key = getattr(s, "sync_114_ssh_key", "")
        self._remote_base = getattr(s, "sync_114_remote_base", "/home/danharoo/www/data/files/goods/goodscode/img")

    def _ssh_cmd(self) -> list[str]:
        """ssh -p PORT -i KEY 조각 (rsync -e 용)."""
        parts = ["ssh", "-o", "StrictHostKeyChecking=no", "-o", "ConnectTimeout=10", "-p", str(self._port)]
        if self._ssh_key:
            parts.extend(["-i", self._ssh_key])
        return parts

    def sync_goods(self, goods_code: str, processed_dir: Path) -> dict[str, Any]:
        """
        상품코드 단위로 114서버에 동기화.

        1. processed_dir/{goods_code}/114/ 폴더에서 매핑된 파일 수집
        2. 114서버에 상품코드 폴더 생성 (소문자)
        3. rsync로 전송
        4. 결과 반환 (성공 파일 수, 실패 내역)

        rsync 명령:
          rsync -avz -e "ssh -p 7916 -i {SSH_KEY}" \\
            {processed_dir}/{goods_code}/114/ \\
            nasync@114.207.244.86:/home/danharoo/www/data/files/goods/goodscode/img/{소문자코드}/
        """
        code_lower = goods_code.lower().strip()
        processed_dir = Path(processed_dir)
        dir_114 = processed_dir / code_lower / "114"

        result: dict[str, Any] = {
            "goods_code": code_lower,
            "success_count": 0,
            "failed": [],
            "error": None,
        }

        if not self._enabled:
            result["error"] = "sync_114 비활성화됨"
            return result

        if not dir_114.is_dir():
            result["error"] = f"114 디렉터리 없음: {dir_114}"
            return result

        # 114/ 및 114/thumbnail/ 내 모든 파일 수집 (전송 후 개수 확인용)
        all_files = list(dir_114.rglob("*"))
        files_only = [f for f in all_files if f.is_file()]
        if not files_only:
            result["error"] = "전송할 파일이 없습니다."
            return result

        remote_dest = f"{self._user}@{self._host}:{self._remote_base.rstrip('/')}/{code_lower}/"
        src = str(dir_114) + "/"
        ssh_argv = self._ssh_cmd()
        rsync_cmd = [
            "rsync",
            "-avz",
            "-e",
            " ".join(ssh_argv),
            src,
            remote_dest,
        ]
        try:
            proc = subprocess.run(
                rsync_cmd,
                capture_output=True,
                text=True,
                timeout=120,
            )
            if proc.returncode != 0:
                result["error"] = proc.stderr or proc.stdout or f"rsync exit {proc.returncode}"
                result["failed"] = [f.name for f in files_only]
                return result
            result["success_count"] = len(files_only)
            return result
        except subprocess.TimeoutExpired:
            result["error"] = "rsync 타임아웃"
            result["failed"] = [f.name for f in files_only]
            return result
        except FileNotFoundError:
            result["error"] = "rsync 또는 ssh 명령을 찾을 수 없음"
            return result
        except Exception as e:
            logger.exception("sync_goods rsync 실패: %s", goods_code)
            result["error"] = str(e)
            result["failed"] = [f.name for f in files_only]
            return result

    def verify_sync(self, goods_code: str) -> dict[str, Any]:
        """
        114서버에 파일이 정상 전송됐는지 확인.
        ssh로 ls 실행하여 파일 목록 반환.
        """
        code_lower = goods_code.lower().strip()
        result: dict[str, Any] = {
            "goods_code": code_lower,
            "success": False,
            "files": [],
            "error": None,
        }

        if not self._enabled:
            result["error"] = "sync_114 비활성화됨"
            return result

        remote_path = f"{self._remote_base.rstrip('/')}/{code_lower}"
        cmd = self._ssh_cmd() + [f"{self._user}@{self._host}", f"find {remote_path} -type f 2>/dev/null || true"]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15,
            )
            if proc.returncode != 0 and not proc.stdout:
                result["error"] = proc.stderr or f"ssh exit {proc.returncode}"
                return result
            # find 출력: 한 줄에 한 경로
            lines = [ln.strip() for ln in (proc.stdout or "").splitlines() if ln.strip()]
            result["files"] = [Path(ln).name for ln in lines]
            result["success"] = True
            return result
        except subprocess.TimeoutExpired:
            result["error"] = "ssh 타임아웃"
            return result
        except FileNotFoundError:
            result["error"] = "ssh 명령을 찾을 수 없음"
            return result
        except Exception as e:
            logger.exception("verify_sync 실패: %s", goods_code)
            result["error"] = str(e)
            return result
