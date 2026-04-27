"""Pydantic 스키마 — 요청/응답의 모양과 토큰의 페이로드 형태.

응답 모델(UserRead)에는 `hashed_password`를 절대 포함시키지 않습니다.
이게 비밀번호 해시가 응답으로 새 나가는 사고를 막는 첫 번째 방어선입니다.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """회원가입 요청 본문(JSON).

    - email: 형식 검증된 이메일.
    - password: 8~64자. (Bcrypt의 72바이트 제한은 security.py에서 추가 검증)
    """

    email: EmailStr
    password: str = Field(min_length=8, max_length=64)


class UserRead(BaseModel):
    """회원 정보 응답.

    `model_config = ConfigDict(from_attributes=True)`는 SQLAlchemy 모델 인스턴스에서
    바로 속성을 읽어 직렬화할 수 있게 해줍니다(예전의 orm_mode=True 와 같은 의미).
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool
    created_at: datetime


class Token(BaseModel):
    """로그인 응답 — OAuth2 표준 형식과 동일하게 두 필드만 가진다.

    Swagger UI의 Authorize 버튼이 이 형식을 자동으로 인식해 토큰을 보관합니다.
    """

    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """디코딩된 JWT 페이로드의 타입화된 표현.

    - sub: subject. 보통 사용자 ID 문자열.
    - iat: issued at. 발급 시각(Unix timestamp).
    - exp: expiration. 만료 시각(Unix timestamp).
    """

    sub: str
    iat: int
    exp: int
