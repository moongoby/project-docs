"""
모델컷 자동 보정: EXIF 회전, 자동 노출, CLAHE 대비, 언샤프마스크.
OpenCV + Pillow 사용. 1장씩 순차 처리. (색온도 변경 없음)
"""
import logging
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


# 레퍼런스 톤 매칭 등에서 활용 가능. 현재는 색온도 변경 없음.
# def _gray_world_wb(img: np.ndarray) -> np.ndarray:
#     """Gray World 화이트밸런스."""
#     avg = img.mean(axis=(0, 1))
#     gray = avg.mean()
#     if gray <= 0:
#         return img
#     scale = gray / (avg + 1e-6)
#     out = (img * scale).clip(0, 255).astype(np.uint8)
#     return out


def _auto_exposure(img: np.ndarray, target_mean: float = 135.0) -> np.ndarray:
    """자동 노출 (평균 밝기 목표치로 스케일)."""
    mean = img.mean()
    if mean <= 0:
        return img
    gain = target_mean / mean
    out = (img * gain).clip(0, 255).astype(np.uint8)
    return out


def correct_model_shot(input_path: Path, output_path: Path) -> None:
    """
    모델컷 자동 보정: EXIF 회전 → 자동 노출(135) → CLAHE(1.5) → 언샤프마스크(1.15) → 저장.
    """
    try:
        pil_img = Image.open(input_path)
        pil_img = ImageOps.exif_transpose(pil_img)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        img = np.array(pil_img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        img = _auto_exposure(img, target_mean=135.0)

        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        l = clahe.apply(l)
        lab = cv2.merge([l, a, b])
        img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

        blur = cv2.GaussianBlur(img, (0, 0), 2.0)
        img = cv2.addWeighted(img, 1.15, blur, -0.15, 0)
        img = np.clip(img, 0, 255).astype(np.uint8)

        out_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        out_pil = Image.fromarray(out_rgb)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        out_pil.save(output_path, "JPEG", quality=92)
    except Exception as e:
        logger.exception("auto_corrector error: %s", input_path)
        raise RuntimeError(f"자동 보정 실패: {e}") from e
