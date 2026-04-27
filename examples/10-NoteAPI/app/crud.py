"""서비스 레이어 — DB 작업만 담당.

라우터가 HTTP만 담당하고 비즈니스 로직(=DB 작업)은 모두 이 모듈에 모은다.
규칙:
- 모든 함수는 `AsyncSession`을 첫 인자로 받는다.
- HTTPException 같은 HTTP 개념은 여기서 알지 못한다(라우터의 책임).
- 결과로는 ORM 인스턴스 / None / 개수 / 모음 만 돌려준다.

이 파일의 모든 Note 관련 함수는 **`user_id` 인자를 받아 본인 소유 검사를 함께**
처리한다. 이렇게 두면 라우터 어느 곳에서 호출하든 "남의 메모를 만지는 사고"가
구조적으로 막힌다.
"""

from collections.abc import Sequence

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Note, User
from app.schemas import NoteCreate, NoteUpdate, UserCreate
from app.security import hash_password


# ── User ────────────────────────────────────────────────────────────


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """이메일로 사용자 한 명을 찾는다(없으면 None)."""
    result = await session.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(session: AsyncSession, payload: UserCreate) -> User:
    """새 사용자 생성 — 비밀번호는 Bcrypt로 해싱해서 저장한다.

    호출하는 쪽(routers/auth.py::signup)이 미리 이메일 중복을 검사한다.
    여기서는 단순히 INSERT만 책임진다.
    """
    user = User(
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


# ── Note ────────────────────────────────────────────────────────────


async def create_note(
    session: AsyncSession,
    *,
    user_id: int,
    payload: NoteCreate,
) -> Note:
    """새 메모 한 건을 만든다(작성자는 user_id로 박힌다)."""
    note = Note(
        title=payload.title,
        body=payload.body,
        tag=payload.tag,
        user_id=user_id,
    )
    session.add(note)
    await session.commit()
    await session.refresh(note)
    return note


async def get_owned_note(
    session: AsyncSession,
    *,
    note_id: int,
    user_id: int,
) -> Note | None:
    """본인 소유 메모 한 건 조회. 다른 사람 메모면 None.

    `user_id == current_user.id` 조건을 항상 함께 건다 — 이게 핵심 보안 패턴.
    """
    stmt = select(Note).where(Note.id == note_id, Note.user_id == user_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def list_notes(
    session: AsyncSession,
    *,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    tag: str | None = None,
    search: str | None = None,
) -> tuple[Sequence[Note], int]:
    """페이지네이션 + 태그 필터 + 키워드 검색 (모두 본인 메모 한정).

    Returns:
        (items, total)
        - items: 현재 페이지의 메모들
        - total: 같은 필터를 만족하는 전체 개수
    """
    base = select(Note).where(Note.user_id == user_id)

    if tag is not None and tag.strip() != "":
        base = base.where(Note.tag == tag)

    if search is not None and search.strip() != "":
        # 제목 또는 본문에 키워드가 포함된 행만(대소문자 무시).
        like = f"%{search}%"
        base = base.where(or_(Note.title.ilike(like), Note.body.ilike(like)))

    # 같은 필터를 적용한 별도 COUNT 쿼리로 전체 개수.
    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    page_stmt = (
        base.order_by(Note.updated_at.desc()).offset(skip).limit(limit)
    )
    items = (await session.execute(page_stmt)).scalars().all()

    return items, int(total)


async def update_note(
    session: AsyncSession,
    *,
    note: Note,
    payload: NoteUpdate,
) -> Note:
    """부분 수정. payload 에서 보낸 필드만 갱신한다.

    `model_dump(exclude_unset=True)`가 핵심.
    클라이언트가 명시적으로 보낸 필드만 dict에 들어가므로,
    "보낸 것만 갱신"이 자연스럽게 구현된다.
    """
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(note, key, value)

    await session.commit()
    await session.refresh(note)
    return note


async def delete_note(session: AsyncSession, *, note: Note) -> None:
    """메모 한 건 삭제(하드 삭제)."""
    await session.delete(note)
    await session.commit()
