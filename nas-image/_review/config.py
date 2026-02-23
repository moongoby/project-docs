"""
설정 모듈. pydantic-settings로 환경변수 및 기본값 관리.
이미지 경로, DB 경로, 뉴톡 규격 사이즈 등.
"""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """앱 설정. 환경변수 또는 .env에서 로드."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 경로
    photos_root: Path = Path("/data/photos")
    processed_root: Path = Path("/data/processed")
    db_dir: Path = Path("/app/data/db")
    log_dir: Path = Path("/app/data/logs")

    # API
    port: int = 8100

    # PhotoRoom API (배경 제거). 미설정 시 rembg 폴백
    photoroom_api_key: str = ""

    # 뉴톡 규격 사이즈 (px). 리사이즈 시 사용
    newtalk_sizes: List[int] = [1200, 600, 300]

    # 114서버 동기화 (rsync)
    sync_114_enabled: bool = True
    sync_114_user: str = "nasync"
    sync_114_host: str = "114.207.244.86"
    sync_114_port: int = 7916
    sync_114_ssh_key: str = "/root/.ssh/id_ed25519"
    sync_114_remote_base: str = "/home/danharoo/www/data/files/goods/goodscode/img"


def get_settings() -> Settings:
    """설정 싱글톤 반환."""
    return Settings()
