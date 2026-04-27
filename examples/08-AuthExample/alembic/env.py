"""Alembic env.py — 비동기 SQLAlchemy + 우리 설정값 통합.

기본 생성된 env.py에서 다음을 바꿨습니다.

1. `sqlalchemy.url`을 우리 settings.database_url로 덮어쓰기.
2. 비동기 엔진(`async_engine_from_config`) 사용.
3. `target_metadata = Base.metadata`, `app.models`를 import해 모든 모델을 등록.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# 우리 앱 설정과 메타데이터를 가져온다.
from app.config import get_settings
from app.db import Base
import app.models  # noqa: F401  (import 만으로 Base.metadata 에 모델이 등록됨)


# Alembic Config 객체 — alembic.ini의 값에 접근할 수 있다.
config = context.config

# 우리 설정값으로 sqlalchemy.url을 덮어쓴다.
# 이렇게 하면 .env 변경만으로 마이그레이션 대상 DB도 바뀐다.
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database_url)

# 로그 설정.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 자동 생성(revision --autogenerate) 시 비교 기준이 될 메타데이터.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """오프라인 모드 — DB에 연결하지 않고 SQL 문자열만 만들어낸다."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """비동기 엔진으로 마이그레이션을 실행한다."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """온라인 모드 — 실제 DB에 연결해 마이그레이션을 실행한다."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
