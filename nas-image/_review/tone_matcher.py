"""
프리셋 기반 톤 매칭 엔진. L채널 중심 매칭으로 의류 색상을 보호하면서 전체 톤을 맞춤.
영역별 차등 매칭: 피부톤 보호(skin_mask), 배경 분리(person_mask) 지원.
"""
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from PIL import Image, ImageOps

logger = logging.getLogger(__name__)

# MediaPipe Pose: advanced 매칭 시에만 사용 (지연 임포트로 초기 부하 완화)
def _get_pose():
    import mediapipe as mp
    return mp.solutions.pose


@dataclass
class ToneStats:
    """이미지 LAB 톤 통계."""
    l_mean: float
    l_std: float
    a_mean: float
    a_std: float
    b_mean: float
    b_std: float
    color_temp: float  # B 채널 평균 (색온도)
    saturation: float  # A,B 표준편차 기반 채도

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ToneStats":
        return cls(
            l_mean=float(d["l_mean"]),
            l_std=float(d["l_std"]),
            a_mean=float(d["a_mean"]),
            a_std=float(d["a_std"]),
            b_mean=float(d["b_mean"]),
            b_std=float(d["b_std"]),
            color_temp=float(d["color_temp"]),
            saturation=float(d["saturation"]),
        )


@dataclass
class MatchResult:
    """톤 매칭 결과."""
    output_path: Path
    preset_id: Optional[int]
    match_strength: float
    original_stats: ToneStats
    result_stats: ToneStats
    warning: Optional[str] = None  # 경고 메시지 (프리셋과 차이 클 때)
    distance: float = 0.0  # 프리셋과의 다차원 거리


class ToneMatcher:
    """LAB 기반 톤 매칭. L채널 중심, protect_colors 시 A/B 약하게 적용."""

    def analyze_image(self, path: Path) -> ToneStats:
        """
        이미지 LAB 변환 후 채널별 평균/표준편차, 색온도(B평균), 채도(A,B 표준편차) 반환.
        """
        path = Path(path)
        pil_img = Image.open(path)
        pil_img = ImageOps.exif_transpose(pil_img)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        img = np.array(pil_img)
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)

        l_mean = float(np.mean(l_ch))
        l_std = float(np.std(l_ch)) or 1e-6
        a_mean = float(np.mean(a_ch))
        a_std = float(np.std(a_ch)) or 1e-6
        b_mean = float(np.mean(b_ch))
        b_std = float(np.std(b_ch)) or 1e-6
        color_temp = b_mean
        saturation = float(np.sqrt(a_std ** 2 + b_std ** 2))

        return ToneStats(
            l_mean=l_mean,
            l_std=l_std,
            a_mean=a_mean,
            a_std=a_std,
            b_mean=b_mean,
            b_std=b_std,
            color_temp=color_temp,
            saturation=saturation,
        )

    def match_tone(
        self,
        image_path: Path,
        output_path: Path,
        preset_stats: ToneStats,
        strength: float = 0.85,
        protect_colors: bool = True,
    ) -> MatchResult:
        """
        원본 LAB에 프리셋 톤 적용.
        L채널: (원본L - 원본L평균) × (프리셋Lstd/원본Lstd) + 프리셋L평균
        protect_colors=True면 A,B는 strength×0.25로 약하게.
        result = 원본×(1-strength) + 매칭×strength, L 클램핑 10~245, JPEG 92.
        """
        image_path = Path(image_path)
        output_path = Path(output_path)
        pil_img = Image.open(image_path)
        pil_img = ImageOps.exif_transpose(pil_img)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        img = np.array(pil_img)
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)
        orig = self.analyze_image(image_path)

        orig_l_std = orig.l_std or 1e-6
        matched_l = (l_ch.astype(np.float32) - orig.l_mean) * (preset_stats.l_std / orig_l_std) + preset_stats.l_mean

        ab_strength = strength * 0.25 if protect_colors else strength
        orig_a_std = orig.a_std or 1e-6
        orig_b_std = orig.b_std or 1e-6
        matched_a = (a_ch.astype(np.float32) - orig.a_mean) * (preset_stats.a_std / orig_a_std) + preset_stats.a_mean
        matched_b = (b_ch.astype(np.float32) - orig.b_mean) * (preset_stats.b_std / orig_b_std) + preset_stats.b_mean

        out_l = (l_ch.astype(np.float32) * (1 - strength) + matched_l * strength)
        out_a = (a_ch.astype(np.float32) * (1 - ab_strength) + matched_a * ab_strength)
        out_b = (b_ch.astype(np.float32) * (1 - ab_strength) + matched_b * ab_strength)

        out_l = np.clip(out_l, 10.0, 245.0)
        out_a = np.clip(out_a, 0, 255)
        out_b = np.clip(out_b, 0, 255)

        lab_out = cv2.merge([out_l.astype(np.uint8), out_a.astype(np.uint8), out_b.astype(np.uint8)])
        bgr_out = cv2.cvtColor(lab_out, cv2.COLOR_LAB2BGR)
        result_rgb = cv2.cvtColor(bgr_out, cv2.COLOR_BGR2RGB)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(result_rgb).save(output_path, "JPEG", quality=92)

        result_stats = ToneStats(
            l_mean=float(np.mean(out_l)),
            l_std=float(np.std(out_l)) or 1e-6,
            a_mean=float(np.mean(out_a)),
            a_std=float(np.std(out_a)) or 1e-6,
            b_mean=float(np.mean(out_b)),
            b_std=float(np.std(out_b)) or 1e-6,
            color_temp=float(np.mean(out_b)),
            saturation=float(np.sqrt(np.std(out_a) ** 2 + np.std(out_b) ** 2)),
        )
        return MatchResult(
            output_path=output_path,
            preset_id=None,
            match_strength=strength,
            original_stats=orig,
            result_stats=result_stats,
            warning=None,
            distance=0.0,
        )

    def detect_skin_mask(self, image_bgr: np.ndarray) -> np.ndarray:
        """
        HSV 색공간에서 피부톤 영역 마스크를 생성한다.

        1. BGR → HSV 변환
        2. 피부톤 범위 (경험적 값):
           H: 0~50 (빨강~주황~노랑 범위)
           S: 40~200 (너무 낮으면 흰색/회색, 너무 높으면 과채도)
           V: 80~255 (너무 어두운 영역 제외)
        3. inRange로 마스크 생성
        4. 모폴로지 연산으로 노이즈 제거:
           - erode (3x3, 1회) → 작은 잡음 제거
           - dilate (5x5, 2회) → 피부 영역 확장
        5. GaussianBlur (21x21) → 마스크 경계 부드럽게 (페더링)
        6. 0~1 float 마스크로 정규화하여 반환
        """
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 40, 80], dtype=np.uint8)
        upper = np.array([50, 200, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower, upper)
        kernel_erode = np.ones((3, 3), np.uint8)
        mask = cv2.erode(mask, kernel_erode, iterations=1)
        kernel_dilate = np.ones((5, 5), np.uint8)
        mask = cv2.dilate(mask, kernel_dilate, iterations=2)
        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        mask_float = mask.astype(np.float32) / 255.0
        return mask_float

    def detect_person_mask(self, image_bgr: np.ndarray) -> np.ndarray:
        """
        MediaPipe Pose를 활용하여 인물 영역 마스크를 생성한다.

        1. MediaPipe Pose로 랜드마크 감지
        2. 랜드마크가 감지되면:
           - 모든 랜드마크의 min_x, min_y, max_x, max_y 계산
           - 여백 추가 (상하좌우 15%)
           - 해당 바운딩 박스를 인물 영역으로 마스크 생성
        3. 랜드마크 감지 실패 시:
           - 이미지 중앙 60% 영역을 인물로 가정 (폴백)
        4. GaussianBlur로 경계 페더링
        5. 0~1 float 마스크로 반환
        """
        h, w = image_bgr.shape[:2]
        rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        mask = np.zeros((h, w), dtype=np.float32)
        try:
            mp_pose = _get_pose()
            with mp_pose.Pose(
                static_image_mode=True,
                model_complexity=1,
                min_detection_confidence=0.5,
            ) as pose:
                results = pose.process(rgb)
            if results.pose_landmarks:
                lm = results.pose_landmarks.landmark
                xs = [p.x for p in lm]
                ys = [p.y for p in lm]
                min_x = max(0.0, min(xs) - 0.15)
                max_x = min(1.0, max(xs) + 0.15)
                min_y = max(0.0, min(ys) - 0.15)
                max_y = min(1.0, max(ys) + 0.15)
                x1 = int(min_x * w)
                y1 = int(min_y * h)
                x2 = int(max_x * w)
                y2 = int(max_y * h)
                x1 = max(0, min(x1, w - 1))
                y1 = max(0, min(y1, h - 1))
                x2 = max(x1 + 1, min(x2, w))
                y2 = max(y1 + 1, min(y2, h))
                mask[y1:y2, x1:x2] = 1.0
            else:
                # 폴백: 중앙 60%
                x1 = int(w * 0.2)
                y1 = int(h * 0.2)
                x2 = int(w * 0.8)
                y2 = int(h * 0.8)
                mask[y1:y2, x1:x2] = 1.0
        except Exception as e:
            logger.warning("detect_person_mask 실패, 폴백 적용: %s", e)
            x1 = int(w * 0.2)
            y1 = int(h * 0.2)
            x2 = int(w * 0.8)
            y2 = int(h * 0.8)
            mask[y1:y2, x1:x2] = 1.0
        mask = cv2.GaussianBlur(mask, (21, 21), 0)
        mask = np.clip(mask, 0.0, 1.0).astype(np.float32)
        return mask

    def match_tone_advanced(
        self,
        image_path: Path,
        output_path: Path,
        preset_stats: ToneStats,
        strength: float = 0.85,
        use_skin_protection: bool = True,
        use_background_separation: bool = True,
    ) -> MatchResult:
        """
        영역별 차등 톤 매칭.

        의류: L 85%, A/B 20%. 피부: L 30%, A/B 10%. 배경: L 50%, A/B 0%.
        use_skin_protection=False면 피부도 의류와 동일 강도.
        use_background_separation=False면 배경도 의류와 동일 강도.
        """
        image_path = Path(image_path)
        output_path = Path(output_path)
        pil_img = Image.open(image_path)
        pil_img = ImageOps.exif_transpose(pil_img)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        img = np.array(pil_img)
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        orig = self.analyze_image(image_path)

        skin_mask = self.detect_skin_mask(bgr)
        person_mask = self.detect_person_mask(bgr)
        clothing_mask = np.clip(person_mask - skin_mask, 0.0, 1.0).astype(np.float32)
        background_mask = (1.0 - person_mask).astype(np.float32)

        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)
        l_f = l_ch.astype(np.float32)
        a_f = a_ch.astype(np.float32)
        b_f = b_ch.astype(np.float32)

        orig_l_std = orig.l_std or 1e-6
        matched_l = (l_f - orig.l_mean) * (preset_stats.l_std / orig_l_std) + preset_stats.l_mean
        ab_strength = strength * 0.25
        orig_a_std = orig.a_std or 1e-6
        orig_b_std = orig.b_std or 1e-6
        matched_a = (a_f - orig.a_mean) * (preset_stats.a_std / orig_a_std) + preset_stats.a_mean
        matched_b = (b_f - orig.b_mean) * (preset_stats.b_std / orig_b_std) + preset_stats.b_mean

        # 기본 매칭 결과 (의류: L strength, A/B ab_strength)
        out_cloth_l = l_f * (1 - strength) + matched_l * strength
        out_cloth_a = a_f * (1 - ab_strength) + matched_a * ab_strength
        out_cloth_b = b_f * (1 - ab_strength) + matched_b * ab_strength

        # 피부: L 30%, A/B 10% (원본 비중 높음)
        skin_l_blend = 0.3
        skin_ab_blend = 0.1
        out_skin_l = l_f * (1 - skin_l_blend) + matched_l * skin_l_blend if use_skin_protection else out_cloth_l
        out_skin_a = a_f * (1 - skin_ab_blend) + matched_a * skin_ab_blend if use_skin_protection else out_cloth_a
        out_skin_b = b_f * (1 - skin_ab_blend) + matched_b * skin_ab_blend if use_skin_protection else out_cloth_b

        # 배경: L 50%, A/B 원본 유지
        if use_background_separation:
            out_bg_l = l_f * 0.5 + matched_l * 0.5
            out_bg_a = a_f
            out_bg_b = b_f
        else:
            out_bg_l = out_cloth_l
            out_bg_a = out_cloth_a
            out_bg_b = out_cloth_b

        out_l = out_cloth_l * clothing_mask + out_skin_l * skin_mask + out_bg_l * background_mask
        out_a = out_cloth_a * clothing_mask + out_skin_a * skin_mask + out_bg_a * background_mask
        out_b = out_cloth_b * clothing_mask + out_skin_b * skin_mask + out_bg_b * background_mask

        out_l = np.clip(out_l, 10.0, 245.0)
        out_a = np.clip(out_a, 0, 255)
        out_b = np.clip(out_b, 0, 255)

        lab_out = cv2.merge([out_l.astype(np.uint8), out_a.astype(np.uint8), out_b.astype(np.uint8)])
        bgr_out = cv2.cvtColor(lab_out, cv2.COLOR_LAB2BGR)
        result_rgb = cv2.cvtColor(bgr_out, cv2.COLOR_BGR2RGB)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(result_rgb).save(output_path, "JPEG", quality=92)

        result_stats = ToneStats(
            l_mean=float(np.mean(out_l)),
            l_std=float(np.std(out_l)) or 1e-6,
            a_mean=float(np.mean(out_a)),
            a_std=float(np.std(out_a)) or 1e-6,
            b_mean=float(np.mean(out_b)),
            b_std=float(np.std(out_b)) or 1e-6,
            color_temp=float(np.mean(out_b)),
            saturation=float(np.sqrt(np.std(out_a) ** 2 + np.std(out_b) ** 2)),
        )
        return MatchResult(
            output_path=output_path,
            preset_id=None,
            match_strength=strength,
            original_stats=orig,
            result_stats=result_stats,
            warning=None,
            distance=0.0,
        )

    def _adaptive_strength(self, original: ToneStats, preset: ToneStats, base: float) -> float:
        """거리 = |L평균차이| + |색온도차이|×0.5. 0.3~0.95."""
        dist = abs(original.l_mean - preset.l_mean) + abs(original.color_temp - preset.color_temp) * 0.5
        strength = base + (0.95 - base) * min(dist / 50.0, 1.0)
        return float(np.clip(strength, 0.3, 0.95))

    def _adaptive_strength_v2(
        self,
        original: ToneStats,
        preset: ToneStats,
        base_strength: float = 0.85,
    ) -> tuple[float, bool, float]:
        """
        다차원 거리 기반 적응형 강도 v2.

        1. 밝기 거리: |original.l_mean - preset.l_mean| / 255
        2. 색온도 거리: |original.color_temp - preset.color_temp| / 50
        3. 채도 거리: |original.saturation - preset.saturation| / 1.0
        4. 대비 거리: |original.l_std - preset.l_std| / 50

        종합 거리 = 밝기×0.4 + 색온도×0.3 + 채도×0.15 + 대비×0.15

        거리 → 강도 매핑:
        - 거리 < 0.1 (매우 유사): base × 0.4 (최소 보정)
        - 거리 0.1~0.3 (약간 다름): base × 0.6~0.8
        - 거리 0.3~0.5 (많이 다름): base × 0.8~1.0
        - 거리 > 0.5 (극단 차이): base × 1.0 + 경고 플래그

        반환: (adjusted_strength, warning_flag, distance)
        """
        d_l = min(abs(original.l_mean - preset.l_mean) / 255.0, 1.0)
        d_temp = min(abs(original.color_temp - preset.color_temp) / 50.0, 1.0)
        sat_scale = max(abs(preset.saturation), 50.0)
        d_sat = min(abs(original.saturation - preset.saturation) / sat_scale, 1.0)
        d_std = min(abs(original.l_std - preset.l_std) / 50.0, 1.0)
        distance = d_l * 0.4 + d_temp * 0.3 + d_sat * 0.15 + d_std * 0.15
        distance = min(distance, 1.0)

        if distance < 0.1:
            factor = 0.4
        elif distance < 0.3:
            factor = 0.6 + (distance - 0.1) / 0.2 * 0.2  # 0.6 ~ 0.8
        elif distance < 0.5:
            factor = 0.8 + (distance - 0.3) / 0.2 * 0.2  # 0.8 ~ 1.0
        else:
            factor = 1.0

        adjusted = float(np.clip(base_strength * factor, 0.3, 0.95))
        warning_flag = distance > 0.5
        return adjusted, warning_flag, distance

    def match_batch(
        self,
        image_paths: List[Path],
        output_dir: Path,
        preset_stats: ToneStats,
        strength: float = 0.85,
        adaptive: bool = True,
        use_adaptive_v2: bool = True,
        advanced: bool = False,
        skin_protection: bool = True,
        bg_separation: bool = True,
    ) -> List[MatchResult]:
        """여러 이미지 톤 매칭. advanced=True면 match_tone_advanced(영역별 차등)."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        results: List[MatchResult] = []
        for img_path in image_paths:
            out_path = output_dir / f"{img_path.stem}_tone.jpg"
            if advanced:
                res = self.match_tone_advanced(
                    img_path,
                    out_path,
                    preset_stats,
                    strength=strength,
                    use_skin_protection=skin_protection,
                    use_background_separation=bg_separation,
                )
                results.append(res)
            else:
                s = strength
                warning_msg: Optional[str] = None
                distance = 0.0
                if adaptive:
                    orig = self.analyze_image(img_path)
                    if use_adaptive_v2:
                        s, warning_flag, distance = self._adaptive_strength_v2(orig, preset_stats, strength)
                        if warning_flag:
                            warning_msg = "이 이미지는 프리셋과 차이가 커서 수동 확인 권장"
                    else:
                        s = self._adaptive_strength(orig, preset_stats, strength)
                res = self.match_tone(img_path, out_path, preset_stats, strength=s, protect_colors=True)
                res.warning = warning_msg
                res.distance = distance
                results.append(res)
        return results


class WhiteBalanceNormalizer:
    """촬영 시 색온도 차이를 정규화하는 전처리기. Gray World 전체 중립이 아닌 LAB B 부분 조정."""

    TARGET_TEMP = 5500  # 일광 기준 색온도 (K)

    def estimate_color_temperature(self, image_bgr: np.ndarray) -> float:
        """
        이미지의 색온도를 추정한다.

        방법: Gray World 가정의 개선 버전
        1. 이미지를 LAB 변환
        2. B채널(청-황) 평균으로 색온도 추정
           B평균 > 128: 차가운 톤 (높은 색온도, 흐린 날/그늘)
           B평균 < 128: 따뜻한 톤 (낮은 색온도, 석양/실내)
        3. A채널(녹-적) 평균으로 보정
        4. 대략적 색온도(K) 반환. 상대 비교용.
        """
        lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
        _, a_ch, b_ch = cv2.split(lab)
        b_mean = float(np.mean(b_ch))
        a_mean = float(np.mean(a_ch))
        # LAB: L 0~255, A 0~255(128 중립), B 0~255(128 중립).
        # OpenCV LAB에서 B가 크면 황/적(따뜻함), B가 작으면 청(차가움). 따라서 B 높음 → 낮은 색온도.
        temp_k = 5500.0 - (b_mean - 128.0) * 50.0 + (128.0 - a_mean) * 5.0
        return max(2500.0, min(10000.0, temp_k))

    def _estimate_from_neutral_regions(self, image_bgr: np.ndarray) -> Optional[float]:
        """
        무채색(회색/흰색) 영역을 찾아 색온도를 추정한다.

        1. HSV 변환
        2. 채도(S) < 30인 영역 추출 (무채색)
        3. 무채색 영역이 전체의 5% 미만이면 None (추정 불가, 정규화 스킵)
        4. 무채색 영역의 RGB 평균으로 색온도 추정: R > B 따뜻함, B > R 차가움
        """
        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        _, s_ch, _ = cv2.split(hsv)
        neutral_mask = s_ch < 30
        neutral_ratio = float(np.sum(neutral_mask)) / neutral_mask.size
        if neutral_ratio < 0.05:
            return None
        pixels = image_bgr[neutral_mask]
        if len(pixels) == 0:
            return None
        b_mean = float(np.mean(pixels[:, 0]))
        g_mean = float(np.mean(pixels[:, 1]))
        r_mean = float(np.mean(pixels[:, 2]))
        # BGR 순. R > B 이면 따뜻(낮은 색온도), B > R 이면 차가움(높은 색온도)
        # b_mean - r_mean: 양수면 차가움 → 높은 K, 음수면 따뜻함 → 낮은 K
        if r_mean + b_mean < 1e-6:
            return 5500.0
        offset = (b_mean - r_mean) * 40.0
        return 5500.0 + offset

    def normalize_white_balance(
        self,
        image_path: Path,
        output_path: Path,
        target_temp: Optional[float] = None,
        strength: float = 0.7,
    ) -> Path:
        """
        색온도를 목표값으로 정규화한다.

        1. 원본 색온도 추정 (무채색 영역 우선, 없으면 전체 LAB B평균)
        2. 목표 색온도와의 차이 계산
        3. LAB 공간에서 B채널 조정, strength로 강도 제어. A채널 30% 비율 미세 조정
        4. JPEG quality=92 저장
        """
        image_path = Path(image_path)
        output_path = Path(output_path)
        pil_img = Image.open(image_path)
        pil_img = ImageOps.exif_transpose(pil_img)
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")
        img = np.array(pil_img)
        bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
        l_ch, a_ch, b_ch = cv2.split(lab)

        est = self._estimate_from_neutral_regions(bgr)
        if est is None:
            est = self.estimate_color_temperature(bgr)
        target = target_temp if target_temp is not None else float(self.TARGET_TEMP)
        # 원본이 차가우면(est > target) B를 올려 따뜻하게; 따뜻하면(est < target) B를 내려 차갑게.
        diff = est - target  # 양수: 원본 차가움 → B 증가(따뜻하게). 음수: 원본 따뜻함 → B 감소(차갑게).
        shift_b = (diff / 50.0) * strength
        shift_a = shift_b * 0.3
        out_b = np.clip(b_ch.astype(np.float32) + shift_b, 0, 255)
        out_a = np.clip(a_ch.astype(np.float32) + shift_a, 0, 255)
        lab_out = cv2.merge([l_ch, out_a.astype(np.uint8), out_b.astype(np.uint8)])
        bgr_out = cv2.cvtColor(lab_out, cv2.COLOR_LAB2BGR)
        result_rgb = cv2.cvtColor(bgr_out, cv2.COLOR_BGR2RGB)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(result_rgb).save(output_path, "JPEG", quality=92)
        return output_path

    def normalize_batch(
        self,
        image_paths: List[Path],
        output_dir: Path,
        target_temp: Optional[float] = None,
        strength: float = 0.7,
    ) -> List[Path]:
        """배치 화이트밸런스 정규화. 추정 불가 이미지는 스킵 후 원본 복사."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        result_paths: List[Path] = []
        for img_path in image_paths:
            out_path = output_dir / f"{img_path.stem}_wb.jpg"
            try:
                self.normalize_white_balance(img_path, out_path, target_temp=target_temp, strength=strength)
                result_paths.append(out_path)
            except Exception as e:
                logger.warning("WB 정규화 스킵 %s: %s", img_path, e)
                import shutil
                shutil.copy2(img_path, out_path)
                result_paths.append(out_path)
        return result_paths
