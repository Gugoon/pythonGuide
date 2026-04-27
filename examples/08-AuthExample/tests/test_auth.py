"""인증 흐름 테스트.

테스트 묶음:
- 정상 흐름(signup → login → me)
- 회원가입 실패(중복, 너무 긴 비번)
- 로그인 실패(잘못된 비번, 존재하지 않는 사용자)
- 보호된 라우트 접근 실패(토큰 없음, 변조 토큰, 만료 토큰)
- 인가 검사(일반은 403, 관리자는 200)
- 헬스체크
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from httpx import AsyncClient
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import User
from app.security import create_access_token


settings = get_settings()


async def test_signup_login_me_full_flow(
    client: AsyncClient,
    signup_payload: dict[str, str],
    login_form: dict[str, str],
) -> None:
    """전형적인 성공 흐름: 회원가입 → 로그인 → /users/me."""
    # 1) 회원가입
    r = await client.post("/auth/signup", json=signup_payload)
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["email"] == signup_payload["email"]
    assert body["is_active"] is True
    assert body["is_admin"] is False
    # 응답에 비밀번호 해시가 새 나가지 않는지 확인 — 가장 중요한 안전장치.
    assert "hashed_password" not in body
    assert "password" not in body

    # 2) 로그인
    r = await client.post("/auth/login", data=login_form)
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    assert r.json()["token_type"] == "bearer"
    assert isinstance(token, str) and len(token) > 0

    # 3) 보호된 라우트
    r = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200, r.text
    assert r.json()["email"] == signup_payload["email"]


async def test_signup_duplicate_email_returns_409(
    client: AsyncClient,
    signup_payload: dict[str, str],
) -> None:
    """같은 이메일로 두 번 가입하면 409."""
    r1 = await client.post("/auth/signup", json=signup_payload)
    assert r1.status_code == 201

    r2 = await client.post("/auth/signup", json=signup_payload)
    assert r2.status_code == 409
    assert "이미" in r2.json()["detail"]


async def test_signup_email_normalization(
    client: AsyncClient,
) -> None:
    """이메일 대소문자가 달라도 같은 사용자로 처리(소문자로 정규화)."""
    await client.post(
        "/auth/signup",
        json={"email": "Alice@Example.com", "password": "hunter22hunter"},
    )
    # 정확히 같은 이메일을 소문자로 다시 시도 → 409
    r = await client.post(
        "/auth/signup",
        json={"email": "alice@example.com", "password": "another88pass"},
    )
    assert r.status_code == 409


async def test_signup_password_too_long_returns_422(
    client: AsyncClient,
) -> None:
    """비밀번호가 너무 길면 422.

    Pydantic 스키마(max_length=64)에서 먼저 막힌다.
    """
    payload = {
        "email": "longpw@example.com",
        "password": "a" * 200,
    }
    r = await client.post("/auth/signup", json=payload)
    assert r.status_code == 422


async def test_login_wrong_password_returns_401(
    client: AsyncClient,
    signup_payload: dict[str, str],
) -> None:
    """잘못된 비밀번호로 로그인하면 401, 메시지는 통일."""
    await client.post("/auth/signup", json=signup_payload)

    r = await client.post(
        "/auth/login",
        data={
            "username": signup_payload["email"],
            "password": "wrongpassword",
        },
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다"


async def test_login_nonexistent_user_returns_401(client: AsyncClient) -> None:
    """존재하지 않는 사용자로 로그인해도 같은 메시지(정보 누설 방지)."""
    r = await client.post(
        "/auth/login",
        data={
            "username": "nobody@example.com",
            "password": "anything",
        },
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다"


async def test_me_without_token_returns_401(client: AsyncClient) -> None:
    """토큰 없이 보호된 라우트에 접근하면 401."""
    r = await client.get("/users/me")
    assert r.status_code == 401


async def test_me_with_tampered_token_returns_401(client: AsyncClient) -> None:
    """변조된 토큰은 서명 검증 실패 → 401."""
    bogus = jwt.encode(
        {"sub": "999", "iat": 0, "exp": 9999999999},
        "definitely-not-the-real-secret",
        algorithm="HS256",
    )
    r = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {bogus}"},
    )
    assert r.status_code == 401


async def test_me_with_expired_token_returns_401(
    client: AsyncClient,
    signup_payload: dict[str, str],
) -> None:
    """만료된 토큰은 401, 메시지는 '토큰이 만료되었습니다'."""
    r = await client.post("/auth/signup", json=signup_payload)
    assert r.status_code == 201
    user_id = r.json()["id"]

    # 만료가 이미 지난 토큰을 직접 만든다.
    now = datetime.now(timezone.utc)
    expired_payload = {
        "sub": str(user_id),
        "iat": int((now - timedelta(hours=2)).timestamp()),
        "exp": int((now - timedelta(hours=1)).timestamp()),
    }
    expired_token = jwt.encode(
        expired_payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    r = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "토큰이 만료되었습니다"


async def test_admin_route_forbidden_for_normal_user(
    client: AsyncClient,
    signup_payload: dict[str, str],
    login_form: dict[str, str],
) -> None:
    """일반 사용자가 관리자 라우트를 부르면 403."""
    await client.post("/auth/signup", json=signup_payload)
    r = await client.post("/auth/login", data=login_form)
    token = r.json()["access_token"]

    r = await client.get(
        "/users/admin/ping",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403
    assert "관리자" in r.json()["detail"]


async def test_admin_route_ok_for_admin(
    client: AsyncClient,
    db_session: AsyncSession,
    signup_payload: dict[str, str],
    login_form: dict[str, str],
) -> None:
    """관리자(`is_admin=True`)는 관리자 라우트에서 200을 받는다.

    db_session 픽스처는 client 픽스처와 같은 인메모리 엔진을 본다(_engine_and_factory 공유).
    """
    r = await client.post("/auth/signup", json=signup_payload)
    assert r.status_code == 201

    # is_admin = True 로 직접 변경
    await db_session.execute(
        update(User)
        .where(User.email == signup_payload["email"])
        .values(is_admin=True)
    )
    await db_session.commit()

    r = await client.post("/auth/login", data=login_form)
    token = r.json()["access_token"]

    r = await client.get(
        "/users/admin/ping",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert "admin" in r.json()["message"].lower()


async def test_inactive_user_cannot_login(
    client: AsyncClient,
    db_session: AsyncSession,
    signup_payload: dict[str, str],
    login_form: dict[str, str],
) -> None:
    """비활성화된 계정은 로그인이 거부된다."""
    r = await client.post("/auth/signup", json=signup_payload)
    assert r.status_code == 201

    await db_session.execute(
        update(User)
        .where(User.email == signup_payload["email"])
        .values(is_active=False)
    )
    await db_session.commit()

    r = await client.post("/auth/login", data=login_form)
    assert r.status_code == 401


async def test_token_for_unknown_user_returns_401(client: AsyncClient) -> None:
    """DB에 없는 user_id로 만든 토큰은 401."""
    token = create_access_token(subject="999999")
    r = await client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 401


async def test_health(client: AsyncClient) -> None:
    """헬스체크는 인증 없이 200."""
    r = await client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
