"""
API 엔드포인트: process, batch, status, sessions, approve, reject, health, preset CRUD.
"""
import json
import logging
import tempfile
from pathlib import Path
from typing import Any, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.config import get_settings
from app.queue.job_manager import (
    create_job,
    get_job_status,
    list_sessions,
    approve_job,
    reject_job,
    create_preset,
    get_preset,
    list_presets,
    update_preset,
    delete_preset,
)
from app.workers.tone_matcher import ToneMatcher, ToneStats

logger = logging.getLogger(__name__)
router = APIRouter()


class ProcessRequest(BaseModel):
    """단건 처리 요청."""
    source_path: str
    mode: str = "bg_remove"  # bg_remove | correct


class BatchProcessRequest(BaseModel):
    """배치 처리 요청. folder_path 또는 items 중 하나 사용. preset_id 있으면 톤 매칭 후 보정."""
    folder_path: Optional[str] = None  # 폴더 단위 1건 job
    folder_mode: str = "bg_remove"  # folder_path 사용 시 모드
    items: Optional[List[ProcessRequest]] = None  # 파일 단위 다건
    preset_id: Optional[int] = None  # 톤 매칭 프리셋 (correct 모드와 함께 사용)
    match_strength: Optional[float] = 0.85  # 톤 매칭 강도 0~1
    advanced_matching: Optional[bool] = False  # 영역별 차등 톤 매칭 (피부/배경 분리)
    skin_protection: Optional[bool] = True  # advanced 시 피부톤 보호
    bg_separation: Optional[bool] = True  # advanced 시 배경 색상 유지
    normalize_wb: Optional[bool] = True  # 톤 매칭 전 화이트밸런스 정규화
    wb_strength: Optional[float] = 0.7  # WB 정규화 강도 0~1


class RejectRequest(BaseModel):
    """QC 반려 요청 (사유 선택)."""
    reason: Optional[str] = None


class JobResponse(BaseModel):
    """작업 생성/상태 응답."""
    job_id: str
    status: str
    message: Optional[str] = None


class SessionItem(BaseModel):
    """세션(작업) 목록 항목."""
    job_id: str
    status: str
    source_path: Optional[str] = None
    created_at: Optional[str] = None
    mode: Optional[str] = None


@router.post("/process", response_model=JobResponse)
async def api_process(req: ProcessRequest) -> Any:
    """단건 이미지 처리 요청."""
    try:
        job_id = await create_job(
            source_path=req.source_path,
            mode=req.mode,
        )
        return JobResponse(job_id=job_id, status="queued")
    except Exception as e:
        logger.exception("process error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process/batch", response_model=List[JobResponse])
async def api_process_batch(req: BatchProcessRequest) -> Any:
    """배치 처리 요청. folder_path(1건) 또는 items(다건). job_id 목록 반환 후 백그라운드에서 처리."""
    result: List[JobResponse] = []
    preset_id = getattr(req, "preset_id", None)
    match_strength = getattr(req, "match_strength", None)
    normalize_wb = getattr(req, "normalize_wb", True)
    wb_strength = getattr(req, "wb_strength", 0.7)
    advanced_matching = getattr(req, "advanced_matching", None)
    skin_protection = getattr(req, "skin_protection", None)
    bg_separation = getattr(req, "bg_separation", None)
    if req.folder_path:
        try:
            job_id = await create_job(
                source_path=req.folder_path,
                mode=req.folder_mode,
                preset_id=preset_id,
                match_strength=match_strength,
                normalize_wb=normalize_wb,
                wb_strength=wb_strength,
                advanced_matching=advanced_matching,
                skin_protection=skin_protection,
                bg_separation=bg_separation,
            )
            result.append(JobResponse(job_id=job_id, status="queued"))
        except Exception as e:
            logger.exception("batch folder error: %s", req.folder_path)
            result.append(JobResponse(job_id="", status="error", message=str(e)))
    if req.items:
        for item in req.items:
            try:
                job_id = await create_job(
                    source_path=item.source_path,
                    mode=item.mode,
                    preset_id=preset_id,
                    match_strength=match_strength,
                    normalize_wb=normalize_wb,
                    wb_strength=wb_strength,
                    advanced_matching=advanced_matching,
                    skin_protection=skin_protection,
                    bg_separation=bg_separation,
                )
                result.append(JobResponse(job_id=job_id, status="queued"))
            except Exception as e:
                logger.exception("batch item error: %s", item.source_path)
                result.append(JobResponse(job_id="", status="error", message=str(e)))
    if not req.folder_path and not req.items:
        raise HTTPException(status_code=400, detail="folder_path 또는 items 중 하나는 필수입니다.")
    return result


@router.get("/status/{job_id}", response_model=JobResponse)
async def api_status(job_id: str) -> Any:
    """작업 상태 조회."""
    status = await get_job_status(job_id)
    if status is None:
        raise HTTPException(status_code=404, detail="job not found")
    return JobResponse(job_id=job_id, status=status.get("status", "unknown"), message=status.get("message"))


@router.get("/sessions", response_model=List[SessionItem])
async def api_sessions() -> Any:
    """세션(작업 목록) 조회."""
    items = await list_sessions()
    return [
        SessionItem(
            job_id=x["job_id"],
            status=x["status"],
            source_path=x.get("source_path"),
            created_at=x.get("created_at"),
            mode=x.get("mode"),
        )
        for x in items
    ]


@router.post("/approve/{job_id}", response_model=JobResponse)
async def api_approve(job_id: str) -> Any:
    """QC 승인."""
    try:
        await approve_job(job_id)
        return JobResponse(job_id=job_id, status="approved")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/reject/{job_id}", response_model=JobResponse)
async def api_reject(job_id: str, body: Optional[RejectRequest] = None) -> Any:
    """QC 반려. body.reason 있으면 image_result.message에 저장."""
    try:
        reason = body.reason if body else None
        await reject_job(job_id, reason=reason)
        return JobResponse(job_id=job_id, status="rejected")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/health")
async def api_health() -> dict:
    """헬스체크."""
    return {"status": "ok"}


# ---------- 폴더 자동 분류 (Part 2) ----------


class ClassifyRequest(BaseModel):
    """폴더 분류 요청."""
    folder_path: str
    threshold: float = 180.0  # 초


class ClassifyConfirmRequest(BaseModel):
    """분류 확정 요청 (그룹별 이미지 경로 목록)."""
    folder_path: str
    groups: List[List[str]]  # 각 그룹별 파일 경로 리스트


class ClassifyReclassifyRequest(BaseModel):
    """재분류 요청."""
    folder_path: str
    threshold: float = 180.0


def _classify_result_to_dict(result: Any) -> dict:
    return {
        "total_images": result.total_images,
        "total_groups": result.total_groups,
        "threshold_seconds": result.threshold_seconds,
        "no_exif_images": [str(p) for p in result.no_exif_images],
        "groups": [
            {
                "group_index": g.group_index,
                "images": [str(p) for p in g.images],
                "start_time": g.start_time,
                "end_time": g.end_time,
                "duration_seconds": g.duration_seconds,
            }
            for g in result.groups
        ],
    }


@router.get("/classify/thumb")
async def api_classify_thumb(path: str) -> Any:
    """분류 그리드용 썸네일. path가 photos_root 또는 processed_root 하위일 때만 서빙."""
    from pathlib import Path
    settings = get_settings()
    try:
        p = Path(path)
        if not p.is_absolute():
            p = (settings.photos_root / path).resolve()
        else:
            p = p.resolve()
        if not p.exists() or not p.is_file():
            raise HTTPException(status_code=404, detail="not found")
        try:
            p.relative_to(settings.photos_root.resolve())
        except ValueError:
            try:
                p.relative_to(settings.processed_root.resolve())
            except ValueError:
                raise HTTPException(status_code=403, detail="path not allowed")
        return FileResponse(p, media_type="image/jpeg")
    except HTTPException:
        raise
    except Exception as e:
        logger.debug("classify thumb %s: %s", path, e)
        raise HTTPException(status_code=404, detail="not found")


@router.post("/classify")
async def api_classify(req: ClassifyRequest) -> Any:
    """폴더 분류: EXIF 시간 기준 그룹화 결과 반환."""
    from app.workers.auto_classify import AutoClassifier

    classifier = AutoClassifier(threshold_seconds=req.threshold)
    result = classifier.classify_folder(req.folder_path)
    return _classify_result_to_dict(result)


@router.post("/classify/confirm")
async def api_classify_confirm(req: ClassifyConfirmRequest) -> Any:
    """분류 확정: groups에 따라 코디 폴더 생성 후 이미지 복사/이동."""
    from pathlib import Path
    from app.workers.auto_classify import AutoClassifier

    folder = Path(req.folder_path)
    if not folder.is_dir():
        raise HTTPException(status_code=400, detail="folder_path is not a directory")
    output_base = folder.parent / (folder.name + "_classified")
    output_base.mkdir(parents=True, exist_ok=True)
    created_dirs: List[str] = []
    for i, paths in enumerate(req.groups):
        dir_name = f"코디_{i + 1:02d}"
        dest_dir = output_base / dir_name
        dest_dir.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(dest_dir))
        for rel_or_abs in paths:
            p = Path(rel_or_abs)
            if not p.is_absolute():
                p = folder / p.name if (folder / p.name).exists() else folder / p
            if p.exists():
                import shutil
                shutil.copy2(p, dest_dir / p.name)
    return {"message": "ok", "output_base": str(output_base), "created_dirs": created_dirs}


@router.post("/classify/reclassify")
async def api_classify_reclassify(req: ClassifyReclassifyRequest) -> Any:
    """재분류: 새 임계값으로 다시 분류."""
    from app.workers.auto_classify import AutoClassifier

    classifier = AutoClassifier(threshold_seconds=req.threshold)
    result = classifier.reclassify(req.folder_path, req.threshold)
    return _classify_result_to_dict(result)


# ----- Preset CRUD -----

def _preset_assets_dir() -> Path:
    """프리셋 이미지 저장 디렉터리."""
    return Path(get_settings().processed_root) / "_preset_assets"


@router.post("/preset/register")
async def api_preset_register(
    image: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    brand: Optional[str] = Form(None),
    season: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
) -> Any:
    """이미지 업로드 → 톤 분석 → 프리셋 DB 저장. id, stats 반환."""
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="image file required")
    try:
        with tempfile.NamedTemporaryFile(suffix=Path(image.filename or "img").suffix or ".jpg", delete=False) as f:
            content = await image.read()
            f.write(content)
            tmp_path = Path(f.name)
        try:
            matcher = ToneMatcher()
            stats = matcher.analyze_image(tmp_path)
            stats_json = json.dumps(stats.to_dict())
            preset_id = await create_preset(
                name=name,
                stats_json=stats_json,
                description=description,
                brand=brand or "",
                season=season or "",
                tags=tags or "",
            )
            assets_dir = _preset_assets_dir() / str(preset_id)
            assets_dir.mkdir(parents=True, exist_ok=True)
            image_path = assets_dir / "image.jpg"
            import shutil
            shutil.copy2(tmp_path, image_path)
            thumbnail_path = assets_dir / "thumbnail.jpg"
            from PIL import Image
            pil = Image.open(image_path).convert("RGB")
            pil.thumbnail((200, 200))
            pil.save(thumbnail_path, "JPEG", quality=85)
            await update_preset(
                preset_id,
                image_path=str(image_path),
                thumbnail_path=str(thumbnail_path),
            )
            preset = await get_preset(preset_id)
            return {"id": preset_id, "stats": stats.to_dict(), "preset": preset}
        finally:
            tmp_path.unlink(missing_ok=True)
    except Exception as e:
        logger.exception("preset register error")
        raise HTTPException(status_code=500, detail=str(e))


class PresetUpdateBody(BaseModel):
    """프리셋 수정 요청."""
    name: Optional[str] = None
    description: Optional[str] = None
    brand: Optional[str] = None
    season: Optional[str] = None
    tags: Optional[str] = None


@router.get("/preset/list")
async def api_preset_list(
    brand: Optional[str] = None,
    season: Optional[str] = None,
) -> Any:
    """프리셋 목록. brand, season 쿼리로 필터."""
    items = await list_presets(brand=brand, season=season)
    return {"presets": items}


@router.get("/preset/{preset_id}")
async def api_preset_get(preset_id: int) -> Any:
    """프리셋 1건 조회."""
    preset = await get_preset(preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="preset not found")
    return preset


@router.get("/preset/{preset_id}/image")
async def api_preset_image(preset_id: int) -> Any:
    """프리셋 원본 이미지 반환."""
    preset = await get_preset(preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="preset not found")
    path = preset.get("image_path")
    if not path or not Path(path).exists():
        raise HTTPException(status_code=404, detail="preset image not found")
    return FileResponse(path, media_type="image/jpeg")


@router.get("/preset/{preset_id}/preview")
async def api_preset_preview(
    preset_id: int,
    image_path: str,
) -> Any:
    """지정 이미지에 프리셋 톤 매칭 적용한 미리보기 반환."""
    preset = await get_preset(preset_id)
    if preset is None:
        raise HTTPException(status_code=404, detail="preset not found")
    path = Path(image_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="image_path not found")
    try:
        stats = ToneStats.from_dict(json.loads(preset["stats_json"]))
        matcher = ToneMatcher()
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            out = Path(f.name)
        matcher.match_tone(path, out, stats, strength=0.85, protect_colors=True)
        return FileResponse(out, media_type="image/jpeg")
    except Exception as e:
        logger.exception("preset preview error: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/preset/{preset_id}")
async def api_preset_update(preset_id: int, body: PresetUpdateBody) -> Any:
    """프리셋 메타 수정."""
    try:
        await update_preset(
            preset_id,
            name=body.name,
            description=body.description,
            brand=body.brand,
            season=body.season,
            tags=body.tags,
        )
        preset = await get_preset(preset_id)
        return preset
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/preset/{preset_id}")
async def api_preset_delete(preset_id: int) -> Any:
    """프리셋 삭제."""
    try:
        await delete_preset(preset_id)
        return {"deleted": preset_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
