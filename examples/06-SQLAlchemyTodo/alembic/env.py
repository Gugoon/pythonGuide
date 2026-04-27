"""Alembic 환경 — 비동기 엔진(AsyncEngine)으로 마이그레이션을 실행한다.

이 파일은 `alembic init` 이 만들어 준 템플릿을 비동기용으로 수정한 것.
한 번 만들어 두면 이후 챕터(07, 08, 10, 11)에서도 그대로 재사용한다.
"""

from __future__ import annotations

import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

# ─────────────────────────────────────────────────────────
# 우리 앱(app/) 을 import 가능하게 하기 위한 sys.path 보정.
# alembic/ 폴더가 프로젝트 루트의 자식이라는 전제.
# ─────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ─────────────────────────────────────────────────────────
# 우리 앱의 설정과 모델을 가져온다.
# - DATABASE_URL: alembic.ini 의 sqlalchemy.url 을 덮어쓴다.
# - Base: autogenerate 가 비교할 메타데이터의 컨테이너.
# - models: 이 import 자체가 모델 클래스를 Base.metadata 에 등록시킨다.
#           이 줄을 빠뜨리면 autogenerate 가 빈 마이그레이션을 만든다.
# ─────────────────────────────────────────────────────────
from app.config import DATABASE_URL  # noqa: E402
from app.db import Base  # noqa: E402
from app import models  # noqa: E402, F401

# ─────────────────────────────────────────────────────────
# Alembic 기본 설정 객체
# ─────────────────────────────────────────────────────────
config = context.config

# alembic.ini 의 sqlalchemy.url 을 환경 변수의 DATABASE_URL 로 덮어쓴다.
config.set_main_option("sqlalchemy.url", DATABASE_URL)

# 로깅 설정(alembic.ini 의 [logger_*] 섹션을 적용)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# autogenerate 가 비교할 메타데이터
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """오프라인 모드 — 실제 DB 에 연결하지 않고 SQL 문만 출력.

    `alembic upgrade head --sql` 같은 명령에서 쓰인다.
    실제 적용 시에는 보통 온라인 모드(아래)가 호출된다.
    """
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
    """실제 마이그레이션을 실행하는 본체. 동기 connection 위에서 돈다."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,            # 열의 타입 변경도 감지
        render_as_batch=True,          # SQLite 의 ALTER TABLE 제약을 우회
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """비동기 엔진을 만들고, 동기 컨텍스트로 변환해 마이그레이션을 실행."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        # Alembic 본체는 동기 함수만 받으므로, run_sync 로 다리를 놓는다.
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """온라인 모드 — 실제 DB 에 연결해 마이그레이션을 실행."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
