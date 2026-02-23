"""
QC UI 라우트: 세션 목록, 비교 슬라이더 페이지, 이미지 서빙.
"""
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.parsers.folder_parser import parse_cody_folder_name
from app.qc.image_resolver import (
    get_session_display_info,
    resolve_qc_images,
)
from app.queue.job_manager import get_job_by_goods_code, get_job_status, list_sessions

logger = logging.getLogger(__name__)
router = APIRouter(tags=["qc"])


def _templates() -> Jinja2Templates:
    """템플릿 디렉터리 (app/templates)."""
    return Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))


@router.get("/qc/presets", response_class=HTMLResponse)
async def qc_presets_list_page(request: Request) -> HTMLResponse:
    """톤 프리셋 목록 페이지."""
    templates = _templates()
    return templates.TemplateResponse(request, "preset_list.html", {"request": request})


@router.get("/qc/presets/register", response_class=HTMLResponse)
async def qc_presets_register_page(request: Request) -> HTMLResponse:
    """톤 프리셋 등록 페이지."""
    templates = _templates()
    return templates.TemplateResponse(request, "preset_register.html", {"request": request})


@router.get("/qc/presets/{preset_id}/edit", response_class=HTMLResponse)
async def qc_presets_edit_page(request: Request, preset_id: str) -> HTMLResponse:
    """톤 프리셋 수정 페이지 (등록 폼과 동일 레이아웃, preset_id 전달)."""
    templates = _templates()
    return templates.TemplateResponse(
        request,
        "preset_register.html",
        {"request": request, "preset_id": preset_id, "is_edit": True},
    )


@router.get("/qc/classify", response_class=HTMLResponse)
async def qc_classify_page(request: Request, folder: Optional[str] = None) -> HTMLResponse:
    """폴더 자동 분류 페이지. ?folder= 경로 전달."""
    templates = _templates()
    return templates.TemplateResponse(
        request,
        "classify.html",
        {"request": request, "folder_path": folder or ""},
    )


@router.get("/qc", response_class=HTMLResponse)
async def qc_list_page(request: Request) -> HTMLResponse:
    """세션 목록 페이지."""
    items = await list_sessions()
    settings = get_settings()
    sessions = []
    for x in items:
        try:
            info = get_session_display_info(
                job_id=x["job_id"],
                source_path=x.get("source_path") or "",
                status=x.get("status") or "unknown",
                created_at=x.get("created_at"),
                mode=x.get("mode") or "bg_remove",
            )
            sessions.append(info)
        except Exception as e:
            logger.warning("session display info skip %s: %s", x.get("job_id"), e)
    templates = _templates()
    return templates.TemplateResponse(
        request,
        "qc_list.html",
        {"request": request, "sessions": sessions},
    )


@router.get("/qc/{goods_code}", response_class=HTMLResponse)
async def qc_detail_page(request: Request, goods_code: str) -> HTMLResponse:
    """비교 슬라이더 페이지."""
    job = await get_job_by_goods_code(goods_code)
    if not job:
        raise HTTPException(status_code=404, detail="해당 goods_code 세션 없음")
    job_id = job["job_id"]
    source_path = job.get("source_path") or ""
    mode = job.get("mode") or "bg_remove"
    status = job.get("status") or "unknown"
    settings = get_settings()
    goods_code_resolved = get_session_display_info(
        job_id=job_id,
        source_path=source_path,
        status=status,
        created_at=job.get("created_at"),
        mode=mode,
    )["goods_code"]
    raw_images = resolve_qc_images(
        photos_root=settings.photos_root,
        processed_root=settings.processed_root,
        source_path=source_path,
        mode=mode,
        goods_code=goods_code_resolved,
    )
    images = []
    for img in raw_images:
        base = f"/qc/image"
        processed_url = f"{base}/processed/{job_id}/{img['index']}" if img.get("processed_path") else None
        crop_urls = {}
        for ct in ("full_body", "upper_body", "half_body"):
            if img.get("crop_paths") and img["crop_paths"].get(ct):
                crop_urls[ct] = f"{base}/cropped/{job_id}/{img['index']}/{ct}"
            else:
                crop_urls[ct] = None
        images.append({
            "index": img["index"],
            "filename": img["filename"],
            "stem": img["stem"],
            "processed_url": processed_url,
            "crop_urls": crop_urls,
        })
    folder_name = Path(source_path).name if source_path else ""
    parsed = parse_cody_folder_name(folder_name)
    product_label = f"{goods_code_resolved} - {parsed.brand} {parsed.product_name}" if parsed else goods_code_resolved
    templates = _templates()
    return templates.TemplateResponse(
        request,
        "qc_detail.html",
        {
            "request": request,
            "job_id": job_id,
            "goods_code": goods_code_resolved,
            "status": status,
            "product_label": product_label,
            "folder_name": folder_name,
            "images": images,
            "image_count": len(images),
        },
    )


async def _get_image_path(
    job_id: str,
    index: int,
    kind: str,
    crop_type: Optional[str] = None,
) -> Path:
    """job_id, index, kind(original|processed|cropped)로 파일 경로 반환."""
    job = await get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    settings = get_settings()
    source_path = job.get("source_path") or ""
    mode = job.get("mode") or "bg_remove"
    from app.qc.image_resolver import get_goods_code_from_source_path
    goods_code = get_goods_code_from_source_path(source_path)
    images = resolve_qc_images(
        photos_root=settings.photos_root,
        processed_root=settings.processed_root,
        source_path=source_path,
        mode=mode,
        goods_code=goods_code,
    )
    if index < 0 or index >= len(images):
        raise HTTPException(status_code=404, detail="image index out of range")
    entry = images[index]
    if kind == "original":
        path = entry["original_path"]
    elif kind == "processed":
        path = entry.get("processed_path")
    elif kind == "cropped" and crop_type:
        path = (entry.get("crop_paths") or {}).get(crop_type)
    else:
        raise HTTPException(status_code=400, detail="invalid kind or crop_type")
    if not path or not Path(path).exists():
        raise HTTPException(status_code=404, detail="image file not found")
    return Path(path)


@router.get("/qc/image/original/{job_id}/{index}")
async def qc_image_original(job_id: str, index: int):
    """원본 이미지 서빙."""
    path = await _get_image_path(job_id, index, "original")
    return FileResponse(path, media_type="image/jpeg")

@router.get("/qc/image/processed/{job_id}/{index}")
async def qc_image_processed(job_id: str, index: int):
    """보정/누끼 이미지 서빙."""
    path = await _get_image_path(job_id, index, "processed")
    return FileResponse(path, media_type="image/jpeg")

@router.get("/qc/image/cropped/{job_id}/{index}/{crop_type}")
async def qc_image_cropped(job_id: str, index: int, crop_type: str):
    """크랍 이미지 서빙. crop_type: full_body, upper_body, half_body."""
    if crop_type not in ("full_body", "upper_body", "half_body"):
        raise HTTPException(status_code=400, detail="crop_type must be full_body, upper_body, or half_body")
    path = await _get_image_path(job_id, index, "cropped", crop_type=crop_type)
    return FileResponse(path, media_type="image/jpeg")
