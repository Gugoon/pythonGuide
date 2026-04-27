"""비동기 SQLAlchemy 엔진과 세션 의존성.

라우트는 `Depends(get_session)`으로 한 요청당 하나의 AsyncSession을 받습니다.
06장과 같은 패턴이며, 실제 DB만 SQLite → MySQL로 바뀌었습니다.
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

# 비동기 엔진 — MySQL + asyncmy 드라이버.
# echo=True로 두면 실행되는 SQL이 로그로 보입니다(N+1 디버깅 시 유용).
engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_pre_ping=True,    # 끊어진 연결 자동 감지(원격 MySQL과 통신할 때 권장)
    pool_recycle=1800,     # 30분 지난 연결은 재연결(MySQL 기본 wait_timeout 회피)
)

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

    `async with`가 끝날 때 세션이 자동으로 닫히므로 리소스 누수가 없습니다.
    트랜잭션 commit/rollback은 라우트 본문에서 명시적으로 부릅니다.
    """
    async with AsyncSessionLocal() as session:
        yield session
