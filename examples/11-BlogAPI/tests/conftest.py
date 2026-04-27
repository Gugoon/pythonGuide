"""테스트용 픽스처 — 매 테스트마다 새로운 인메모리 SQLite DB를 띄운다.

운영은 MySQL이지만 테스트는 인메모리 SQLite로 빠르게 돕니다.
SQLAlchemy 2.0의 ORM 코드는 두 DB에서 동일하게 동작합니다(이 가이드의 모델과
쿼리는 둘 모두에서 통합니다). 테스트 픽스처에서 `get_session`만 갈아끼웁니다.

핵심 트릭:
1. StaticPool로 단일 연결을 공유해서 여러 세션이 같은 인메모리 DB를 본다.
2. `Base.metadata.create_all`로 ORM 모델로부터 테이블을 직접 만든다(Alembic 미사용).
3. FastAPI 앱의 `get_session` 의존성을 이 엔진을 쓰는 함수로 덮어쓴다.
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
    """엔진과 세션 팩토리를 만들고, 테이블도 같이 만들어 둔다."""
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


# ── 헬퍼 픽스처 ──

@pytest.fixture
def alice_payload() -> dict[str, str]:
    return {
        "email": "alice@example.com",
        "password": "hunter22hunter",
        "name": "Alice",
    }


@pytest.fixture
def bob_payload() -> dict[str, str]:
    return {
        "email": "bob@example.com",
        "password": "anothersecret77",
        "name": "Bob",
    }


@pytest_asyncio.fixture
async def alice_token(client: AsyncClient, alice_payload: dict[str, str]) -> str:
    """회원가입 + 로그인까지 마친 alice의 액세스 토큰."""
    r = await client.post("/auth/signup", json=alice_payload)
    assert r.status_code == 201, r.text

    r = await client.post(
        "/auth/login",
        data={"username": alice_payload["email"], "password": alice_payload["password"]},
    )
    assert r.status_code == 200, r.text
    return str(r.json()["access_token"])


@pytest_asyncio.fixture
async def bob_token(client: AsyncClient, bob_payload: dict[str, str]) -> str:
    r = await client.post("/auth/signup", json=bob_payload)
    assert r.status_code == 201, r.text

    r = await client.post(
        "/auth/login",
        data={"username": bob_payload["email"], "password": bob_payload["password"]},
    )
    assert r.status_code == 200, r.text
    return str(r.json()["access_token"])
