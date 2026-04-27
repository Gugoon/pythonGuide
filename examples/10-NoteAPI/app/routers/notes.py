"""Note 도메인 라우터.

이 모듈의 모든 라우트는 `Depends(get_current_active_user)`로 인증을 강제한다.
또한 모든 Note 핸들러는 다음 보안 규약을 따른다.

- 메모 단건/수정/삭제는 `crud.get_owned_note(...)`로 본인 소유만 가져온다.
- 본인이 소유하지 않은 메모(또는 존재하지 않는 메모) → **404 Not Found**.
  "권한 없음(403)" 대신 "없음(404)"으로 응답해, 다른 사용자 메모의 존재 여부조차
  공격자에게 흘리지 않게 한다.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.db import get_session
from app.deps import get_current_active_user
from app.models import User
from app.schemas import NoteCreate, NoteRead, NotesPage, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post(
    "",
    response_model=NoteRead,
    status_code=status.HTTP_201_CREATED,
    summary="메모 생성",
)
async def create_note_endpoint(
    payload: NoteCreate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> NoteRead:
    """새 메모 한 건을 현재 사용자 소유로 만든다."""
    note = await crud.create_note(
        session, user_id=current_user.id, payload=payload
    )
    return NoteRead.model_validate(note)


@router.get(
    "",
    response_model=NotesPage,
    summary="내 메모 목록 (페이지네이션 + 태그/검색 필터)",
)
async def list_notes_endpoint(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 개수 (1~100)"),
    tag: str | None = Query(None, description="태그 필터(완전 일치)"),
    search: str | None = Query(None, description="제목·본문 부분 검색(대소문자 무시)"),
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> NotesPage:
    """현재 사용자의 메모만 돌려준다. 다른 사람 메모는 절대 포함되지 않는다."""
    items, total = await crud.list_notes(
        session,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        tag=tag,
        search=search,
    )
    return NotesPage(
        items=[NoteRead.model_validate(n) for n in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{note_id}",
    response_model=NoteRead,
    summary="메모 단건 조회 (본인 소유만)",
)
async def get_note_endpoint(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> NoteRead:
    note = await crud.get_owned_note(
        session, note_id=note_id, user_id=current_user.id
    )
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"메모 {note_id}를 찾을 수 없습니다",
        )
    return NoteRead.model_validate(note)


@router.patch(
    "/{note_id}",
    response_model=NoteRead,
    summary="메모 부분 수정 (본인 소유만)",
)
async def update_note_endpoint(
    note_id: int,
    payload: NoteUpdate,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> NoteRead:
    """본문에 보낸 필드만 갱신한다. 빈 본문(`{}`)은 정상이며 원본 그대로 돌아온다."""
    note = await crud.get_owned_note(
        session, note_id=note_id, user_id=current_user.id
    )
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"메모 {note_id}를 찾을 수 없습니다",
        )
    updated = await crud.update_note(session, note=note, payload=payload)
    return NoteRead.model_validate(updated)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="메모 삭제 (본인 소유만)",
)
async def delete_note_endpoint(
    note_id: int,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    note = await crud.get_owned_note(
        session, note_id=note_id, user_id=current_user.id
    )
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"메모 {note_id}를 찾을 수 없습니다",
        )
    await crud.delete_note(session, note=note)
    # 204는 본문이 없어야 하므로 return 값 없음.
