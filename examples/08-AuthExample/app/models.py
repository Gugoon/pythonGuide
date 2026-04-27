"""ORM 모델 정의.

이 챕터의 예제는 User 한 테이블만 다룹니다.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class User(Base):
    """회원가입한 사용자 한 명을 표현한다.

    - id: 자동 증가 정수 PK
    - email: 유일 인덱스, 로그인 식별자
    - hashed_password: Bcrypt 해시 결과 문자열 (평문 절대 저장 금지)
    - is_active: 비활성화된 계정은 로그인 차단에 활용
    - is_admin: 인가(권한) 검사용 단순 플래그
    - created_at: 생성 시각 (timezone-aware UTC)
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
