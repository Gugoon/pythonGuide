"""테스트용 픽스처 — 매 테스트마다 새로운 인메모리 SQLite DB.

운영은 PostgreSQL이지만 테스트는 의존성을 줄이고 빠른 피드백을 위해
in-memory SQLite를 쓴다. SQLAlchemy 모델 코드는 그대로 동작한다.

핵심 트릭:
1. 인메모리 SQLite 엔진을 만들고 그 위에 테이블을 새로 만든다.
2. FastAPI 앱의 `get_session` 의존성을 이 엔진을 쓰는 함수로 덮어쓴다.
3. httpx의 AsyncClient + ASGITransport로 실제 요청을 보낸다.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import app


@pytest_asyncio.fixture
async def _engine_and_factory():
    """엔진과 세션 팩토리를 만들고, 테이블도 같이 만들어 둔다.

    StaticPool을 써야 같은 메모리 DB에 여러 세션이 공유 접근할 수 있다.
    (기본 풀은 연결마다 별도 메모리 공간을 잡아 테스트가 깨진다.)
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine, SessionLocal

    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(_engine_and_factory) -> AsyncIterator[AsyncSession]:
    """테스트 안에서 DB를 직접 만질 때 쓰는 세션."""
    _engine, SessionLocal = _engine_and_factory
    async with SessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(_engine_and_factory) -> AsyncIterator[AsyncClient]:
    """테스트용 FastAPI 클라이언트 — get_session을 인메모리 엔진으로 덮어쓴다."""
    _engine, SessionLocal = _engine_and_factory

    async def override_get_session() -> AsyncIterator[AsyncSession]:
        async with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ── 자주 쓰는 페이로드 ──────────────────────────────────────────────


@pytest.fixture
def alice_signup() -> dict[str, str]:
    return {"email": "alice@example.com", "password": "alicepass1234"}


@pytest.fixture
def alice_login() -> dict[str, str]:
    """OAuth2 표준대로 form 필드 이름은 username."""
    return {"username": "alice@example.com", "password": "alicepass1234"}


@pytest.fixture
def bob_signup() -> dict[str, str]:
    return {"email": "bob@example.com", "password": "bobpass12345"}


@pytest.fixture
def bob_login() -> dict[str, str]:
    return {"username": "bob@example.com", "password": "bobpass12345"}


# ── 헬퍼 ────────────────────────────────────────────────────────────


async def signup_and_login(
    client: AsyncClient, signup: dict[str, str], login: dict[str, str]
) -> str:
    """회원가입 → 로그인 한 흐름으로 액세스 토큰을 돌려준다."""
    r = await client.post("/auth/signup", json=signup)
    assert r.status_code == 201, r.text
    r = await client.post("/auth/login", data=login)
    assert r.status_code == 200, r.text
    return r.json()["access_token"]
