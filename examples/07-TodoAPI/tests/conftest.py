"""pytest 전역 설정 / 공통 fixture.

이 파일이 하는 일은 단 두 가지다.

1. 매 테스트마다 깨끗한 in-memory SQLite 데이터베이스를 준비한다.
2. FastAPI 의 `get_session` 의존성을 우리 테스트용 세션으로 갈아 끼운다(의존성 오버라이드).

이렇게 해두면 라우터·crud 코드는 손대지 않고, 테스트만 별도의 DB 위에서 돈다.
"""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db import Base, get_session
from app.main import app


# in-memory SQLite. 프로세스가 살아 있는 동안만 존재하므로 매 테스트가 격리된다.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def engine():
    """테스트용 비동기 엔진. 매 테스트마다 새로 만든다."""
    engine = create_async_engine(TEST_DATABASE_URL)

    # 테이블을 만든다. 운영에서는 alembic 이 하지만, 테스트는 빠르게 metadata.create_all 로 끝낸다.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@pytest_asyncio.fixture
async def client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncClient, None]:
    """의존성 오버라이드된 비동기 HTTP 클라이언트.

    이 클라이언트로 보낸 요청은 진짜 네트워크가 아니라 ASGI 인터페이스로 곧장 앱에 전달된다.
    실제 서버를 띄우지 않으므로 빠르고 격리된다.
    """

    async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    # 앱의 get_session 의존성을 우리 테스트용으로 교체.
    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    # 다른 테스트에 영향이 가지 않도록 정리.
    app.dependency_overrides.clear()


@pytest.fixture
def sample_payload() -> dict:
    """기본 생성 페이로드. 테스트마다 살짝 바꿔 쓴다."""
    return {
        "title": "테스트 할 일",
        "description": "예시 설명",
        "is_done": False,
    }
