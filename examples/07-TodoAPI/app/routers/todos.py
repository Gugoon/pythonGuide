"""Todo 도메인 라우터.

이 모듈의 책임은 HTTP 다.
- 요청 본문 파싱 / 쿼리 파라미터 / 경로 파라미터
- 적절한 status_code 와 응답 모델
- 에러를 HTTPException 으로 일관되게 변환

비즈니스 로직(=DB 작업) 은 모두 `app.crud` 에 위임한다.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.db import get_session
from app.schemas import TodoCreate, TodoRead, TodosPage, TodoUpdate

# prefix="/todos" 를 한 번만 적어두면 모든 라우트에 자동으로 붙는다.
# tags=["todos"] 는 /docs 의 그룹 라벨.
router = APIRouter(prefix="/todos", tags=["todos"])


@router.post(
    "",
    response_model=TodoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Todo 생성",
)
async def create_todo_endpoint(
    payload: TodoCreate,
    session: AsyncSession = Depends(get_session),
) -> TodoRead:
    """새 Todo 한 건을 만든다.

    성공 시 `201 Created` 와 함께 만들어진 Todo 를 돌려준다.
    제목이 비었거나 길이를 벗어나면 Pydantic 이 자동으로 422 를 돌려준다.
    """
    todo = await crud.create_todo(session, payload)
    return TodoRead.model_validate(todo)


@router.get(
    "",
    response_model=TodosPage,
    summary="Todo 목록 조회 (페이지네이션 + 필터)",
)
async def list_todos_endpoint(
    skip: int = Query(0, ge=0, description="건너뛸 개수"),
    limit: int = Query(20, ge=1, le=100, description="가져올 개수 (1~100)"),
    is_done: bool | None = Query(None, description="완료 여부 필터"),
    session: AsyncSession = Depends(get_session),
) -> TodosPage:
    """skip/limit 페이지네이션과 is_done 필터를 지원한다.

    Query(...) 의 `ge` 와 `le` 는 자동 검증 제약이다.
    예) `limit=200` 으로 호출하면 FastAPI 가 자동으로 422 를 돌려준다.
    """
    items, total = await crud.list_todos(
        session, skip=skip, limit=limit, is_done=is_done
    )
    return TodosPage(
        items=[TodoRead.model_validate(t) for t in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{todo_id}",
    response_model=TodoRead,
    summary="Todo 단건 조회",
)
async def get_todo_endpoint(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
) -> TodoRead:
    todo = await crud.get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} 를 찾을 수 없습니다",
        )
    return TodoRead.model_validate(todo)


@router.patch(
    "/{todo_id}",
    response_model=TodoRead,
    summary="Todo 부분 수정",
)
async def update_todo_endpoint(
    todo_id: int,
    payload: TodoUpdate,
    session: AsyncSession = Depends(get_session),
) -> TodoRead:
    """본문에 보낸 필드만 갱신한다.

    아무 필드도 보내지 않은 빈 본문(`{}`) 도 정상이며,
    이 경우 데이터는 그대로 두고 응답으로 현재 상태를 돌려준다.
    """
    todo = await crud.get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} 를 찾을 수 없습니다",
        )
    updated = await crud.update_todo(session, todo, payload)
    return TodoRead.model_validate(updated)


@router.delete(
    "/{todo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Todo 삭제",
)
async def delete_todo_endpoint(
    todo_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    """삭제 성공 시 본문 없이 204 를 돌려준다."""
    todo = await crud.get_todo(session, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo {todo_id} 를 찾을 수 없습니다",
        )
    await crud.delete_todo(session, todo)
    # 204 는 본문이 없어야 하므로 return 값 없음.
