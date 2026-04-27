"""글(Post) 관련 라우트.

핵심 기능:
- POST /posts: 본인 글 작성. tags=["python","fastapi"]를 함께 받으면 자동 생성·연결.
- GET /posts: 목록(페이지네이션, 검색, 태그 필터, 정렬). 비로그인 가능 — 공개 글만.
              로그인된 경우 본인 비공개 글까지 보임.
- GET /posts/{id}: 한 건 조회. 비공개 글은 작성자만.
- PATCH /posts/{id}: 부분 수정. 본인 글만.
- DELETE /posts/{id}: 삭제. 본인 글만.
- POST /posts/{id}/publish, /unpublish: 공개 상태 토글.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud import (
    apply_search,
    apply_sort,
    apply_tag_filter,
    apply_visibility,
    base_count_query,
    base_post_query,
    count_posts,
    get_or_create_tags,
    make_unique_slug,
)
from app.db import get_session
from app.deps import get_current_user, get_optional_user
from app.models import Post, User
from app.schemas import PostCreate, PostList, PostRead, PostUpdate

router = APIRouter(prefix="/posts", tags=["posts"])


# ── 공개·비공개 가시성 헬퍼 ──

def _post_visible_to(post: Post, viewer: User | None) -> bool:
    """공개 글이거나 본인 글이면 True."""
    if post.published:
        return True
    return viewer is not None and post.user_id == viewer.id


# ── 목록 ──

@router.get("", response_model=PostList, summary="글 목록")
async def list_posts(
    session: AsyncSession = Depends(get_session),
    viewer: User | None = Depends(get_optional_user),
    page: int = Query(1, ge=1, description="1부터 시작"),
    size: int = Query(20, ge=1, le=100, description="페이지 크기 (1~100)"),
    q: str | None = Query(None, description="title·body LIKE 검색어"),
    tag: str | None = Query(None, description="이 태그 이름이 붙은 글만"),
    sort: str | None = Query(
        None,
        description="정렬: 'created_at' | '-created_at' (기본: -created_at)",
    ),
) -> PostList:
    """페이지네이션 + 검색 + 태그 필터 + 정렬.

    selectinload로 author·tags를 미리 로드해 N+1 문제를 막습니다.
    """
    viewer_id = viewer.id if viewer is not None else None

    # 1) 카운트 — 같은 필터를 카운트 전용 쿼리에도 적용한다.
    count_stmt = base_count_query()
    count_stmt = apply_visibility(count_stmt, viewer_id)
    count_stmt = apply_search(count_stmt, q)
    count_stmt = apply_tag_filter(count_stmt, tag)
    total = await count_posts(session, count_stmt)

    # 2) 본 SELECT — eager loading 포함.
    stmt = base_post_query()
    stmt = apply_visibility(stmt, viewer_id)
    stmt = apply_search(stmt, q)
    stmt = apply_tag_filter(stmt, tag)
    stmt = apply_sort(stmt, sort)
    stmt = stmt.offset((page - 1) * size).limit(size)

    result = await session.execute(stmt)
    posts = list(result.unique().scalars().all())
    items = [PostRead.model_validate(p) for p in posts]
    return PostList(items=items, page=page, size=size, total=total)


# ── 단건 조회 ──

@router.get("/{post_id}", response_model=PostRead, summary="글 한 건 조회")
async def get_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    viewer: User | None = Depends(get_optional_user),
) -> Post:
    stmt = (
        select(Post)
        .where(Post.id == post_id)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )
    result = await session.execute(stmt)
    post = result.scalar_one_or_none()
    if post is None or not _post_visible_to(post, viewer):
        # 비공개 글의 존재 여부를 굳이 알려줄 필요 없음 — 모두 404.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="해당 글을 찾을 수 없습니다",
        )
    return post


# ── 작성 ──

@router.post(
    "",
    response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
    summary="글 작성",
)
async def create_post(
    payload: PostCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Post:
    slug = await make_unique_slug(session, payload.title)
    now = datetime.now(timezone.utc)
    post = Post(
        user_id=current_user.id,
        title=payload.title,
        slug=slug,
        body=payload.body,
        published=payload.published,
        published_at=now if payload.published else None,
    )
    if payload.tags:
        post.tags = await get_or_create_tags(session, payload.tags)

    session.add(post)
    await session.commit()

    # 응답에 author·tags 포함을 위해 다시 로드.
    refreshed = await session.execute(
        select(Post)
        .where(Post.id == post.id)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )
    return refreshed.scalar_one()


# ── 수정 ──

@router.patch("/{post_id}", response_model=PostRead, summary="글 수정 (작성자만)")
async def update_post(
    post_id: int,
    payload: PostUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Post:
    # tags 를 교체할 수 있으므로 처음부터 selectinload 로 함께 로드한다.
    # session.get() 만 쓰면 post.tags 가 lazy 상태라 비동기 컨텍스트 안에서
    # 재할당 시 MissingGreenlet 이 발생한다.
    result = await session.execute(
        select(Post)
        .where(Post.id == post_id)
        .options(selectinload(Post.tags))
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "해당 글을 찾을 수 없습니다")
    if post.user_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "본인이 작성한 글만 수정할 수 있습니다"
        )

    data = payload.model_dump(exclude_unset=True)

    if "title" in data:
        post.title = data["title"]
        # 제목이 바뀌면 slug도 재생성해야 깔끔하지만, URL이 깨질 수 있어
        # 본 가이드에서는 slug를 그대로 유지합니다(원하는 정책으로 바꿀 것).

    if "body" in data:
        post.body = data["body"]

    if "published" in data:
        new_published: bool = data["published"]
        # False → True 로 바뀌는 순간 published_at 도장을 찍는다.
        if new_published and not post.published:
            post.published_at = datetime.now(timezone.utc)
        post.published = new_published

    if "tags" in data:
        names = data["tags"] or []
        post.tags = await get_or_create_tags(session, names)

    await session.commit()

    # 응답용 재로드.
    refreshed = await session.execute(
        select(Post)
        .where(Post.id == post.id)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )
    return refreshed.scalar_one()


# ── 삭제 ──

@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="글 삭제 (작성자만)",
)
async def delete_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    # cascade="all, delete-orphan" 정책 때문에 session.delete(post) 가
    # post.comments 와 post.tags 를 lazy load 하려 한다. 비동기 컨텍스트에서
    # 그 lazy load 가 MissingGreenlet 으로 터지므로, 처음부터 selectinload 로
    # 함께 가져온다(태그는 secondary, 댓글은 1:N).
    result = await session.execute(
        select(Post)
        .where(Post.id == post_id)
        .options(selectinload(Post.comments), selectinload(Post.tags))
    )
    post = result.scalar_one_or_none()
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "해당 글을 찾을 수 없습니다")
    if post.user_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "본인이 작성한 글만 삭제할 수 있습니다"
        )
    await session.delete(post)
    await session.commit()


# ── 게시 상태 토글 ──

@router.post(
    "/{post_id}/publish",
    response_model=PostRead,
    summary="공개 처리 (작성자만)",
)
async def publish_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Post:
    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "해당 글을 찾을 수 없습니다")
    if post.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "권한이 없습니다")

    if not post.published:
        post.published = True
        post.published_at = datetime.now(timezone.utc)
        await session.commit()

    refreshed = await session.execute(
        select(Post)
        .where(Post.id == post.id)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )
    return refreshed.scalar_one()


@router.post(
    "/{post_id}/unpublish",
    response_model=PostRead,
    summary="비공개 처리 (작성자만)",
)
async def unpublish_post(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Post:
    post = await session.get(Post, post_id)
    if post is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "해당 글을 찾을 수 없습니다")
    if post.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "권한이 없습니다")

    if post.published:
        post.published = False
        # published_at을 null로 되돌릴지는 정책. 본 가이드는 마지막 공개 시각을 보존.
        await session.commit()

    refreshed = await session.execute(
        select(Post)
        .where(Post.id == post.id)
        .options(selectinload(Post.author), selectinload(Post.tags))
    )
    return refreshed.scalar_one()
