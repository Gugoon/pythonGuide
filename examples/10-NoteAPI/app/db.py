"""비동기 SQLAlchemy 엔진과 세션 의존성.

라우트는 `Depends(get_session)`으로 한 요청당 하나의 AsyncSession을 받습니다.
06장에서 다룬 패턴과 같습니다.
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()

# 비동기 엔진 — 운영은 PostgreSQL(asyncpg), 테스트는 conftest.py에서 별도 엔진을 만든다.
# echo=True로 두면 실행되는 SQL이 로그로 보이지만, 학습 후에는 끄는 게 좋습니다.
engine = create_async_engine(settings.database_url, echo=False)

# 세션 팩토리 — 한 요청당 한 세션을 만들기 위한 도장.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """모든 ORM 모델 클래스의 부모. SQLAlchemy 2.0의 declarative 베이스."""


async def get_session() -> AsyncIterator[AsyncSession]:
    """라우트 의존성으로 사용되는 비동기 세션 제너레이터.

    - `async with`가 끝날 때 세션이 자동으로 닫히므로 리소스 누수가 없습니다.
    - 라우트 함수가 `await session.commit()`을 직접 부르도록 두는 패턴입니다.
      (필요하면 여기서 commit/rollback을 자동 처리하도록 확장할 수도 있음)
    """
    async with AsyncSessionLocal() as session:
        yield session
