"""
SQLite 작업 큐: image_queue, image_result, tone_presets 테이블. aiosqlite 비동기.
"""
import logging
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiosqlite

from app.parsers.folder_parser import parse_cody_folder_name

logger = logging.getLogger(__name__)
_db_path: Optional[Path] = None


def _get_db_path() -> Path:
    global _db_path
    if _db_path is None:
        raise RuntimeError("DB not initialized")
    return _db_path


async def init_db(db_dir: Path) -> None:
    """DB 디렉터리 생성 및 테이블 초기화."""
    global _db_path
    db_dir = Path(db_dir)
    db_dir.mkdir(parents=True, exist_ok=True)
    _db_path = db_dir / "jobs.db"
    async with aiosqlite.connect(_db_path) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS image_queue (
                job_id TEXT PRIMARY KEY,
                source_path TEXT NOT NULL,
                mode TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'queued',
                message TEXT,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS image_result (
                job_id TEXT PRIMARY KEY,
                output_path TEXT,
                status TEXT NOT NULL,
                message TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (job_id) REFERENCES image_queue(job_id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tone_presets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                brand TEXT,
                season TEXT,
                tags TEXT,
                stats_json TEXT NOT NULL,
                image_path TEXT,
                thumbnail_path TEXT,
                use_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        await db.commit()
    async with aiosqlite.connect(_db_path) as db:
        for col in (
            "preset_id INTEGER",
            "match_strength REAL",
            "advanced_matching INTEGER",
            "skin_protection INTEGER",
            "bg_separation INTEGER",
            "normalize_wb INTEGER",
            "wb_strength REAL",
        ):
            try:
                await db.execute("ALTER TABLE image_queue ADD COLUMN " + col)
                await db.commit()
            except aiosqlite.OperationalError:
                pass


async def create_job(
    source_path: str,
    mode: str = "bg_remove",
    preset_id: Optional[int] = None,
    match_strength: Optional[float] = None,
    advanced_matching: Optional[bool] = None,
    skin_protection: Optional[bool] = None,
    bg_separation: Optional[bool] = None,
    normalize_wb: Optional[bool] = None,
    wb_strength: Optional[float] = None,
) -> str:
    """작업 생성. job_id 반환. preset_id/match_strength/advanced_matching/normalize_wb/wb_strength 등은 배치 톤 매칭 시 사용."""
    import datetime
    job_id = str(uuid.uuid4())
    now = datetime.datetime.utcnow().isoformat() + "Z"
    adv = 1 if advanced_matching else 0
    skin = 1 if skin_protection else 0
    bg = 1 if bg_separation else 0
    nwb = 1 if normalize_wb is not False else 0
    wbs = wb_strength if wb_strength is not None else 0.7
    async with aiosqlite.connect(_get_db_path()) as db:
        await db.execute(
            "INSERT INTO image_queue (job_id, source_path, mode, status, created_at, preset_id, match_strength, "
            "advanced_matching, skin_protection, bg_separation, normalize_wb, wb_strength) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (job_id, source_path, mode, "queued", now, preset_id, match_strength, adv, skin, bg, nwb, wbs),
        )
        await db.commit()
    return job_id


async def get_job_status(job_id: str) -> Optional[dict]:
    """작업 상태 조회."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT j.job_id, j.source_path, j.mode, j.status, j.message, j.preset_id, j.match_strength, "
            "j.advanced_matching, j.skin_protection, j.bg_separation, r.output_path, r.updated_at "
            "FROM image_queue j LEFT JOIN image_result r ON j.job_id = r.job_id WHERE j.job_id = ?",
            (job_id,),
        ) as cur:
            row = await cur.fetchone()
    if row is None:
        return None
    out = {
        "job_id": row["job_id"],
        "source_path": row["source_path"],
        "mode": row["mode"],
        "status": row["status"],
        "message": row["message"],
        "preset_id": row["preset_id"] if "preset_id" in row.keys() else None,
        "match_strength": row["match_strength"] if "match_strength" in row.keys() else None,
        "output_path": row["output_path"],
        "updated_at": row["updated_at"],
    }
    if "advanced_matching" in row.keys():
        out["advanced_matching"] = bool(row["advanced_matching"]) if row["advanced_matching"] is not None else False
    if "skin_protection" in row.keys():
        out["skin_protection"] = bool(row["skin_protection"]) if row["skin_protection"] is not None else True
    if "bg_separation" in row.keys():
        out["bg_separation"] = bool(row["bg_separation"]) if row["bg_separation"] is not None else True
    return out


async def list_sessions(limit: int = 100) -> List[dict]:
    """최근 작업 목록. created_at, mode 포함."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT job_id, source_path, status, created_at, mode FROM image_queue ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ) as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_job_by_goods_code(goods_code: str) -> Optional[dict]:
    """goods_code에 해당하는 작업 1건 조회. source_path 폴더명 파싱으로 매칭."""
    sessions = await list_sessions(limit=500)
    code_lower = goods_code.strip().lower()
    for s in sessions:
        source = s.get("source_path") or ""
        folder_name = Path(source).name
        parsed = parse_cody_folder_name(folder_name)
        if parsed and parsed.goods_code.lower() == code_lower:
            return s
    return None


async def get_one_queued_job() -> Optional[dict]:
    """
    queued 상태인 작업 1건을 가져와 processing으로 변경 후 반환.
    동시성: SELECT 후 UPDATE ... WHERE job_id=? AND status='queued' 로 한 워커만 가져가도록 함.
    """
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT job_id, source_path, mode, preset_id, match_strength, normalize_wb, wb_strength, "
            "advanced_matching, skin_protection, bg_separation FROM image_queue "
            "WHERE status = 'queued' ORDER BY created_at ASC LIMIT 1"
        ) as cur:
            row = await cur.fetchone()
        if row is None:
            return None
        job_id = row["job_id"]
        cur_up = await db.execute(
            "UPDATE image_queue SET status = 'processing' WHERE job_id = ? AND status = 'queued'", (job_id,)
        )
        updated = cur_up.rowcount
        await db.commit()
        if updated == 0:
            return None
    result = {
        "job_id": job_id,
        "source_path": row["source_path"],
        "mode": row["mode"],
        "preset_id": row["preset_id"],
        "match_strength": row["match_strength"],
        "normalize_wb": bool(row["normalize_wb"]) if "normalize_wb" in row.keys() and row["normalize_wb"] is not None else True,
        "wb_strength": float(row["wb_strength"]) if "wb_strength" in row.keys() and row["wb_strength"] is not None else 0.7,
    }
    result["advanced_matching"] = bool(row["advanced_matching"]) if "advanced_matching" in row.keys() and row["advanced_matching"] is not None else False
    result["skin_protection"] = bool(row["skin_protection"]) if "skin_protection" in row.keys() and row["skin_protection"] is not None else True
    result["bg_separation"] = bool(row["bg_separation"]) if "bg_separation" in row.keys() and row["bg_separation"] is not None else True
    return result


async def set_job_result(job_id: str, output_path: Optional[str], status: str, message: Optional[str] = None) -> None:
    """작업 결과 기록 및 큐 상태 갱신."""
    import datetime
    now = datetime.datetime.utcnow().isoformat() + "Z"
    async with aiosqlite.connect(_get_db_path()) as db:
        await db.execute(
            "UPDATE image_queue SET status = ?, message = ? WHERE job_id = ?",
            (status, message, job_id),
        )
        await db.execute(
            "INSERT OR REPLACE INTO image_result (job_id, output_path, status, message, updated_at) VALUES (?,?,?,?,?)",
            (job_id, output_path or "", status, message or "", now),
        )
        await db.commit()


async def approve_job(job_id: str) -> None:
    """QC 승인."""
    async with aiosqlite.connect(_get_db_path()) as db:
        async with db.execute("SELECT 1 FROM image_queue WHERE job_id = ?", (job_id,)) as cur:
            if await cur.fetchone() is None:
                raise ValueError("job not found")
        await db.execute("UPDATE image_queue SET status = 'approved' WHERE job_id = ?", (job_id,))
        await db.execute(
            "INSERT OR REPLACE INTO image_result (job_id, output_path, status, message, updated_at) VALUES (?,?,?,?,?)",
            (job_id, "", "approved", "", __import__("datetime").datetime.utcnow().isoformat() + "Z"),
        )
        await db.commit()


async def reject_job(job_id: str, reason: Optional[str] = None) -> None:
    """QC 반려. reason은 image_result.message에 저장."""
    import datetime
    now = datetime.datetime.utcnow().isoformat() + "Z"
    async with aiosqlite.connect(_get_db_path()) as db:
        async with db.execute("SELECT 1 FROM image_queue WHERE job_id = ?", (job_id,)) as cur:
            if await cur.fetchone() is None:
                raise ValueError("job not found")
        await db.execute("UPDATE image_queue SET status = 'rejected' WHERE job_id = ?", (job_id,))
        await db.execute(
            "INSERT OR REPLACE INTO image_result (job_id, output_path, status, message, updated_at) VALUES (?,?,?,?,?)",
            (job_id, "", "rejected", reason or "", now),
        )
        await db.commit()


# ----- tone_presets -----

async def create_preset(
    name: str,
    stats_json: str,
    description: Optional[str] = None,
    brand: Optional[str] = None,
    season: Optional[str] = None,
    tags: Optional[str] = None,
    image_path: Optional[str] = None,
    thumbnail_path: Optional[str] = None,
) -> int:
    """프리셋 생성. id 반환."""
    import datetime
    now = datetime.datetime.utcnow().isoformat() + "Z"
    async with aiosqlite.connect(_get_db_path()) as db:
        cur = await db.execute(
            "INSERT INTO tone_presets (name, description, brand, season, tags, stats_json, "
            "image_path, thumbnail_path, use_count, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,0,?,?)",
            (name, description or "", brand or "", season or "", tags or "", stats_json,
             image_path or "", thumbnail_path or "", now, now),
        )
        await db.commit()
        return cur.lastrowid or 0


async def get_preset(preset_id: int) -> Optional[Dict[str, Any]]:
    """프리셋 1건 조회."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, name, description, brand, season, tags, stats_json, image_path, "
            "thumbnail_path, use_count, created_at, updated_at FROM tone_presets WHERE id = ?",
            (preset_id,),
        ) as cur:
            row = await cur.fetchone()
    if row is None:
        return None
    return dict(row)


async def list_presets(
    brand: Optional[str] = None,
    season: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """프리셋 목록. brand/season 필터 optional."""
    async with aiosqlite.connect(_get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        if brand or season:
            conditions = []
            params: List[Any] = []
            if brand:
                conditions.append("brand = ?")
                params.append(brand)
            if season:
                conditions.append("season = ?")
                params.append(season)
            sql = "SELECT id, name, description, brand, season, tags, stats_json, image_path, thumbnail_path, use_count, created_at, updated_at FROM tone_presets WHERE " + " AND ".join(conditions) + " ORDER BY use_count DESC, id ASC"
            async with db.execute(sql, params) as cur:
                rows = await cur.fetchall()
        else:
            async with db.execute(
                "SELECT id, name, description, brand, season, tags, stats_json, image_path, thumbnail_path, use_count, created_at, updated_at FROM tone_presets ORDER BY use_count DESC, id ASC"
            ) as cur:
                rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def update_preset(
    preset_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    brand: Optional[str] = None,
    season: Optional[str] = None,
    tags: Optional[str] = None,
    stats_json: Optional[str] = None,
    image_path: Optional[str] = None,
    thumbnail_path: Optional[str] = None,
) -> None:
    """프리셋 수정. 전달된 필드만 갱신."""
    import datetime
    now = datetime.datetime.utcnow().isoformat() + "Z"
    preset = await get_preset(preset_id)
    if not preset:
        raise ValueError("preset not found")
    updates = ["updated_at = ?"]
    params: List[Any] = [now]
    if name is not None:
        updates.append("name = ?")
        params.append(name)
    if description is not None:
        updates.append("description = ?")
        params.append(description)
    if brand is not None:
        updates.append("brand = ?")
        params.append(brand)
    if season is not None:
        updates.append("season = ?")
        params.append(season)
    if tags is not None:
        updates.append("tags = ?")
        params.append(tags)
    if stats_json is not None:
        updates.append("stats_json = ?")
        params.append(stats_json)
    if image_path is not None:
        updates.append("image_path = ?")
        params.append(image_path)
    if thumbnail_path is not None:
        updates.append("thumbnail_path = ?")
        params.append(thumbnail_path)
    params.append(preset_id)
    async with aiosqlite.connect(_get_db_path()) as db:
        await db.execute(
            "UPDATE tone_presets SET " + ", ".join(updates) + " WHERE id = ?",
            params,
        )
        await db.commit()


async def delete_preset(preset_id: int) -> None:
    """프리셋 삭제."""
    async with aiosqlite.connect(_get_db_path()) as db:
        cur = await db.execute("DELETE FROM tone_presets WHERE id = ?", (preset_id,))
        await db.commit()
        if cur.rowcount == 0:
            raise ValueError("preset not found")


async def increment_preset_use(preset_id: int) -> None:
    """프리셋 사용 횟수 +1."""
    async with aiosqlite.connect(_get_db_path()) as db:
        await db.execute("UPDATE tone_presets SET use_count = use_count + 1 WHERE id = ?", (preset_id,))
        await db.commit()


# 기본 프리셋 3종 (시스템 초기화 시 삽입)
DEFAULT_PRESETS = [
    {
        "name": "밝고 따뜻한 톤",
        "description": "밝고 따뜻한 색감. B 채널 약간 높음.",
        "stats": {
            "l_mean": 145.0, "l_std": 45.0, "a_mean": 128.0, "a_std": 12.0,
            "b_mean": 138.0, "b_std": 10.0, "color_temp": 138.0, "saturation": 15.6,
        },
    },
    {
        "name": "밝고 차가운 톤",
        "description": "밝고 차가운 색감. B 채널 약간 낮음.",
        "stats": {
            "l_mean": 148.0, "l_std": 42.0, "a_mean": 128.0, "a_std": 11.0,
            "b_mean": 118.0, "b_std": 10.0, "color_temp": 118.0, "saturation": 14.9,
        },
    },
    {
        "name": "자연스러운 톤",
        "description": "중간 밝기, 중성 색온도.",
        "stats": {
            "l_mean": 128.0, "l_std": 48.0, "a_mean": 128.0, "a_std": 14.0,
            "b_mean": 128.0, "b_std": 12.0, "color_temp": 128.0, "saturation": 18.4,
        },
    },
]


async def ensure_default_presets() -> None:
    """프리셋이 하나도 없으면 기본 프리셋 3개 생성."""
    import json
    existing = await list_presets()
    if existing:
        return
    for p in DEFAULT_PRESETS:
        stats_json = json.dumps(p["stats"])
        await create_preset(
            name=p["name"],
            stats_json=stats_json,
            description=p.get("description") or "",
        )
    logger.info("default tone presets created")
