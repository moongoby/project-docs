"""
HEIC → JPG 변환 (pillow-heif), 뉴톡 규격 리사이즈 (1200/600/300px).
"""
import logging
from pathlib import Path
from typing import List, Optional

from PIL import Image

logger = logging.getLogger(__name__)

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pillow_heif = None  # type: ignore


def heic_to_jpg(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """
    HEIC 파일을 JPG로 변환. output_path 미지정 시 같은 디렉터리에 .jpg 로 저장.
    """
    if pillow_heif is None:
        raise RuntimeError("pillow-heif not installed")
    input_path = Path(input_path)
    if output_path is None:
        output_path = input_path.with_suffix(".jpg")
    output_path = Path(output_path)
    try:
        img = Image.open(input_path)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(output_path, "JPEG", quality=92)
        return output_path
    except Exception as e:
        logger.exception("heic_to_jpg error: %s", input_path)
        raise RuntimeError(f"HEIC 변환 실패: {e}") from e


def resize_newtalk_sizes(
    input_path: Path,
    output_dir: Path,
    sizes: Optional[List[int]] = None,
) -> List[Path]:
    """
    뉴톡 규격 사이즈(기본 1200, 600, 300 px)로 리사이즈하여 output_dir 에 저장.
    파일명: 원본이름_1200.jpg 등. 긴 변 기준으로 리사이즈.
    """
    if sizes is None:
        sizes = [1200, 600, 300]
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result: List[Path] = []
    try:
        img = Image.open(input_path).convert("RGB")
        w, h = img.size
        base_name = input_path.stem
        long_side = max(w, h)
        for size in sizes:
            # 원본 장축이 요청 크기 이하이면 확대하지 않고 해당 사이즈 스킵
            if long_side <= size:
                continue
            if w >= h:
                nw, nh = size, int(h * size / w) if w else size
            else:
                nw, nh = int(w * size / h) if h else size, size
            out_img = img.resize((nw, nh), Image.Resampling.LANCZOS)
            out_path = output_dir / f"{base_name}_{size}.jpg"
            out_img.save(out_path, "JPEG", quality=92)
            result.append(out_path)
        return result
    except Exception as e:
        logger.exception("resize_newtalk error: %s", input_path)
        raise RuntimeError(f"리사이즈 실패: {e}") from e
