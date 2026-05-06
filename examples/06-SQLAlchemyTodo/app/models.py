"""ORM 모델 정의.

이 파일을 alembic/env.py 가 import 해야 Base.metadata 에 모델이 등록되고
autogenerate 가 작동한다.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Todo(Base):
    """할 일 한 건을 표현하는 ORM 모델 (todos 테이블에 매핑)."""

    __tablename__ = "todos"

    # 정수 PK — 자동 증가가 기본.
    id: Mapped[int] = mapped_column(primary_key=True)

    # 제목 — VARCHAR(200), NOT NULL.
    title: Mapped[str] = mapped_column(String(200))

    # 완료 여부 — 기본값 False(미완료).
    is_done: Mapped[bool] = mapped_column(default=False)

    # 생성 시각 — DB-side `func.now()` 를 server_default 로 두어 raw SQL INSERT 시에도
    # 자동 채움. timezone=True 로 PostgreSQL/MySQL 에서도 timezone-aware 로 일관 동작.
    # Python-side default(lambda) 는 보조 — ORM 경로에서 즉시 값이 객체에 박히도록.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<Todo id={self.id} title={self.title!r} is_done={self.is_done}>"
        )
