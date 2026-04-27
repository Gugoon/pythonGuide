"""인증 관련 라우트 — 회원가입과 로그인.

`/auth` 프리픽스 아래의 두 엔드포인트는 토큰이 없어도 부를 수 있는 공개 라우트다.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.db import get_session
from app.models import User
from app.schemas import Token, UserCreate, UserRead
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="이메일과 비밀번호로 새 계정을 만든다. 비밀번호는 Bcrypt로 해싱해서 저장된다.",
)
async def signup(
    payload: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> User:
    """이메일 중복 체크 → 비밀번호 해싱 → 사용자 저장."""
    # 이메일 정규화 — 대소문자 무시 일관성을 위해 소문자로 통일한다.
    email = payload.email.lower()

    if await crud.get_user_by_email(session, email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 사용 중인 이메일입니다",
        )

    try:
        user = await crud.create_user(
            session,
            UserCreate(email=email, password=payload.password),
        )
    except ValueError as e:
        # 한국어 비밀번호가 너무 길어 72바이트를 넘기면 여기로 떨어진다.
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )

    return user


@router.post(
    "/login",
    response_model=Token,
    summary="로그인",
    description=(
        "form 필드 `username`(=이메일)과 `password`를 받아 액세스 토큰을 돌려준다. "
        "Swagger UI의 Authorize 버튼이 이 엔드포인트를 호출한다."
    ),
)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> Token:
    """비번 검증 → 토큰 발급."""
    email = form.username.lower()
    user = await crud.get_user_by_email(session, email)

    # 사용자 없음 / 비밀번호 불일치 모두 같은 메시지로 응답한다.
    # 구분해서 알려주면 "이 이메일은 가입돼 있다"는 정보를 공격자에게 주게 된다.
    if user is None or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비활성화된 계정입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)
