"""SQLAlchemy ORM 모델.

여기서 정의한 클래스가 곧 DB 의 테이블이 됩니다.
한 클래스 = 한 테이블, 한 인스턴스 = 한 행(row).
"""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Todo(Base):
    """할 일 한 건을 표현하는 테이블.

    - id: 자동 증가 정수 기본 키
    - title: 1~200자 사이의 제목 (DB 차원에서는 VARCHAR(200))
    - description: 본문 설명 (선택)
    - is_done: 완료 여부
    - created_at / updated_at: 생성·수정 시각 (서버 측 기본값)
    """

    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(200), nullable=False)

    # nullable=True 라서 입력하지 않으면 NULL 이 들어갑니다.
    description: Mapped[str | None] = mapped_column(String(2000), nullable=True)

    # default=False 는 Python 측 기본값(ORM 이 INSERT 전에 채워줌),
    # server_default 는 DB 측 기본값(직접 SQL 로 INSERT 해도 안전).
    # 두 가지를 함께 두면 마이그레이션 자동 비교(autogenerate) 시 drift 가 안 생김.
    is_done: Mapped[bool] = mapped_column(
        Boolean(),
        default=False,
        server_default=text("0"),
        nullable=False,
    )

    # server_default=func.now() 는 "DB 가 INSERT 할 때 알아서 현재 시각을 넣어라" 는 뜻.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        nullable=False,
    )

    # onupdate=func.now() 는 "이 행이 UPDATE 될 때 자동으로 갱신해라".
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:  # pragma: no cover  -- 디버깅용
        return f"<Todo id={self.id} title={self.title!r} is_done={self.is_done}>"
