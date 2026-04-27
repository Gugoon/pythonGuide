"""ORM 모델 정의.

이 파일을 alembic/env.py 가 import 해야 Base.metadata 에 모델이 등록되고
autogenerate 가 작동한다.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String
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

    # 생성 시각 — 행이 만들어질 때 lambda 가 호출되어 현재 UTC 시각이 채워진다.
    # Python 3.12+ 에서 datetime.utcnow() 는 deprecated 이므로
    # 명시적 timezone.utc 를 붙인 datetime.now(timezone.utc) 를 쓴다.
    # default 에는 함수 객체(여기서는 lambda)를 넘긴다 — 호출하면 모듈 import 시각이 박힘.
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return (
            f"<Todo id={self.id} title={self.title!r} is_done={self.is_done}>"
        )
