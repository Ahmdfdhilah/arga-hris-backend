"""add attendance location

Revision ID: a74a4a122481
Revises: 90607a685ea0
Create Date: 2025-11-03 15:59:39.965139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a74a4a122481'
down_revision: Union[str, None] = '90607a685ea0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add location fields for check-in
    op.add_column('attendances', sa.Column('check_in_latitude', sa.Numeric(precision=10, scale=8), nullable=True, comment='Check-in latitude coordinate'))
    op.add_column('attendances', sa.Column('check_in_longitude', sa.Numeric(precision=11, scale=8), nullable=True, comment='Check-in longitude coordinate'))
    op.add_column('attendances', sa.Column('check_in_location_name', sa.String(500), nullable=True, comment='Check-in location address from reverse geocoding'))

    # Add location fields for check-out
    op.add_column('attendances', sa.Column('check_out_latitude', sa.Numeric(precision=10, scale=8), nullable=True, comment='Check-out latitude coordinate'))
    op.add_column('attendances', sa.Column('check_out_longitude', sa.Numeric(precision=11, scale=8), nullable=True, comment='Check-out longitude coordinate'))
    op.add_column('attendances', sa.Column('check_out_location_name', sa.String(500), nullable=True, comment='Check-out location address from reverse geocoding'))


def downgrade() -> None:
    # Remove location fields
    op.drop_column('attendances', 'check_out_location_name')
    op.drop_column('attendances', 'check_out_longitude')
    op.drop_column('attendances', 'check_out_latitude')
    op.drop_column('attendances', 'check_in_location_name')
    op.drop_column('attendances', 'check_in_longitude')
    op.drop_column('attendances', 'check_in_latitude')
