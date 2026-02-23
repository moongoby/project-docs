"""
FastAPI 앱 진입점. lifespan에서 DB 초기화, rembg 모델 프리로드, 큐 워커 실행.
"""
import asyncio
import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.queue.job_manager import (
    ensure_default_presets,
    get_one_queued_job,
    get_preset,
    init_db,
    increment_preset_use,
    set_job_result,
)
from app.workers.batch_pipeline import run_pipeline

logger = logging.getLogger(__name__)

_worker_task: asyncio.Task | None = None
_worker_stop = asyncio.Event()


async def _worker_loop() -> None:
    """큐에서 queued 작업을 가져와 파이프라인 실행 후 결과 저장."""
    loop = asyncio.get_event_loop()
    while not _worker_stop.is_set():
        try:
            job = await get_one_queued_job()
            if job is None:
                await asyncio.sleep(2)
                continue
            job_id = job["job_id"]
            source_path = job["source_path"]
            mode = job["mode"]
            preset_id = job.get("preset_id")
            match_strength = job.get("match_strength") if job.get("match_strength") is not None else 0.85
            normalize_wb = job.get("normalize_wb", True)
            wb_strength = job.get("wb_strength", 0.7) if job.get("wb_strength") is not None else 0.7
            advanced_matching = job.get("advanced_matching") in (True, 1)
            skin_protection = job.get("skin_protection") if job.get("skin_protection") is not None else True
            bg_separation = job.get("bg_separation") if job.get("bg_separation") is not None else True
            preset_stats = None
            if preset_id:
                preset = await get_preset(preset_id)
                if preset and preset.get("stats_json"):
                    preset_stats = json.loads(preset["stats_json"])
            try:
                summary, err = await loop.run_in_executor(
                    None,
                    run_pipeline,
                    source_path,
                    mode,
                    preset_stats,
                    match_strength,
                    normalize_wb,
                    wb_strength,
                    advanced_matching,
                    skin_protection,
                    bg_separation,
                )
                if err:
                    await set_job_result(job_id, None, "done", message=err)
                else:
                    await set_job_result(job_id, None, "done", message=summary or "ok")
                    if preset_id:
                        await increment_preset_use(preset_id)
            except Exception as e:
                logger.exception("worker job error: %s", job_id)
                await set_job_result(job_id, None, "error", message=str(e))
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.exception("worker loop: %s", e)
            await asyncio.sleep(5)
    logger.info("worker loop stopped")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작 시 DB 초기화, rembg 모델 프리로드, 큐 워커 시작."""
    global _worker_task
    settings = get_settings()
    Path(settings.db_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.log_dir).mkdir(parents=True, exist_ok=True)
    await init_db(settings.db_dir)
    await ensure_default_presets()
    logger.info("DB initialized")
    try:
        from rembg import remove
        from PIL import Image
        import io
        buf = io.BytesIO()
        Image.new("RGB", (10, 10)).save(buf, format="PNG")
        remove(buf.getvalue())
        logger.info("rembg model preloaded")
    except Exception as e:
        logger.warning("rembg preload skip: %s", e)

    _worker_task = asyncio.create_task(_worker_loop())
    yield
    _worker_stop.set()
    if _worker_task:
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    logger.info("shutdown")


app = FastAPI(title="뉴톡 이미지 자동화 API", lifespan=lifespan)

from app.api.routes import router  # noqa: E402
from app.api.qc_routes import router as qc_router  # noqa: E402

app.include_router(router, prefix="/api", tags=["api"])
app.include_router(qc_router)

# 정적 파일 (QC UI)
_static_dir = Path(__file__).resolve().parent / "static"
if _static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(_static_dir)), name="static")
