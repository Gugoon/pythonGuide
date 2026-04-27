"""FastAPI 의존성 함수 모음.

`Depends(get_current_user)`로 보호된 라우트에 현재 사용자를 주입한다.
`get_current_active_user`는 활성 계정만 통과시킨다.
"""

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.security import decode_access_token

# tokenUrl은 Swagger UI의 "Authorize" 버튼이 사용할 로그인 엔드포인트 경로.
# 실제 라우트와 정확히 일치해야 자동 문서에서 로그인이 통한다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session),
) -> User:
    """헤더의 Bearer 토큰을 검증하고 현재 사용자를 돌려준다.

    실패 케이스마다 401을 던지되, 만료와 그 외 오류를 메시지로만 구분한다.
    """
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
        # 서명 불일치, 형식 오류, 알고리즘 불일치 등 모든 검증 실패
        raise credentials_exc

    # sub은 문자열로 들어오므로 정수 변환 가능 여부를 확인한다.
    try:
        user_id = int(payload.sub)
    except (TypeError, ValueError):
        raise credentials_exc

    user = await session.get(User, user_id)
    if user is None:
        raise credentials_exc

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """활성 계정만 통과. 비활성화된 계정은 401."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비활성화된 계정입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user
