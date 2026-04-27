"""Pydantic 스키마(= 요청/응답 DTO).

ORM 모델(`models.Todo`)과 분리되어 있습니다. 이유:
- ORM 은 DB 표현, Pydantic 은 외부 API 표현. 둘은 따로 진화할 수 있어야 한다.
- 응답에서 민감한 필드(예: password_hash)가 실수로 새는 것을 막기 위함.
- 부분 수정(PATCH) 처럼 "일부 필드만" 다루는 변형 스키마를 자유롭게 만들 수 있다.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoBase(BaseModel):
    """공통 필드. 다른 스키마들이 상속해서 재사용한다."""

    title: str = Field(min_length=1, max_length=200, description="할 일 제목")
    description: str | None = Field(
        default=None,
        max_length=2000,
        description="자유 형식 설명",
    )
    is_done: bool = Field(default=False, description="완료 여부")


class TodoCreate(TodoBase):
    """POST /todos 요청 본문 스키마.

    필수 필드는 `title` 하나, 나머지는 기본값이 채워진다.
    """


class TodoUpdate(BaseModel):
    """PATCH /todos/{id} 요청 본문 스키마.

    모든 필드가 Optional 이고 기본값이 None.
    클라이언트는 바꾸고 싶은 필드만 보내면 된다.
    """

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)
    is_done: bool | None = None


class TodoRead(TodoBase):
    """API 응답으로 내보내는 스키마.

    `from_attributes=True` 가 핵심. ORM 인스턴스(Todo) 를 그대로 넘겨도
    Pydantic 이 속성을 읽어 변환해 준다.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TodosPage(BaseModel):
    """GET /todos 의 응답.

    - items: 현재 페이지에 포함된 Todo 들
    - total: 필터 조건을 만족하는 전체 개수 (페이지 수 계산용)
    - skip / limit: 클라이언트가 보낸 페이지네이션 인자를 그대로 반사
    """

    items: list[TodoRead]
    total: int
    skip: int
    limit: int
