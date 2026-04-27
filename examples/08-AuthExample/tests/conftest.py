"""테스트용 픽스처 — 매 테스트마다 새로운 인메모리 DB를 띄운다.

핵심 트릭:
1. 인메모리 SQLite 엔진을 만들고 그 위에 테이블을 새로 만든다.
2. FastAPI 앱의 `get_session` 의존성을 이 엔진을 쓰는 함수로 덮어쓴다.
3. httpx의 AsyncClient + ASGITransport로 실제 요청을 보낸다.

테스트 케이스가 DB를 직접 만져야 하면 `db_session` 픽스처를 함께 받는다.
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
        # StaticPool 을 써야 같은 연결이 재사용되어 여러 세션에서 같은 인메모리 DB를 본다.
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


@pytest.fixture
def signup_payload() -> dict[str, str]:
    """기본 회원가입 입력값."""
    return {"email": "alice@example.com", "password": "hunter22hunter"}


@pytest.fixture
def login_form() -> dict[str, str]:
    """기본 로그인 폼 입력값(필드 이름은 OAuth2 표준대로 username)."""
    return {"username": "alice@example.com", "password": "hunter22hunter"}
