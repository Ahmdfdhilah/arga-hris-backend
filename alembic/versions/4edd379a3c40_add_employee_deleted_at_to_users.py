"""add employee_deleted_at to users

Revision ID: 4edd379a3c40
Revises: b4e8f3a2c9d1
Create Date: 2025-11-29 14:46:43.553880

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '4edd379a3c40'
down_revision: Union[str, None] = 'b4e8f3a2c9d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add employee_deleted_at column to users table
    op.add_column(
        "users",
        sa.Column("employee_deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # Add index for faster filtering
    op.create_index("ix_users_employee_deleted_at", "users", ["employee_deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_users_employee_deleted_at", table_name="users")
    op.drop_column("users", "employee_deleted_at")
