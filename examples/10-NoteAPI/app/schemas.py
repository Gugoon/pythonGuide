"""Pydantic 스키마 — 요청/응답의 모양과 토큰 페이로드.

응답 모델(`UserRead`)에 절대 비밀번호 해시(`hashed_password`)를 포함시키지 않습니다.
이게 비밀번호 해시가 응답으로 새 나가는 사고를 막는 첫 번째 방어선입니다.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── User ────────────────────────────────────────────────────────────


class UserCreate(BaseModel):
    """회원가입 요청 본문(JSON).

    - email: 형식 검증된 이메일.
    - password: 8~64자. (Bcrypt의 72바이트 제한은 security.py에서 추가 검증)
    """

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class UserRead(BaseModel):
    """회원 정보 응답."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime


# ── Auth ────────────────────────────────────────────────────────────


class Token(BaseModel):
    """로그인 응답 — OAuth2 표준 형식과 동일하게 두 필드만 가진다.

    Swagger UI의 Authorize 버튼이 이 형식을 자동으로 인식해 토큰을 보관합니다.
    """

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """디코딩된 JWT 페이로드의 타입화된 표현."""

    sub: str
    iat: int
    exp: int


# ── Note ────────────────────────────────────────────────────────────


class NoteBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=10_000)
    tag: str | None = Field(default=None, max_length=50)


class NoteCreate(NoteBase):
    """POST /notes 요청 본문."""


class NoteUpdate(BaseModel):
    """PATCH /notes/{id} — 부분 수정. 모든 필드 Optional."""

    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = Field(default=None, min_length=1, max_length=10_000)
    tag: str | None = Field(default=None, max_length=50)


class NoteRead(NoteBase):
    """GET 응답에 사용. ORM 인스턴스를 그대로 받을 수 있다."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class NotesPage(BaseModel):
    """페이지네이션이 적용된 목록 응답."""

    items: list[NoteRead]
    total: int
    skip: int
    limit: int
