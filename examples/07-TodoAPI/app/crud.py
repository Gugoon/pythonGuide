"""서비스 레이어(=비즈니스 로직).

라우터(`app/routers/todos.py`) 가 HTTP 만 담당한다면, 이 모듈은 DB 만 담당한다.
이 둘을 분리하는 이유는 다음과 같다.

1. 같은 비즈니스 로직을 다른 진입점(예: CLI, 백그라운드 작업)에서도 재사용할 수 있다.
2. 라우터의 단위 테스트를 작성할 때 crud 함수만 모킹할 수 있다.
3. 라우터 한 함수가 너무 길어지지 않는다(가독성).

규칙:
- 이 모듈의 함수는 `AsyncSession` 을 첫 인자로 받는다.
- HTTPException 같은 HTTP 개념은 여기서 알지 못한다. 그건 라우터의 책임.
- 결과로는 ORM 인스턴스 또는 None / 개수 / 모음 만 돌려준다.
"""

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Todo
from app.schemas import TodoCreate, TodoUpdate


async def create_todo(session: AsyncSession, payload: TodoCreate) -> Todo:
    """새 Todo 한 건 만들기."""
    todo = Todo(
        title=payload.title,
        description=payload.description,
        is_done=payload.is_done,
    )
    session.add(todo)
    await session.commit()
    # commit 이후 자동 증가된 id 등을 객체에 다시 채워 넣기 위해 refresh.
    await session.refresh(todo)
    return todo


async def get_todo(session: AsyncSession, todo_id: int) -> Todo | None:
    """단건 조회. 없으면 None.

    `session.get` 은 기본 키 한 건을 빠르게 가져오는 헬퍼다.
    더 복잡한 조건이 붙으면 select() + execute() 를 쓴다.
    """
    return await session.get(Todo, todo_id)


async def list_todos(
    session: AsyncSession,
    *,
    skip: int = 0,
    limit: int = 20,
    is_done: bool | None = None,
) -> tuple[Sequence[Todo], int]:
    """페이지네이션과 필터를 적용한 목록 조회.

    돌려주는 값은 (items, total) 두 쌍.
    - items: 현재 페이지에 들어갈 Todo 들
    - total: 필터 조건을 만족하는 전체 개수 (페이지 수 계산용)
    """
    base = select(Todo)
    if is_done is not None:
        base = base.where(Todo.is_done == is_done)

    # 전체 개수: 같은 필터를 적용한 별도의 COUNT 쿼리.
    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await session.execute(count_stmt)).scalar_one()

    # 페이지: 정렬 + skip + limit 을 붙인 쿼리.
    # 최신 항목이 위로 오도록 created_at 내림차순.
    page_stmt = base.order_by(Todo.created_at.desc()).offset(skip).limit(limit)
    items = (await session.execute(page_stmt)).scalars().all()

    return items, int(total)


async def update_todo(
    session: AsyncSession,
    todo: Todo,
    payload: TodoUpdate,
) -> Todo:
    """부분 수정. payload 에서 보낸 필드만 갱신한다.

    `model_dump(exclude_unset=True)` 가 핵심.
    - exclude_unset=True 면 클라이언트가 명시적으로 보낸 필드만 dict 에 들어간다.
    - 기본값이 None 인 필드를 안 보내면 dict 에서 제외된다.
    - 그래서 "보낸 것만 갱신"이 자연스럽게 구현된다.
    """
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(todo, key, value)

    await session.commit()
    await session.refresh(todo)
    return todo


async def delete_todo(session: AsyncSession, todo: Todo) -> None:
    """Todo 한 건 삭제."""
    await session.delete(todo)
    await session.commit()
