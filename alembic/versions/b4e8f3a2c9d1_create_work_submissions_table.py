"""create work_submissions table

Revision ID: b4e8f3a2c9d1
Revises: 810af87fff78
Create Date: 2025-11-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = 'b4e8f3a2c9d1'
down_revision: Union[str, None] = '810af87fff78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create work_submissions table
    op.create_table(
        'work_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('submission_month', sa.Date(), nullable=False, comment='Bulan submission (always 1st day of month)'),
        sa.Column('title', sa.String(length=255), nullable=False, comment='Judul submission'),
        sa.Column('description', sa.Text(), nullable=True, comment='Deskripsi detail pekerjaan'),
        sa.Column(
            'files',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default='[]',
            comment='Array of file metadata (file_name, file_path, file_size, file_type)'
        ),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft', comment='Status: draft or submitted'),
        sa.Column('submitted_at', sa.DateTime(timezone=True), nullable=True, comment='Timestamp when status changed to submitted'),
        sa.Column('created_by', sa.Integer(), nullable=True, comment='User ID who created this submission'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('employee_id', 'submission_month', name='uq_employee_submission_month'),
        sa.CheckConstraint("status IN ('draft', 'submitted')", name='check_submission_status_valid'),
    )

    # Create indexes
    op.create_index('ix_work_submissions_id', 'work_submissions', ['id'], unique=False)
    op.create_index('ix_work_submissions_employee_id', 'work_submissions', ['employee_id'], unique=False)
    op.create_index('ix_work_submissions_submission_month', 'work_submissions', ['submission_month'], unique=False)
    op.create_index('ix_work_submissions_status', 'work_submissions', ['status'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_work_submissions_status', table_name='work_submissions')
    op.drop_index('ix_work_submissions_submission_month', table_name='work_submissions')
    op.drop_index('ix_work_submissions_employee_id', table_name='work_submissions')
    op.drop_index('ix_work_submissions_id', table_name='work_submissions')

    # Drop table
    op.drop_table('work_submissions')
