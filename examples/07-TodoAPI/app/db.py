"""DB 연결 모듈.

- 비동기 엔진(AsyncEngine)과 세션 팩토리(async_sessionmaker)를 만든다.
- FastAPI 의존성으로 주입할 `get_session` 함수를 노출한다.
- 모든 SQLAlchemy 모델이 상속할 `Base` 클래스를 정의한다.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """모든 ORM 모델이 상속하는 베이스 클래스.

    Alembic 의 자동 생성 기능이 이 Base.metadata 를 보고
    "어떤 테이블이 있어야 하는지" 를 파악합니다.
    """


# 비동기 엔진. 앱 전체에서 하나만 만들어 재사용합니다.
# echo=False 로 두지만, SQL 로그를 보고 싶다면 잠시 True 로 켜도 됩니다.
engine: AsyncEngine = create_async_engine(
    settings.database_url,
    echo=False,
)

# 세션 팩토리. 매 요청마다 이 팩토리에서 세션 하나를 꺼내 씁니다.
# expire_on_commit=False 로 두면 커밋 후에도 객체 속성에 접근할 수 있어 응답 직렬화가 편합니다.
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 의존성으로 주입할 비동기 세션.

    - 한 요청 동안 세션 하나를 만들고
    - 핸들러에서 예외가 나면 자동으로 롤백
    - 끝나면 무조건 close
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        # `async with` 블록을 빠져나가면 자동으로 close 됩니다.
