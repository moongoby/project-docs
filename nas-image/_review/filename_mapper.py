"""
NAS _processed/ 출력 파일명을 114서버 규칙에 맞게 변환하는 모듈.
folder_parser의 goods_code를 받아 사용하며, sync/rsync_114에서 MappedFile 목록으로 전송에 사용.
"""
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

ImageType = Literal["product", "model", "resize_600", "resize_300", "thumbnail"]

# 114서버 이미지 베이스 경로
PATH_114_BASE = "/home/danharoo/www/data/files/goods/goodscode/img"


@dataclass
class MappedFile:
    """변환된 파일 정보."""

    original_path: Path
    target_filename: str
    target_dir: str
    image_type: str


class FilenameMapper:
    """NAS 출력 파일명 → 114서버 규칙 변환."""

    def __init__(self, goods_code: str) -> None:
        """
        goods_code: folder_parser에서 추출한 상품코드.
        내부적으로 소문자로 변환하여 사용.
        """
        self._code = goods_code.lower()

    def map_product_images(self, file_paths: list[Path]) -> list[MappedFile]:
        """
        제품컷 파일 목록 → 114 규칙 매핑.

        - _nobg.png, _nobg.jpg 파일을 {코드}_01.jpg ~ _15.jpg 순번 부여
        - thumb_ 접두사 파일은 thumbnail 타입으로 분류
        - -Photoroom 접미사 파일은 스킵 (수동 누끼)
        """
        result: list[MappedFile] = []
        paths = [Path(p) for p in file_paths]

        # -Photoroom 제외
        def skip_photoroom(p: Path) -> bool:
            return "-Photoroom" in p.stem

        # 썸네일 / 제품컷 분리
        thumb_paths = sorted(p for p in paths if p.name.startswith("thumb_") and not skip_photoroom(p))
        product_paths = sorted(
            p for p in paths if not p.name.startswith("thumb_") and not skip_photoroom(p)
        )

        # 제품컷: _nobg 등 → _01.jpg ~ _15.jpg (최대 15장, 2자리 제로패딩)
        for i, p in enumerate(product_paths[:15], start=1):
            result.append(
                MappedFile(
                    original_path=p,
                    target_filename=f"{self._code}_{i:02d}.jpg",
                    target_dir=self._code,
                    image_type="product",
                )
            )

        # 썸네일: thumbnail 폴더용 파일명
        for i, p in enumerate(thumb_paths, start=1):
            result.append(
                MappedFile(
                    original_path=p,
                    target_filename=f"{self._code}_thumb_{i}.jpg",
                    target_dir=self._code,
                    image_type="thumbnail",
                )
            )

        return result

    def map_model_images(self, file_paths: list[Path]) -> list[MappedFile]:
        """
        모델컷 파일 목록 → 114 규칙 매핑.

        - 보정된 jpg 파일을 {코드}-s_1.jpg, -s_2.jpg ... 순번 부여
        - 파일명 정렬 후 순번 부여 (IMG_3473.jpg → IMG_3474.jpg 순서 유지)
        """
        paths = sorted(Path(p) for p in file_paths)
        result: list[MappedFile] = []
        for i, p in enumerate(paths, start=1):
            result.append(
                MappedFile(
                    original_path=p,
                    target_filename=f"{self._code}-s_{i}.jpg",
                    target_dir=self._code,
                    image_type="model",
                )
            )
        return result

    def map_resize_images(self, file_paths: list[Path], size: int) -> list[MappedFile]:
        """
        리사이즈 파일 목록 → 114 규칙 매핑.

        - size=600: {코드}-600_1.jpg, -600_2.jpg ...
        - size=300: {코드}-300_1.jpg, -300_2.jpg ...
        """
        paths = sorted(Path(p) for p in file_paths)
        image_type: str = "resize_600" if size == 600 else "resize_300"
        result: list[MappedFile] = []
        for i, p in enumerate(paths, start=1):
            result.append(
                MappedFile(
                    original_path=p,
                    target_filename=f"{self._code}-{size}_{i}.jpg",
                    target_dir=self._code,
                    image_type=image_type,
                )
            )
        return result

    def get_target_dir(self) -> str:
        """114서버 대상 디렉터리명 반환 (소문자 상품코드)."""
        return self._code

    def get_114_path(self, mapped_file: MappedFile) -> str:
        """
        114서버 전체 경로 반환.

        형식: /home/danharoo/www/data/files/goods/goodscode/img/{소문자코드}/{파일명}
        썸네일: .../img/{소문자코드}/thumbnail/{파일명}
        """
        base = f"{PATH_114_BASE}/{self._code}"
        if mapped_file.image_type == "thumbnail":
            return f"{base}/thumbnail/{mapped_file.target_filename}"
        return f"{base}/{mapped_file.target_filename}"
