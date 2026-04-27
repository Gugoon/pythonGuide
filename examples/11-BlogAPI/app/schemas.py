"""Pydantic 스키마 — 요청·응답의 모양과 토큰의 페이로드 형태.

응답 모델(UserRead 등)에는 `hashed_password` 같은 민감한 필드를 절대 포함시키지
않습니다. ORM 모델과 응답 스키마를 분리하는 가장 큰 이유입니다.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ── User ──

class UserCreate(BaseModel):
    """회원가입 요청 본문.

    - email: 형식 검증된 이메일 (Pydantic의 EmailStr).
    - password: 8~64자. (Bcrypt의 72바이트 제한은 security.py에서 추가 검증)
    - name: 닉네임. 1~80자.
    """

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    name: str = Field(min_length=1, max_length=80)


class UserRead(BaseModel):
    """회원 정보 응답 — 비밀번호 해시는 절대 포함하지 않는다."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    is_active: bool
    created_at: datetime


class AuthorSummary(BaseModel):
    """글·댓글 응답에 함께 노출하는 작성자 요약. 이메일은 비공개."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


# ── Tag ──

class TagSummary(BaseModel):
    """글 응답·태그 목록 응답 모두에 사용되는 태그 요약."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str


# ── Token / Auth ──

class Token(BaseModel):
    """로그인 응답 — OAuth2 표준 형식과 동일하게 두 필드만 가진다."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """디코딩된 JWT 페이로드의 타입화된 표현."""

    sub: str
    iat: int
    exp: int


# ── Post ──

class PostCreate(BaseModel):
    """POST /posts 요청 본문.

    - title: 1~200자.
    - body: 1~50,000자.
    - published: 기본 False(비공개). True면 즉시 공개.
    - tags: ["python", "fastapi"] 형태의 문자열 배열. 없으면 빈 배열.
    """

    title: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=50_000)
    published: bool = False
    tags: list[str] = Field(default_factory=list, max_length=10)


class PostUpdate(BaseModel):
    """PATCH /posts/{id} — 부분 수정. 모든 필드가 선택적.

    `tags`가 None이면 태그를 변경하지 않고, 빈 리스트면 모든 태그 제거,
    값 있는 리스트면 그것으로 교체합니다.
    """

    title: str | None = Field(default=None, min_length=1, max_length=200)
    body: str | None = Field(default=None, min_length=1, max_length=50_000)
    published: bool | None = None
    tags: list[str] | None = Field(default=None, max_length=10)


class PostRead(BaseModel):
    """GET /posts/{id} 와 목록의 각 항목 응답.

    응답에는 작성자 요약과 태그 목록을 같이 넣습니다(N+1 방지를 위해 라우트에서
    selectinload로 미리 가져옵니다).
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    body: str
    published: bool
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    author: AuthorSummary
    tags: list[TagSummary]


class PostList(BaseModel):
    """페이지네이션된 글 목록."""

    model_config = ConfigDict(from_attributes=True)

    items: list[PostRead]
    page: int
    size: int
    total: int


# ── Comment ──

class CommentCreate(BaseModel):
    """POST /posts/{id}/comments 요청 본문."""

    body: str = Field(min_length=1, max_length=2000)


class CommentUpdate(BaseModel):
    """PATCH /comments/{id} 요청 본문."""

    body: str = Field(min_length=1, max_length=2000)


class CommentRead(BaseModel):
    """댓글 한 건 응답."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    post_id: int
    body: str
    created_at: datetime
    author: AuthorSummary
