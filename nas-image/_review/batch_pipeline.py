"""
배치 파이프라인: 폴더/파일 → 파싱 → 이미지 처리(bg_remove/correct) → 리사이즈 → 파일명 매핑(114 규칙) → 저장.
preset_id 있으면: 톤 매칭 → 보정(CLAHE+언샤프) → 크랍 → 리사이즈 → 114. 동기 함수, 워커에서 run_in_executor로 호출.
"""
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.config import get_settings
from app.parsers.folder_parser import parse_cody_folder_name
from app.utils.filename_mapper import FilenameMapper
from app.utils.image_utils import heic_to_jpg, resize_newtalk_sizes
from app.workers.auto_corrector import correct_model_shot
from app.workers.auto_crop import crop_model_shot_all_types
from app.workers.bg_remover import remove_background
from app.workers.tone_matcher import ToneMatcher, ToneStats, WhiteBalanceNormalizer

logger = logging.getLogger(__name__)

# 이미지 확장자 (소문자)
IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".heic"}


def _collect_images(path: Path) -> List[Path]:
    """경로가 디렉터리면 내부 이미지 목록, 파일이면 단일 목록 반환."""
    path = Path(path)
    if path.is_file():
        if path.suffix.lower() in IMAGE_SUFFIXES:
            return [path]
        return []
    if path.is_dir():
        return sorted(p for p in path.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES)
    return []


def _ensure_jpg(path: Path, work_dir: Path) -> Path:
    """HEIC면 JPG로 변환 후 경로 반환, 아니면 그대로."""
    if path.suffix.lower() == ".heic":
        try:
            return heic_to_jpg(path, work_dir / path.with_suffix(".jpg").name)
        except Exception as e:
            logger.warning("HEIC 변환 스킵 %s: %s", path, e)
            return path
    return path


def run_pipeline(
    source_path: str,
    mode: str,
    preset_stats: Optional[Dict[str, Any]] = None,
    match_strength: float = 0.85,
    normalize_wb: bool = True,
    wb_strength: float = 0.7,
    advanced_matching: bool = False,
    skin_protection: bool = True,
    bg_separation: bool = True,
) -> Tuple[Optional[str], Optional[str]]:
    """
    단일 경로(파일 또는 폴더)에 대해 배치 파이프라인 실행.

    preset_stats 있으면 correct 모드에서:
    화이트밸런스 정규화(normalize_wb=True 시) → 톤 매칭 → 보정 → 크랍 → 리사이즈 → 114.
    advanced_matching=True면 영역별 차등 톤 매칭(피부/배경 분리) 적용.
    없으면 기존과 동일: HEIC 변환 → bg_remove 또는 correct → 리사이즈 → 114.

    Returns:
        (output_summary, error_message). 성공 시 error_message=None.
    """
    settings = get_settings()
    processed_root = Path(settings.processed_root)
    newtalk_sizes = list(settings.newtalk_sizes)
    path = Path(source_path)

    if not path.exists():
        return None, f"경로 없음: {source_path}"

    # 이미지 목록 및 goods_code
    images = _collect_images(path)
    if not images:
        return None, "처리할 이미지가 없습니다."

    folder_name = path.name if path.is_dir() else path.parent.name
    parsed = parse_cody_folder_name(folder_name)
    goods_code = parsed.goods_code if parsed else "unknown"
    code_lower = goods_code.lower()

    base_out = processed_root / code_lower
    nobg_dir = base_out / "nobg"
    tone_matched_dir = base_out / "tone_matched"
    corrected_dir = base_out / "corrected"
    cropped_dir = base_out / "cropped"
    resize_dir = base_out / "resize"
    dir_114 = base_out / "114"
    thumb_114 = dir_114 / "thumbnail"
    thumb_114.mkdir(parents=True, exist_ok=True)
    dir_114.mkdir(parents=True, exist_ok=True)

    try:
        if mode == "bg_remove":
            nobg_paths: List[Path] = []
            for img_path in images:
                work_path = _ensure_jpg(img_path, img_path.parent)
                stem = work_path.stem
                out_jpg = nobg_dir / f"{stem}_nobg.jpg"
                nobg_dir.mkdir(parents=True, exist_ok=True)
                remove_background(work_path, out_jpg, use_photoroom=bool(get_settings().photoroom_api_key))
                nobg_paths.append(out_jpg)
                thumb_path = nobg_dir / f"thumb_{out_jpg.name}"
                if thumb_path.exists():
                    nobg_paths.append(thumb_path)
            product_jpgs = [p for p in nobg_paths if not p.name.startswith("thumb_")]
            thumbs = [p for p in nobg_paths if p.name.startswith("thumb_")]

            # 리사이즈: 제품컷(nobg) JPG 기준
            all_resized_600: List[Path] = []
            all_resized_300: List[Path] = []
            for p in product_jpgs:
                resized = resize_newtalk_sizes(p, resize_dir, sizes=newtalk_sizes)
                all_resized_600.extend(q for q in resized if q.name.endswith("_600.jpg"))
                all_resized_300.extend(q for q in resized if q.name.endswith("_300.jpg"))

            mapper = FilenameMapper(goods_code)
            for m in mapper.map_product_images(nobg_paths):
                dest = thumb_114 / m.target_filename if m.image_type == "thumbnail" else dir_114 / m.target_filename
                shutil.copy2(m.original_path, dest)
            for m in mapper.map_resize_images(all_resized_600, 600):
                shutil.copy2(m.original_path, dir_114 / m.target_filename)
            for m in mapper.map_resize_images(all_resized_300, 300):
                shutil.copy2(m.original_path, dir_114 / m.target_filename)

            summary = f"nobg={len(product_jpgs)}, 114={code_lower}, resize 600/300 적용"
            return summary, None

        elif mode == "correct":
            # 톤 매칭 프리셋 있으면: [WB 정규화] → 톤 매칭 → 보정. 없으면 원본 기준 보정.
            input_for_correct: List[Path] = []
            if preset_stats:
                tone_stats = ToneStats.from_dict(preset_stats)
                matcher = ToneMatcher()
                tone_matched_dir.mkdir(parents=True, exist_ok=True)
                if normalize_wb:
                    wb_normalizer = WhiteBalanceNormalizer()
                    wb_paths = wb_normalizer.normalize_batch(
                        [_ensure_jpg(p, p.parent) for p in images],
                        tone_matched_dir,
                        target_temp=WhiteBalanceNormalizer.TARGET_TEMP,
                        strength=wb_strength,
                    )
                    sources_for_tone = wb_paths
                else:
                    sources_for_tone = [_ensure_jpg(p, p.parent) for p in images]
                results = matcher.match_batch(
                    sources_for_tone,
                    tone_matched_dir,
                    tone_stats,
                    strength=match_strength,
                    adaptive=True,
                    use_adaptive_v2=True,
                    advanced=advanced_matching,
                    skin_protection=skin_protection,
                    bg_separation=bg_separation,
                )
                input_for_correct = [r.output_path for r in results]
            else:
                for img_path in images:
                    work_path = _ensure_jpg(img_path, img_path.parent)
                    input_for_correct.append(work_path)

            corrected_paths: List[Path] = []
            corrected_dir.mkdir(parents=True, exist_ok=True)
            for work_path in input_for_correct:
                out_path = corrected_dir / f"{work_path.stem.replace('_tone', '')}.jpg"
                correct_model_shot(work_path, out_path)
                corrected_paths.append(out_path)

            # 보정 → 크랍 (전신/상반신/반신). NAS 저사양 대비 model_complexity=1
            cropped_dir.mkdir(parents=True, exist_ok=True)
            cropped_paths: List[Path] = []
            for p in corrected_paths:
                try:
                    results = crop_model_shot_all_types(
                        p, cropped_dir, model_complexity=1
                    )
                    cropped_paths.extend(r.cropped_path for r in results)
                except Exception as e:
                    logger.warning("auto_crop 스킵 %s: %s", p, e)

            # 리사이즈: 보정본 + 크랍본
            all_resized_600: List[Path] = []
            all_resized_300: List[Path] = []
            for p in corrected_paths + cropped_paths:
                resized = resize_newtalk_sizes(p, resize_dir, sizes=newtalk_sizes)
                all_resized_600.extend(q for q in resized if q.name.endswith("_600.jpg"))
                all_resized_300.extend(q for q in resized if q.name.endswith("_300.jpg"))

            mapper = FilenameMapper(goods_code)
            for m in mapper.map_model_images(corrected_paths):
                shutil.copy2(m.original_path, dir_114 / m.target_filename)
            for m in mapper.map_resize_images(all_resized_600, 600):
                shutil.copy2(m.original_path, dir_114 / m.target_filename)
            for m in mapper.map_resize_images(all_resized_300, 300):
                shutil.copy2(m.original_path, dir_114 / m.target_filename)

            summary = (
                f"corrected={len(corrected_paths)}, cropped={len(cropped_paths)}, "
                f"114={code_lower}, resize 적용"
            )
            return summary, None

        else:
            return None, f"지원하지 않는 mode: {mode}"
    except Exception as e:
        logger.exception("batch_pipeline error: %s", source_path)
        return None, str(e)
