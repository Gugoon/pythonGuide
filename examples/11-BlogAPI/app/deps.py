"""FastAPI 의존성 함수 모음.

- `get_current_user`: 보호된 라우트가 받는 인증 의존성. 토큰이 없으면 401.
- `get_optional_user`: 토큰이 없어도 통과하되, 있으면 검증해서 사용자 객체를 반환.
                       공개·비공개 글을 같은 라우트가 분기 처리할 때 사용.
"""

from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.security import decode_access_token

# Swagger UI의 Authorize 버튼이 사용할 로그인 엔드포인트.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# auto_error=False 로 두면 토큰이 없어도 None을 반환할 뿐, 401을 던지지 않는다.
# 공개 라우트에서 "로그인했으면 본인 비공개 글까지 보여주기" 같은 분기에 사용한다.
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/auth/login", auto_error=False
)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """헤더의 Bearer 토큰을 검증하고 현재 사용자를 돌려준다."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="유효하지 않은 인증 정보입니다",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="토큰이 만료되었습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise credentials_exc

    try:
        user_id = int(payload.sub)
    except (TypeError, ValueError):
        raise credentials_exc

    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_exc

    return user


async def get_optional_user(
    session: AsyncSession = Depends(get_session),
    token: str | None = Depends(oauth2_scheme_optional),
) -> User | None:
    """토큰이 없으면 None, 있으면 검증해서 사용자를 돌려준다.

    잘못된/만료된 토큰이면 None으로 처리합니다(공개 라우트의 사용성 우선).
    엄격한 거부가 필요한 라우트는 `get_current_user`를 쓰세요.
    """
    if token is None:
        return None

    try:
        payload = decode_access_token(token)
    except jwt.InvalidTokenError:
        return None

    try:
        user_id = int(payload.sub)
    except (TypeError, ValueError):
        return None

    user = await session.get(User, user_id)
    if user is None or not user.is_active:
        return None
    return user
