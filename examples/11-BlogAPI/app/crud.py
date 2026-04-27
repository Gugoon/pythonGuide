"""순수 DB 접근 함수 모음.

라우터에서 직접 ORM을 다루기보다, 자주 쓰는 쿼리를 한 곳에 모았습니다.
- `make_unique_slug`: title을 slug로 변환하면서 중복 시 -2, -3 접미사를 붙입니다.
- `get_or_create_tags`: 태그 이름 리스트를 받아 없으면 만들고 있으면 가져옵니다.
- `apply_visibility/apply_search/apply_tag_filter/apply_sort`: 쿼리 빌더 헬퍼들.
- `base_post_query`: 본 SELECT 쿼리 (eager loading 포함).
- `base_count_query` + `count_posts`: 페이지네이션 메타데이터용 카운트.

apply_* 함수들은 본 쿼리(SELECT Post)와 카운트 쿼리(SELECT COUNT)의 모양이
서로 달라도 같은 .where/.join 호출이 통하기 때문에, 타입 어노테이션을
`Select[Any]`로 두어 두 쪽에서 모두 사용할 수 있게 했습니다.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from slugify import slugify
from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Post, PostTag, Tag


# ── slug ──

async def make_unique_slug(session: AsyncSession, title: str) -> str:
    """제목으로부터 unique slug를 만든다.

    1) python-slugify로 영문·숫자·하이픈 형태로 정규화.
    2) DB에 이미 같은 slug가 있으면 "-2", "-3" 식으로 접미사를 붙여 시도.
    3) 한국어만 있는 제목은 slug가 빈 문자열이 되므로 'post'를 기본으로.
    """
    base = slugify(title) or "post"
    candidate = base
    n = 2
    while True:
        existing = await session.execute(
            select(Post.id).where(Post.slug == candidate)
        )
        if existing.scalar_one_or_none() is None:
            return candidate
        candidate = f"{base}-{n}"
        n += 1
        # 무한 루프 방지(현실적으로는 도달 안 함).
        if n > 1000:
            raise RuntimeError("slug 후보 생성 한도 초과")


# ── tags ──

async def get_or_create_tags(
    session: AsyncSession, names: Sequence[str]
) -> list[Tag]:
    """태그 이름 리스트를 받아 모두 Tag 인스턴스로 돌려준다.

    - 입력 문자열은 strip + 소문자 정규화.
    - 빈 문자열은 무시.
    - DB에 있으면 그대로, 없으면 INSERT.
    - 중복은 한 번만(같은 이름이 두 번 와도 한 Tag).
    """
    cleaned: list[str] = []
    seen: set[str] = set()
    for raw in names:
        norm = raw.strip().lower()
        if not norm or norm in seen:
            continue
        seen.add(norm)
        cleaned.append(norm)

    if not cleaned:
        return []

    # 있는 것 한 번에 SELECT.
    result = await session.execute(select(Tag).where(Tag.name.in_(cleaned)))
    existing = list(result.scalars().all())
    by_name: dict[str, Tag] = {t.name: t for t in existing}

    # 없는 것은 새로 만든다.
    new_tags: list[Tag] = []
    for name in cleaned:
        if name in by_name:
            continue
        tag = Tag(name=name, slug=slugify(name) or name)
        session.add(tag)
        new_tags.append(tag)
        by_name[name] = tag

    if new_tags:
        # PK 등을 채우기 위해 한 번 flush.
        await session.flush()

    # 입력 순서를 유지하려면 cleaned 기준으로 다시 정렬.
    return [by_name[n] for n in cleaned]


# ── post 목록 ──

def base_post_query() -> Select[Any]:
    """공통 SELECT — author·tags를 한 번에 같이 로드한다.

    selectinload는 "추가 SELECT 1번으로 N+1번 쿼리를 1+M번으로" 줄여 줍니다.
    """
    return (
        select(Post)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )


def base_count_query() -> Select[Any]:
    """count 전용 베이스 쿼리.

    selectinload 옵션은 카운트에 무의미하므로 처음부터 따로 만든다.
    `apply_visibility`/`apply_search`/`apply_tag_filter`는 같은 시그니처로
    이 쿼리에도 적용된다.
    """
    return select(func.count(func.distinct(Post.id))).select_from(Post)


def apply_visibility(stmt: Select[Any], viewer_id: int | None) -> Select[Any]:
    """공개/비공개 필터.

    - 비로그인: 공개 글만.
    - 로그인: 공개 글 + 본인이 쓴 비공개 글.
    """
    if viewer_id is None:
        return stmt.where(Post.published.is_(True))
    return stmt.where(or_(Post.published.is_(True), Post.user_id == viewer_id))


def apply_search(stmt: Select[Any], q: str | None) -> Select[Any]:
    """title·body에 LIKE 검색.

    MySQL에서 LIKE는 인덱스를 활용하지 못해 데이터가 많아지면 느려진다.
    실서비스에서는 FULLTEXT 인덱스 또는 외부 검색엔진(Meilisearch 등)을
    검토하세요(본 가이드 11.21 참고).
    """
    if not q:
        return stmt
    pattern = f"%{q}%"
    return stmt.where(or_(Post.title.like(pattern), Post.body.like(pattern)))


def apply_tag_filter(
    stmt: Select[Any], tag_name: str | None
) -> Select[Any]:
    """특정 태그 이름이 붙은 글만 통과시킨다."""
    if not tag_name:
        return stmt
    norm = tag_name.strip().lower()
    return (
        stmt.join(PostTag, PostTag.post_id == Post.id)
        .join(Tag, Tag.id == PostTag.tag_id)
        .where(Tag.name == norm)
    )


def apply_sort(stmt: Select[Any], sort: str | None) -> Select[Any]:
    """정렬 — sort 파라미터가 'created_at' 또는 '-created_at'."""
    if sort == "created_at":
        return stmt.order_by(Post.created_at.asc(), Post.id.asc())
    # 기본값은 최신순.
    return stmt.order_by(Post.created_at.desc(), Post.id.desc())


async def count_posts(session: AsyncSession, count_stmt: Select[Any]) -> int:
    """필터까지 적용된 카운트 쿼리를 실행해 정수 한 개를 돌려준다."""
    result = await session.execute(count_stmt)
    return int(result.scalar_one())
