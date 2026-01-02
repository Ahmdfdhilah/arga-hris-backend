"""Alembic migration: Add holidays table.

Revision ID: 002_add_holidays
Revises: 001_initial
Create Date: 2026-01-02

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_holidays'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Buat tabel holidays untuk menyimpan hari libur nasional."""
    op.create_table(
        'holidays',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('date', sa.Date(), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.Column('updated_by', sa.UUID(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    """Drop tabel holidays."""
    op.drop_table('holidays')
