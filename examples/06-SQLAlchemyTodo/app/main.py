"""FastAPI 앱 본체 — 모든 라우트를 한 파일에 모은다(07장에서 라우터 분리).

이 파일에는 다음 6개의 라우트가 있다.
    GET    /health         — 헬스 체크
    POST   /todos          — 새 todo 생성
    GET    /todos          — 전체 목록(최신순)
    GET    /todos/{id}     — 단건 조회
    PATCH  /todos/{id}     — 부분 수정
    DELETE /todos/{id}     — 삭제
"""

from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Todo
from app.schemas import TodoCreate, TodoRead, TodoUpdate

app = FastAPI(
    title="SQLAlchemy Todo",
    description="FastAPI 가이드 06장 — SQLAlchemy 2.0 (async) + Alembic 예제",
    version="0.1.0",
)


# ─────────────────────────────────────────────────────────
# 헬스 체크
# ─────────────────────────────────────────────────────────
@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    """앱이 살아 있는지 확인하는 단순 엔드포인트.

    배포 환경의 로드밸런서/오케스트레이터가 정기적으로 호출한다.
    """
    return {"status": "ok"}


# ─────────────────────────────────────────────────────────
# 생성 (POST /todos)
# ─────────────────────────────────────────────────────────
@app.post(
    "/todos",
    response_model=TodoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["todos"],
)
async def create_todo(
    payload: TodoCreate,
    session: AsyncSession = Depends(get_session),
) -> Todo:
    """새 할 일 한 건을 만든다.

    요청 본문: {"title": "..."}
    응답: 생성된 todo (id, created_at 포함)
    """
    todo = Todo(title=payload.title)
    session.add(todo)

    # commit 은 get_session 의존성이 라우트 종료 후 알아서 한다.
    # 다만 응답에 id/created_at 을 정확히 담으려면 flush + refresh 가 필요하다.
    await session.flush()
    await session.refresh(todo)
    return todo


# ─────────────────────────────────────────────────────────
# 목록 (GET /todos)
# ─────────────────────────────────────────────────────────
@app.get("/todos", response_model=list[TodoRead], tags=["todos"])
async def list_todos(
    session: AsyncSession = Depends(get_session),
) -> list[Todo]:
    """전체 할 일 목록을 최신순으로 돌려준다."""
    stmt = select(Todo).order_by(Todo.created_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())


# ─────────────────────────────────────────────────────────
# 단건 조회 (GET /todos/{id})
# ─────────────────────────────────────────────────────────
@app.get("/todos/{todo_id}", response_model=TodoRead, tags=["todos"])
async def get_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
) -> Todo:
    """id 로 할 일 한 건을 조회. 없으면 404."""
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )
    return todo


# ─────────────────────────────────────────────────────────
# 부분 수정 (PATCH /todos/{id})
# ─────────────────────────────────────────────────────────
@app.patch("/todos/{todo_id}", response_model=TodoRead, tags=["todos"])
async def update_todo(
    todo_id: int,
    payload: TodoUpdate,
    session: AsyncSession = Depends(get_session),
) -> Todo:
    """할 일을 부분 수정한다.

    payload 에 명시적으로 보낸 필드만 갱신한다.
    예: {"is_done": true} 만 보내면 title 은 그대로.
    """
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )

    # exclude_unset=True : 클라이언트가 명시적으로 보낸 필드만 dict 로.
    # 보내지 않은 필드를 None 으로 덮어쓰는 사고를 막는다.
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(todo, key, value)

    # SQLAlchemy 가 변경된 속성을 추적해 UPDATE 문을 자동 생성한다.
    await session.flush()
    await session.refresh(todo)
    return todo


# ─────────────────────────────────────────────────────────
# 삭제 (DELETE /todos/{id})
# ─────────────────────────────────────────────────────────
@app.delete(
    "/todos/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["todos"],
)
async def delete_todo(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    """할 일을 영구 삭제한다(하드 삭제).

    소프트 삭제(is_deleted 플래그) 패턴은 11장에서 다룬다.
    """
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} not found",
        )

    await session.delete(todo)
    # 커밋은 get_session 이 라우트 종료 후 알아서 한다.
    return None
