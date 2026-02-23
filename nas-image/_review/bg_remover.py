"""
PhotoRoom API로 배경 제거 후 흰 배경 합성 및 썸네일 생성.
PhotoRoom 실패 시 rembg 폴백.
"""
import http.client
import logging
import mimetypes
import os
import uuid
from io import BytesIO
from pathlib import Path
from typing import Optional

from PIL import Image

logger = logging.getLogger(__name__)

PHOTOROOM_API_KEY = os.getenv("PHOTOROOM_API_KEY", "")
PHOTOROOM_HOST = "sdk.photoroom.com"
PHOTOROOM_ENDPOINT = "/v1/segment"


def _remove_bg_photoroom(image_data: bytes, filename: str) -> bytes:
    """PhotoRoom API로 배경 제거. 실패 시 예외 발생."""
    if not PHOTOROOM_API_KEY:
        raise RuntimeError("PHOTOROOM_API_KEY 환경변수가 설정되지 않았습니다.")

    boundary = "----------{}".format(uuid.uuid4().hex)
    content_type, _ = mimetypes.guess_type(filename)
    if content_type is None:
        content_type = "application/octet-stream"

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image_file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode("utf-8") + image_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    conn = http.client.HTTPSConnection(PHOTOROOM_HOST, timeout=30)
    headers = {
        "Content-Type": f"multipart/form-data; boundary={boundary}",
        "x-api-key": PHOTOROOM_API_KEY,
    }

    try:
        conn.request("POST", PHOTOROOM_ENDPOINT, body=body, headers=headers)
        response = conn.getresponse()
        response_data = response.read()

        if response.status == 200:
            logger.info("PhotoRoom API 성공: %s", filename)
            return response_data
        else:
            raise RuntimeError(
                f"PhotoRoom API 에러: {response.status} {response.reason}"
            )
    finally:
        conn.close()


def _remove_bg_rembg(image_data: bytes) -> bytes:
    """rembg 폴백: 로컬 CPU로 배경 제거."""
    from rembg import remove

    logger.info("rembg 폴백 사용")
    return remove(image_data)


def remove_background(
    input_path: Path,
    output_path: Path,
    thumbnail_size: Optional[tuple[int, int]] = (300, 300),
    use_photoroom: bool = True,
    save_transparent: bool = False,
) -> None:
    """
    입력 이미지 배경 제거 후 저장.

    - use_photoroom=True: PhotoRoom API 사용, 실패 시 rembg 폴백
    - save_transparent=True: 투명 배경 PNG 저장
    - save_transparent=False: 흰 배경 JPG 저장 (기본)
    """
    try:
        with open(input_path, "rb") as f:
            data = f.read()

        filename = input_path.name

        # 1차: PhotoRoom API
        if use_photoroom and PHOTOROOM_API_KEY:
            try:
                out_data = _remove_bg_photoroom(data, filename)
            except Exception as e:
                logger.warning("PhotoRoom 실패, rembg 폴백: %s", e)
                out_data = _remove_bg_rembg(data)
        else:
            out_data = _remove_bg_rembg(data)

        img = Image.open(BytesIO(out_data)).convert("RGBA")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if save_transparent:
            # 투명 배경 PNG
            output_png = output_path.with_suffix(".png")
            img.save(output_png, "PNG")
        else:
            # 흰 배경 JPG
            w, h = img.size
            bg = Image.new("RGB", (w, h), (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            bg.save(output_path, "JPEG", quality=92)

            # 썸네일
            if thumbnail_size:
                thumb = bg.copy()
                thumb.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                thumb_path = output_path.parent / f"thumb_{output_path.name}"
                thumb.save(thumb_path, "JPEG", quality=85)

        logger.info("배경 제거 완료: %s -> %s", input_path, output_path)

    except Exception as e:
        logger.exception("bg_remover error: %s", input_path)
        raise RuntimeError(f"배경 제거 실패: {e}") from e
