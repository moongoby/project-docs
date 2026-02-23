# CUR-GO100-UNIFIED-SAVE-BE, 2026-02-23
# GO100 사용자 ID 변환 유틸리티
# legacy users.id ↔ v4_users.user_id 매핑

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


async def get_effective_uid(db: AsyncSession, jwt_user_id: int) -> int:
    """
    JWT에서 추출한 user_id를 v4_users.user_id로 변환.
    이미 v4_users.user_id이면 그대로 반환.
    legacy users.id이면 email 기준으로 v4_users.user_id를 조회.
    """
    result = await db.execute(
        text("SELECT user_id FROM v4_users WHERE user_id = :uid"),
        {"uid": jwt_user_id}
    )
    if result.scalar_one_or_none() is not None:
        return jwt_user_id

    result = await db.execute(
        text("""
            SELECT vu.user_id
            FROM users u
            JOIN v4_users vu ON u.email = vu.email
            WHERE u.id = :uid
        """),
        {"uid": jwt_user_id}
    )
    v4_uid = result.scalar_one_or_none()
    if v4_uid is not None:
        return v4_uid

    return jwt_user_id


async def get_user_email(db: AsyncSession, user_id: int) -> Optional[str]:
    """user_id로 이메일 조회 (v4_users 우선, fallback legacy users)"""
    result = await db.execute(
        text("SELECT email FROM v4_users WHERE user_id = :uid"),
        {"uid": user_id}
    )
    email = result.scalar_one_or_none()
    if email:
        return email

    result = await db.execute(
        text("SELECT email FROM users WHERE id = :uid"),
        {"uid": user_id}
    )
    return result.scalar_one_or_none()
