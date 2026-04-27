"""태그 관련 라우트.

- GET /tags: 전체 태그 목록 (이름 사전순).
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Tag
from app.schemas import TagSummary

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=list[TagSummary], summary="태그 목록")
async def list_tags(
    session: AsyncSession = Depends(get_session),
) -> list[Tag]:
    result = await session.execute(select(Tag).order_by(Tag.name.asc()))
    return list(result.scalars().all())
