"""Alembic 환경 설정 모듈.

`alembic upgrade head` / `alembic revision --autogenerate` 명령이
실행될 때 이 파일이 호출된다.

요점:
- 우리는 비동기 엔진(aiosqlite/asyncpg) 을 쓰므로, asyncio 기반으로 마이그레이션을 돌린다.
- 모델의 메타데이터(`Base.metadata`) 를 alembic 에 알려줘 자동 생성을 가능하게 한다.
- DB URL 은 alembic.ini 가 아니라 앱의 settings(=환경 변수)에서 가져온다.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# 앱 모듈을 import 해서 모델을 로드한다.
# 이게 있어야 Base.metadata 에 모든 테이블이 등록된다.
from app.config import settings
from app.db import Base
from app import models  # noqa: F401  -- 모델 등록을 위해 필요

config = context.config

# alembic.ini 의 기본 sqlalchemy.url 을 환경 변수 값으로 덮어쓴다.
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """오프라인 모드 — DB 에 실제 연결하지 않고 SQL 스크립트만 출력."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """동기 커넥션을 받아 실제 마이그레이션을 실행."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        render_as_batch=True,  # SQLite 에서 ALTER TABLE 호환성을 위해 켠다.
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """온라인 모드 — 실제 DB 에 연결해서 마이그레이션을 적용."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
