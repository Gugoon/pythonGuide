"""댓글(Comment) 관련 라우트.

- GET /posts/{post_id}/comments: 댓글 목록 (공개 글이거나 본인 비공개 글이면 가능).
- POST /posts/{post_id}/comments: 댓글 작성 (로그인 필요).
- PATCH /comments/{comment_id}: 본인 댓글만 수정.
- DELETE /comments/{comment_id}: 본인 댓글만 삭제.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db import get_session
from app.deps import get_current_user, get_optional_user
from app.models import Comment, Post, User
from app.schemas import CommentCreate, CommentRead, CommentUpdate

# 댓글 목록·작성은 글 ID에 종속이라 /posts 아래에 두고,
# 단건 수정·삭제는 /comments/{id}로 둔다.
post_comments_router = APIRouter(prefix="/posts", tags=["comments"])
comments_router = APIRouter(prefix="/comments", tags=["comments"])


def _post_visible_to(post: Post, viewer: User | None) -> bool:
    if post.published:
        return True
    return viewer is not None and post.user_id == viewer.id


@post_comments_router.get(
    "/{post_id}/comments",
    response_model=list[CommentRead],
    summary="댓글 목록",
)
async def list_comments(
    post_id: int,
    session: AsyncSession = Depends(get_session),
    viewer: User | None = Depends(get_optional_user),
) -> list[Comment]:
    post = await session.get(Post, post_id)
    if post is None or not _post_visible_to(post, viewer):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "해당 글을 찾을 수 없습니다")

    result = await session.execute(
        select(Comment)
        .where(Comment.post_id == post_id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at.asc(), Comment.id.asc())
    )
    return list(result.scalars().all())


@post_comments_router.post(
    "/{post_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="댓글 작성",
)
async def create_comment(
    post_id: int,
    payload: CommentCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Comment:
    post = await session.get(Post, post_id)
    if post is None or not _post_visible_to(post, current_user):
        # 본인이 자기 비공개 글에 댓글 다는 것은 허용. 남의 비공개는 404.
        raise HTTPException(status.HTTP_404_NOT_FOUND, "해당 글을 찾을 수 없습니다")

    comment = Comment(post_id=post_id, user_id=current_user.id, body=payload.body)
    session.add(comment)
    await session.commit()

    # author 같이 로드해서 응답.
    result = await session.execute(
        select(Comment)
        .where(Comment.id == comment.id)
        .options(selectinload(Comment.author))
    )
    return result.scalar_one()


@comments_router.patch(
    "/{comment_id}",
    response_model=CommentRead,
    summary="댓글 수정 (작성자만)",
)
async def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> Comment:
    comment = await session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "해당 댓글을 찾을 수 없습니다")
    if comment.user_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "본인이 작성한 댓글만 수정할 수 있습니다"
        )

    comment.body = payload.body
    await session.commit()

    result = await session.execute(
        select(Comment)
        .where(Comment.id == comment.id)
        .options(selectinload(Comment.author))
    )
    return result.scalar_one()


@comments_router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="댓글 삭제 (작성자만)",
)
async def delete_comment(
    comment_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> None:
    comment = await session.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "해당 댓글을 찾을 수 없습니다")
    if comment.user_id != current_user.id:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "본인이 작성한 댓글만 삭제할 수 있습니다"
        )
    await session.delete(comment)
    await session.commit()
