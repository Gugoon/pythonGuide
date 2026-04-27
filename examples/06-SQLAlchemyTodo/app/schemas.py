"""Pydantic 스키마 — 요청·응답의 모양을 정의.

ORM 모델(models.Todo)과는 분리된 클래스. 두 가지를 분리하면
"DB 가 가지는 정보"와 "외부 API 가 노출/받는 정보"를 독립적으로 진화시킬 수 있다.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoCreate(BaseModel):
    """POST /todos 의 요청 본문."""

    title: str = Field(min_length=1, max_length=200, description="할 일 제목")


class TodoUpdate(BaseModel):
    """PATCH /todos/{id} 의 요청 본문 — 부분 수정.

    모든 필드가 선택적. 보내지 않은 필드는 기존 값을 유지한다.
    """

    title: str | None = Field(default=None, min_length=1, max_length=200)
    is_done: bool | None = None


class TodoRead(BaseModel):
    """GET 응답에 사용하는 스키마."""

    id: int
    title: str
    is_done: bool
    created_at: datetime

    # ORM 객체(Todo 인스턴스)에서 그대로 값을 읽어 만들 수 있게 한다.
    # Pydantic v1 의 orm_mode = True 와 동일한 의미.
    model_config = ConfigDict(from_attributes=True)
