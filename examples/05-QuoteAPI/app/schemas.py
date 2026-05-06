"""명언(Quote) API에서 쓰는 Pydantic 모델 모음.

- QuoteBase: 입력·출력에 공통으로 들어가는 필드.
- QuoteCreate: 생성 요청 본문(POST).
- QuoteUpdate: 부분 수정 요청 본문(PATCH) — 모든 필드가 선택값.
- QuoteRead: 응답 모델(GET, POST/PUT/PATCH의 성공 응답).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class QuoteBase(BaseModel):
    """입력·출력에 공통으로 들어가는 필드들."""

    text: str = Field(..., min_length=1, max_length=500, description="명언 본문")
    author: str = Field(..., min_length=1, max_length=100, description="저자")


class QuoteCreate(QuoteBase):
    """POST /quotes 요청 본문."""


class QuoteUpdate(BaseModel):
    """PATCH /quotes/{id} 요청 본문 — 모든 필드가 선택값."""

    text: str | None = Field(default=None, min_length=1, max_length=500)
    author: str | None = Field(default=None, min_length=1, max_length=100)


class QuoteRead(QuoteBase):
    """모든 응답에서 쓰는 출력 모델."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
