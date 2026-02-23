"""
MediaPipe Pose 기반 모델컷 자동 크랍.
전신(full_body), 상반신(upper_body), 반신(half_body) 크랍 타입 지원.
포즈 감지 실패 시 비율 기반 폴백 크랍.
"""
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mediapipe as mp
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

# MediaPipe Pose 랜드마크 인덱스 (PoseLandmark와 동일)
_NOSE = 0
_LEFT_SHOULDER = 11
_RIGHT_SHOULDER = 12
_LEFT_HIP = 23
_RIGHT_HIP = 24
_LEFT_KNEE = 25
_RIGHT_KNEE = 26
_LEFT_ANKLE = 27
_RIGHT_ANKLE = 28

# 최소 크랍 크기 (px). 이보다 작으면 원본 유지
MIN_CROP_PX = 300

# JPEG 저장 품질
JPEG_QUALITY = 92


@dataclass
class CropResult:
    """크랍 결과."""

    crop_type: str  # "full_body" | "upper_body" | "half_body"
    cropped_path: Path  # 저장된 파일 경로
    original_size: tuple  # (w, h)
    crop_box: tuple  # (left, top, right, bottom)
    landmarks_detected: bool


class AutoCrop:
    """MediaPipe Pose 기반 자동 크랍."""

    # 여백 비율 (크랍 영역 대비)
    MARGIN_TOP = 0.15  # 머리 위 여백
    MARGIN_BOTTOM = 0.05  # 하단 여백
    MARGIN_SIDE = 0.10  # 좌우 여백

    def __init__(self, model_complexity: int = 2) -> None:
        """
        MediaPipe Pose 초기화.

        Args:
            model_complexity: 0=라이트, 1=미디엄, 2=풀. NAS 등 저사양에서는 1 권장.
        """
        self.mp_pose = mp.solutions.pose
        self._model_complexity = min(2, max(0, model_complexity))

    def detect_pose(self, image_path: Path) -> Optional[dict[str, tuple[float, float]]]:
        """
        이미지에서 포즈 감지.

        반환: 주요 랜드마크 좌표 dict (키: nose, left_shoulder, right_shoulder 등).
        각 좌표는 (x, y) 정규화 좌표 (0~1).
        감지 실패 시 None.
        """
        image_path = Path(image_path)
        if not image_path.exists():
            logger.warning("detect_pose: 파일 없음 %s", image_path)
            return None

        try:
            pil_img = Image.open(image_path)
            pil_img = pil_img.convert("RGB")
            img_array = np.array(pil_img)
            # MediaPipe는 BGR 입력도 받지만 RGB로 동작
            h, w = img_array.shape[:2]

            with self.mp_pose.Pose(
                static_image_mode=True,
                model_complexity=self._model_complexity,
                min_detection_confidence=0.5,
            ) as pose:
                results = pose.process(img_array)

            if not results.pose_landmarks:
                return None

            lm = results.pose_landmarks.landmark
            out: dict[str, tuple[float, float]] = {}
            names_and_indices = [
                ("nose", _NOSE),
                ("left_shoulder", _LEFT_SHOULDER),
                ("right_shoulder", _RIGHT_SHOULDER),
                ("left_hip", _LEFT_HIP),
                ("right_hip", _RIGHT_HIP),
                ("left_knee", _LEFT_KNEE),
                ("right_knee", _RIGHT_KNEE),
                ("left_ankle", _LEFT_ANKLE),
                ("right_ankle", _RIGHT_ANKLE),
            ]
            for name, idx in names_and_indices:
                if idx < len(lm):
                    p = lm[idx]
                    out[name] = (float(p.x), float(p.y))
            return out if out else None
        except Exception as e:
            logger.warning("detect_pose 실패 %s: %s", image_path, e)
            return None

    def crop_full_body(
        self, image_path: Path, output_path: Path
    ) -> CropResult:
        """
        전신 크랍.
        상단: nose 위로 MARGIN_TOP, 하단: ankle 아래로 MARGIN_BOTTOM,
        좌우: shoulder 기준 MARGIN_SIDE. 실패 시 폴백.
        """
        return self._crop_by_type(image_path, output_path, "full_body")

    def crop_upper_body(
        self, image_path: Path, output_path: Path
    ) -> CropResult:
        """
        상반신 크랍.
        상단: nose 위로 MARGIN_TOP, 하단: hip 아래로 MARGIN_BOTTOM,
        좌우: shoulder 기준 MARGIN_SIDE.
        """
        return self._crop_by_type(image_path, output_path, "upper_body")

    def crop_half_body(self, image_path: Path, output_path: Path) -> CropResult:
        """
        반신 크랍.
        상단: nose 위로 MARGIN_TOP, 하단: knee 아래로 MARGIN_BOTTOM,
        좌우: shoulder 기준 MARGIN_SIDE.
        """
        return self._crop_by_type(image_path, output_path, "half_body")

    def _crop_by_type(
        self, image_path: Path, output_path: Path, crop_type: str
    ) -> CropResult:
        """공통 크랍 로직: 포즈 감지 → 박스 계산 또는 폴백 → 크랍 저장."""
        image_path = Path(image_path)
        output_path = Path(output_path)
        try:
            pil_img = Image.open(image_path)
            if pil_img.mode != "RGB":
                pil_img = pil_img.convert("RGB")
        except Exception as e:
            logger.exception("이미지 로드 실패 %s", image_path)
            raise RuntimeError(f"이미지 로드 실패: {e}") from e

        w, h = pil_img.size
        original_size = (w, h)
        landmarks = self.detect_pose(image_path)

        if landmarks:
            crop_box = self._calculate_crop_box(landmarks, original_size, crop_type)
            if crop_box:
                cw = crop_box[2] - crop_box[0]
                ch = crop_box[3] - crop_box[1]
                if cw >= MIN_CROP_PX and ch >= MIN_CROP_PX:
                    cropped = pil_img.crop(crop_box)
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    cropped.save(output_path, "JPEG", quality=JPEG_QUALITY)
                    return CropResult(
                        crop_type=crop_type,
                        cropped_path=output_path,
                        original_size=original_size,
                        crop_box=crop_box,
                        landmarks_detected=True,
                    )
        # 폴백 (이미 연 pil_img 사용)
        return self._fallback_crop(pil_img, output_path, crop_type, original_size)

    def _calculate_crop_box(
        self,
        landmarks: dict[str, tuple[float, float]],
        image_size: tuple[int, int],
        crop_type: str,
    ) -> Optional[tuple[int, int, int, int]]:
        """
        랜드마크 + 이미지 크기 → 크랍 박스 (left, top, right, bottom).
        경계 클램핑, 최소 크기 보장.
        """
        w, h = image_size
        if w <= 0 or h <= 0:
            return None

        def get_y(name: str) -> float:
            if name in landmarks:
                return landmarks[name][1]
            return 0.5

        def get_x(name: str) -> float:
            if name in landmarks:
                return landmarks[name][0]
            return 0.5

        nose_y = get_y("nose")
        l_shoulder_x = get_x("left_shoulder")
        r_shoulder_x = get_x("right_shoulder")
        shoulder_center_x = (l_shoulder_x + r_shoulder_x) / 2
        shoulder_span = abs(r_shoulder_x - l_shoulder_x) or 0.1

        if crop_type == "full_body":
            bottom_y = max(get_y("left_ankle"), get_y("right_ankle"))
        elif crop_type == "upper_body":
            bottom_y = max(get_y("left_hip"), get_y("right_hip"))
        elif crop_type == "half_body":
            bottom_y = max(get_y("left_knee"), get_y("right_knee"))
        else:
            bottom_y = 1.0

        # 정규화 좌표 → 픽셀. 상단은 nose 위 MARGIN_TOP 비율만큼
        body_height = max(0.01, bottom_y - nose_y)
        top_margin = body_height * self.MARGIN_TOP
        bottom_margin = body_height * self.MARGIN_BOTTOM
        side_margin = (shoulder_span * (1 + 2 * self.MARGIN_SIDE)) / 2
        side_margin = max(side_margin, 0.05)

        top_norm = max(0.0, nose_y - top_margin)
        bottom_norm = min(1.0, bottom_y + bottom_margin)
        left_norm = max(0.0, shoulder_center_x - side_margin)
        right_norm = min(1.0, shoulder_center_x + side_margin)

        left = int(left_norm * w)
        top = int(top_norm * h)
        right = int(right_norm * w)
        bottom = int(bottom_norm * h)

        # 경계 클램핑
        left = max(0, min(left, w - 1))
        top = max(0, min(top, h - 1))
        right = max(left + 1, min(right, w))
        bottom = max(top + 1, min(bottom, h))

        # 최소 크기
        if right - left < MIN_CROP_PX:
            mid_x = (left + right) // 2
            left = max(0, mid_x - MIN_CROP_PX // 2)
            right = min(w, left + MIN_CROP_PX)
            if right - left < MIN_CROP_PX:
                right = min(w, left + MIN_CROP_PX)
        if bottom - top < MIN_CROP_PX:
            mid_y = (top + bottom) // 2
            top = max(0, mid_y - MIN_CROP_PX // 2)
            bottom = min(h, top + MIN_CROP_PX)
            if bottom - top < MIN_CROP_PX:
                bottom = min(h, top + MIN_CROP_PX)

        return (left, top, right, bottom)

    def _fallback_crop(
        self,
        pil_img: Image.Image,
        output_path: Path,
        crop_type: str,
        original_size: tuple[int, int],
    ) -> CropResult:
        """
        포즈 감지 실패 시 폴백.
        full_body: 원본 그대로(상하 10% 여백 제거).
        upper_body: 상단 60% 크랍.
        half_body: 상단 75% 크랍.
        """
        w, h = pil_img.size
        if crop_type == "full_body":
            # 상하 10% 여백 제거
            top = int(h * 0.10)
            bottom = int(h * 0.90)
            left = 0
            right = w
        elif crop_type == "upper_body":
            # 상단 60%
            left, top = 0, 0
            right, bottom = w, int(h * 0.60)
        else:  # half_body
            # 상단 75%
            left, top = 0, 0
            right, bottom = w, int(h * 0.75)

        crop_box = (left, top, right, bottom)
        cropped = pil_img.crop(crop_box)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cropped.save(output_path, "JPEG", quality=JPEG_QUALITY)
        return CropResult(
            crop_type=crop_type,
            cropped_path=output_path,
            original_size=original_size,
            crop_box=crop_box,
            landmarks_detected=False,
        )

    def crop_all_types(
        self, image_path: Path, output_dir: Path
    ) -> list[CropResult]:
        """
        한 이미지에서 전신/상반신/반신 세 가지 크랍 모두 생성.
        output_dir 하위에 {원본이름}_full.jpg, _upper.jpg, _half.jpg 저장.
        """
        image_path = Path(image_path)
        output_dir = Path(output_dir)
        stem = image_path.stem
        results: list[CropResult] = []
        for crop_type, suffix in [
            ("full_body", "full"),
            ("upper_body", "upper"),
            ("half_body", "half"),
        ]:
            out_path = output_dir / f"{stem}_{suffix}.jpg"
            res = self._crop_by_type(image_path, out_path, crop_type)
            results.append(res)
        return results


def crop_model_shot_all_types(
    image_path: Path,
    output_dir: Path,
    model_complexity: int = 1,
) -> list[CropResult]:
    """
    배치 파이프라인용 헬퍼.
    한 모델컷 이미지에 대해 전신/상반신/반신 크랍을 생성한다.

    Args:
        image_path: 원본 이미지 경로
        output_dir: 크랍 결과 저장 디렉터리 (cropped/)
        model_complexity: NAS 등에서는 1 권장

    Returns:
        CropResult 리스트 (full, upper, half 순)
    """
    cropper = AutoCrop(model_complexity=model_complexity)
    return cropper.crop_all_types(image_path, output_dir)
