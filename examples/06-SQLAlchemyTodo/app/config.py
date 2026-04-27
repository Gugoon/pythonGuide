"""앱 전역 설정.

지금은 DATABASE_URL 한 가지만 있다. 운영 환경에서는 환경 변수로 덮어쓰고,
개발 환경에서는 이 파일의 기본값(SQLite 파일)을 그대로 쓴다.
"""

from __future__ import annotations

import os

# 개발 기본값: 현재 작업 폴더에 todo.db 라는 SQLite 파일을 사용한다.
# 운영에서는 환경 변수 DATABASE_URL 을 PostgreSQL/MySQL 의 주소로 설정한다.
#
# 형식 참고:
#   sqlite+aiosqlite:///./todo.db
#   sqlite+aiosqlite:///:memory:
#   postgresql+asyncpg://user:pass@host:5432/dbname
#   mysql+asyncmy://user:pass@host:3306/dbname
DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./todo.db",
)
