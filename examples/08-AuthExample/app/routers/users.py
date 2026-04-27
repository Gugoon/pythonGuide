"""사용자 관련 라우트 — 자기 정보 조회, 관리자 데모.

이 모듈의 모든 라우트는 인증이 필요한 보호된 엔드포인트입니다.
`Depends(get_current_user)` 또는 `Depends(get_current_admin)`로 검증합니다.
"""

from fastapi import APIRouter, Depends

from app.deps import get_current_admin, get_current_user
from app.models import User
from app.schemas import UserRead

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="내 정보",
    description="Bearer 토큰의 주인 정보를 돌려준다.",
)
async def me(current_user: User = Depends(get_current_user)) -> User:
    """라우트 본문은 한 줄. 모든 검증은 의존성에서 끝났다."""
    return current_user


@router.get(
    "/admin/ping",
    summary="관리자 핑 (인가 데모)",
    description="`is_admin=True`인 사용자만 200을 받는다. 일반 사용자는 403.",
)
async def admin_ping(admin: User = Depends(get_current_admin)) -> dict[str, str]:
    """인가 검사가 끝난 admin 객체가 들어온다."""
    return {"message": f"Hello, admin {admin.email}!"}
