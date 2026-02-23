"""
폴더 내 이미지 EXIF 시간 기반 자동 분류.
시간순 정렬 후 임계값(초) 초과 간격 시 새 그룹(코디)으로 구분.
"""
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from PIL import Image

logger = logging.getLogger(__name__)

# 지원 확장자
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic"}

# EXIF 태그: DateTimeOriginal(36867), DateTime(306)
EXIF_DATETIME_ORIGINAL = 36867
EXIF_DATETIME = 306


@dataclass
class ClassifiedGroup:
    """한 코디 그룹 (연속 촬영 구간)."""
    group_index: int
    images: List[Path]
    start_time: Optional[float] = None  # timestamp
    end_time: Optional[float] = None
    duration_seconds: Optional[float] = None


@dataclass
class ClassifyResult:
    """분류 결과."""
    total_images: int
    total_groups: int
    groups: List[ClassifiedGroup]
    threshold_seconds: float
    no_exif_images: List[Path] = field(default_factory=list)


def _parse_exif_datetime(path: Path) -> Optional[float]:
    """EXIF DateTimeOriginal 또는 DateTime 파싱. 실패 시 None."""
    try:
        with Image.open(path) as im:
            exif = im.getexif()
            if not exif:
                return None
            for tag in (EXIF_DATETIME_ORIGINAL, EXIF_DATETIME):
                val = exif.get(tag)
                if not val:
                    continue
                # "2024:01:15 14:30:00" 형태
                from datetime import datetime
                s = str(val).strip()
                for fmt in ("%Y:%m:%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
                    try:
                        dt = datetime.strptime(s, fmt)
                        return dt.timestamp()
                    except ValueError:
                        continue
    except Exception as e:
        logger.debug("EXIF read %s: %s", path, e)
    return None


class AutoClassifier:
    """EXIF 시간 기반 이미지 그룹 분류."""

    def __init__(self, threshold_seconds: float = 180.0) -> None:
        self.threshold_seconds = threshold_seconds

    def extract_datetime(self, path: Path) -> Optional[float]:
        """
        이미지 촬영 시각 추출.
        EXIF DateTimeOriginal/DateTime 우선, 없으면 파일 mtime, 실패 시 None.
        """
        ts = _parse_exif_datetime(path)
        if ts is not None:
            return ts
        try:
            return path.stat().st_mtime
        except OSError:
            return None

    def classify_folder(self, folder_path: str | Path) -> ClassifyResult:
        """
        폴더 내 jpg/jpeg/png/heic 수집 → EXIF 시간 추출 → 시간순 정렬
        → 인접 촬영 간격이 threshold_seconds 초과 시 새 그룹.
        """
        folder = Path(folder_path)
        if not folder.is_dir():
            return ClassifyResult(
                total_images=0,
                total_groups=0,
                groups=[],
                threshold_seconds=self.threshold_seconds,
                no_exif_images=[],
            )

        paths: List[Path] = []
        for p in folder.iterdir():
            if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS:
                paths.append(p)

        # (timestamp, path) 리스트. timestamp 없으면 (None, path)
        no_exif: List[Path] = []
        timed: List[tuple[Optional[float], Path]] = []
        for p in paths:
            ts = self.extract_datetime(p)
            if ts is None:
                no_exif.append(p)
            else:
                timed.append((ts, p))

        timed.sort(key=lambda x: (x[0] or 0, str(x[1])))

        groups: List[ClassifiedGroup] = []
        current: List[Path] = []
        start_time: Optional[float] = None
        last_time: Optional[float] = None

        for ts, p in timed:
            if last_time is not None and ts is not None and (ts - last_time) > self.threshold_seconds:
                if current:
                    end_time = last_time
                    duration = (end_time - start_time) if start_time is not None else None
                    groups.append(ClassifiedGroup(
                        group_index=len(groups) + 1,
                        images=current.copy(),
                        start_time=start_time,
                        end_time=end_time,
                        duration_seconds=duration,
                    ))
                    current = []
                    start_time = None
                    last_time = None
            if ts is not None:
                last_time = ts
                if start_time is None:
                    start_time = ts
            current.append(p)

        if current:
            end_time = last_time
            duration = (end_time - start_time) if start_time is not None else None
            groups.append(ClassifiedGroup(
                group_index=len(groups) + 1,
                images=current.copy(),
                start_time=start_time,
                end_time=end_time,
                duration_seconds=duration,
            ))

        return ClassifyResult(
            total_images=len(paths),
            total_groups=len(groups),
            groups=groups,
            threshold_seconds=self.threshold_seconds,
            no_exif_images=no_exif,
        )

    def classify_and_move(
        self,
        folder_path: str | Path,
        output_base: str | Path,
        *,
        use_symlink: bool = False,
        name_prefix: str = "코디",
    ) -> List[Path]:
        """
        분류 후 output_base 아래 코디_01, 코디_02 ... 폴더 생성해
        이미지 복사 또는 심볼릭 링크.
        반환: 생성된 디렉터리 경로 목록.
        """
        result = self.classify_folder(folder_path)
        output = Path(output_base)
        output.mkdir(parents=True, exist_ok=True)
        created: List[Path] = []
        for g in result.groups:
            dir_name = f"{name_prefix}_{g.group_index:02d}"
            dest_dir = output / dir_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            created.append(dest_dir)
            for src in g.images:
                dst = dest_dir / src.name
                if use_symlink:
                    if not dst.exists():
                        try:
                            dst.symlink_to(src.resolve())
                        except OSError:
                            import shutil
                            shutil.copy2(src, dst)
                else:
                    import shutil
                    shutil.copy2(src, dst)
        return created

    def reclassify(self, folder_path: str | Path, threshold_seconds: float) -> ClassifyResult:
        """새 임계값으로 다시 분류."""
        self.threshold_seconds = threshold_seconds
        return self.classify_folder(folder_path)
