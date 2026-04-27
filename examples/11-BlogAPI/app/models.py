"""ORM 모델 정의 — User · Post · Comment · Tag · PostTag.

이 챕터의 핵심은 다섯 모델 사이의 관계입니다.

- User 1 : N Post   — 한 사용자가 여러 글을 쓴다
- User 1 : N Comment — 한 사용자가 여러 댓글을 단다
- Post 1 : N Comment — 한 글에 여러 댓글이 달린다
- Post N : M Tag    — 한 글에 여러 태그, 한 태그가 여러 글에 (PostTag 연결 테이블)

`relationship(...)`은 Python 객체 사이의 연결만 표현하고, 실제 DB의 외래 키는
각 ForeignKey 컬럼이 책임집니다. 두 가지를 함께 선언해야 ORM이 완전해집니다.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _utcnow() -> datetime:
    """timezone-aware UTC 현재 시각.

    `default=`에 함수 자체를 넘기기 위해 람다 대신 명시적 함수로 두었습니다.
    """
    return datetime.now(timezone.utc)


class User(Base):
    """블로그 사용자.

    - email은 unique. 로그인 식별자.
    - hashed_password는 Bcrypt 결과 문자열(평문 절대 저장 금지).
    - is_active=False인 계정은 로그인이 차단됩니다.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        nullable=False,
    )

    # 1:N 관계 — User 한 명이 가진 글들.
    # back_populates는 양방향 연결의 짝꿍 이름을 지정합니다.
    # cascade="all, delete-orphan"은 사용자가 지워질 때 글도 함께 지우라는 정책.
    posts: Mapped[list["Post"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="author",
        cascade="all, delete-orphan",
    )


class Post(Base):
    """블로그 글.

    - user_id: User에 대한 FK. ondelete="CASCADE"로 작성자가 지워지면 글도 지움.
    - slug: 사람이 읽을 수 있는 URL 일부 ("python-fastapi-intro").
            unique=True로 중복 방지. 충돌 시 라우터에서 숫자 접미사를 붙입니다.
    - published / published_at: 비공개 글은 다른 사람에게 보이지 않습니다.
    """

    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), unique=True, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utcnow,
        onupdate=_utcnow,           # UPDATE 가 나갈 때마다 자동 갱신
        nullable=False,
    )

    # ── 관계 ──
    author: Mapped["User"] = relationship(back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="Comment.created_at.asc()",
    )
    # N:M — 연결 테이블 PostTag를 통한 many-to-many.
    # secondary= 인자에 연결 테이블의 __table__을 넘긴다.
    tags: Mapped[list["Tag"]] = relationship(
        secondary="post_tags",
        back_populates="posts",
    )

    # 검색·정렬을 자주 하는 열에 인덱스(공개 글의 최신순 목록 조회용)
    __table_args__ = (
        Index("ix_posts_published_created", "published", "created_at"),
    )


class Comment(Base):
    """글에 달리는 댓글.

    - post_id, user_id 둘 다 FK + ondelete="CASCADE".
    - 글이 지워지면 댓글도, 사용자가 지워지면 그 사람의 댓글도 함께 지웁니다.
    """

    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    body: Mapped[str] = mapped_column(String(2000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    post: Mapped["Post"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="comments")


class Tag(Base):
    """글에 붙는 태그.

    - name: "python", "fastapi" 같은 사람이 입력한 원래 문자열(소문자로 정규화).
    - slug: URL에 박을 안전한 형태(같이 둘 수도 있고 name과 동일할 수도 있음).
    """

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)

    posts: Mapped[list["Post"]] = relationship(
        secondary="post_tags",
        back_populates="tags",
    )


class PostTag(Base):
    """Post ↔ Tag 다대다 연결 테이블 (N:M pivot).

    이 테이블 자체는 컬럼이 (post_id, tag_id) 두 개뿐이고, 두 컬럼이 합쳐
    PRIMARY KEY 역할을 합니다. UNIQUE 제약으로 같은 (post, tag) 조합이
    두 번 들어가는 것을 막습니다.

    `secondary="post_tags"`로 N:M을 표현했기 때문에, 일반적인 사용에서
    PostTag 인스턴스를 직접 만들 일은 없습니다(SQLAlchemy가 알아서 INSERT).
    """

    __tablename__ = "post_tags"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True
    )
    tag_id: Mapped[int] = mapped_column(
        ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    )

    __table_args__ = (
        UniqueConstraint("post_id", "tag_id", name="uq_post_tag"),
    )
