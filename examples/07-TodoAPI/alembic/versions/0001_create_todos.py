"""create todos table

이 파일은 Alembic 의 첫 번째 마이그레이션이다.
실제 환경에서는 `uv run alembic revision --autogenerate -m "create todos"`
로 생성되며, 이 챕터에서는 그 결과를 그대로 옮겨 두었다.

Revision ID: 0001
Revises:
Create Date: 2026-04-25 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """todos 테이블을 만든다."""
    op.create_table(
        "todos",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.String(length=2000), nullable=True),
        sa.Column(
            "is_done",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=False),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """업그레이드의 반대. 운영 환경에서 잘못된 변경을 되돌릴 때 쓴다."""
    op.drop_table("todos")
