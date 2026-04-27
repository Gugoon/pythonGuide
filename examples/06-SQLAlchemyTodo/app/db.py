"""DB 인프라 — 비동기 엔진, 세션 팩토리, FastAPI 의존성 함수.

이 가이드의 모든 챕터(07, 08, 10, 11)가 이 파일의 패턴을 그대로 쓴다.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import DATABASE_URL


class Base(DeclarativeBase):
    """모든 ORM 모델의 부모 클래스.

    Base 를 상속한 클래스들이 자동으로 Base.metadata 에 등록되어,
    Alembic 의 autogenerate 가 그것을 보고 마이그레이션을 만든다.
    """

    pass


# ─────────────────────────────────────────────────────────
# 1) 비동기 엔진 — 앱 전체에서 한 개만 만들고 끝까지 재사용한다.
# ─────────────────────────────────────────────────────────
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    # echo=True 로 두면 모든 SQL 문이 콘솔에 찍힌다(디버깅에 유용).
    echo=False,
    # 2.0 스타일 사용 명시(2.0 에서는 사실 기본).
    future=True,
)


# ─────────────────────────────────────────────────────────
# 2) 세션 팩토리 — 호출하면 새 AsyncSession 을 만들어 준다.
# ─────────────────────────────────────────────────────────
SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    # commit 후에도 객체 속성에 접근할 수 있게 한다.
    # FastAPI 라우트는 응답 직전에 commit 이 일어나므로 거의 항상 False 가 편하다.
    expire_on_commit=False,
    # autoflush 를 끈다 — 명시적으로 flush 를 부르도록 해 동작을 예측 가능하게 만든다.
    autoflush=False,
)


# ─────────────────────────────────────────────────────────
# 3) FastAPI 의존성 함수
#    한 요청 = 한 세션 = 한 트랜잭션을 보장한다.
# ─────────────────────────────────────────────────────────
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """라우트에 AsyncSession 을 주입하는 의존성.

    사용:
        async def my_route(session: AsyncSession = Depends(get_session)):
            ...

    동작:
        1. 새 AsyncSession 을 만든다.
        2. yield 로 라우트에 넘겨준다.
        3. 라우트가 정상 종료되면 commit, 예외가 나면 rollback.
        4. async with 가 끝나며 세션을 close.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        else:
            await session.commit()
