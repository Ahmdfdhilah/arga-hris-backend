"""add overtime hours

Revision ID: 810af87fff78
Revises: 1e71f7bd999f
Create Date: 2025-11-22 12:40:55.811500

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '810af87fff78'
down_revision: Union[str, None] = '1e71f7bd999f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add overtime_hours column to attendances table
    op.add_column(
        'attendances',
        sa.Column(
            'overtime_hours',
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment='Overtime hours after 18:00 (e.g., 2.5 for 2 hours 30 minutes)'
        )
    )


def downgrade() -> None:
    # Remove overtime_hours column
    op.drop_column('attendances', 'overtime_hours')
