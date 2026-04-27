"""ORM 모델 — User, Note.

User 1 : N Note 관계입니다. 한 사용자가 여러 메모를 가집니다.
SQLAlchemy 2.0의 `Mapped[...]` + `mapped_column(...)` 표기를 사용합니다.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    """회원가입한 사용자 한 명을 표현한다.

    - id: 자동 증가 정수 PK
    - email: 유일 인덱스, 로그인 식별자
    - hashed_password: Bcrypt 해시 결과 문자열 (평문 절대 저장 금지)
    - is_active: 비활성화된 계정은 로그인 차단에 활용
    - created_at: 생성 시각 (timezone-aware UTC)
    - notes: 이 사용자의 모든 메모(1:N)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # 1:N 역방향 관계. 회원이 사라지면 메모도 cascade로 함께 사라진다.
    notes: Mapped[list["Note"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class Note(Base):
    """개인 메모 한 건.

    - 본인 소유 검사: 라우트 단에서 항상 `note.user_id == current_user.id`를
      쿼리 조건으로 함께 건다(=다른 사용자의 메모는 애초에 조회되지 않음).
    """

    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(String(10_000), nullable=False)
    # 단순 문자열 태그 — N:M 분리는 11장에서.
    tag: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # 외래 키 — 회원이 삭제되면 그 사람의 메모도 cascade로 같이 삭제된다.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # 정방향 관계 — note.user 로 작성자에 접근 가능.
    user: Mapped["User"] = relationship(back_populates="notes")
