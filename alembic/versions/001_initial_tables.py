"""Initial tables for users and attendances

Revision ID: 001_initial_tables
Revises:
Create Date: 2025-01-28 22:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "001_initial_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    # Create users table
    if not table_exists("users"):
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("sso_id", sa.Integer(), nullable=True),  
            sa.Column("employee_id", sa.Integer(), nullable=True),
            sa.Column("org_unit_id", sa.Integer(), nullable=True),
            sa.Column("email", sa.String(length=255), nullable=False),  # Required and unique
            sa.Column("first_name", sa.String(length=100), nullable=False),
            sa.Column("last_name", sa.String(length=100), nullable=False),
            sa.Column("account_type", sa.String(length=20), nullable=False, server_default="regular"),  # regular or guest
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)
        op.create_index(op.f("ix_users_sso_id"), "users", ["sso_id"], unique=True)
        op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
        op.create_index(
            op.f("ix_users_employee_id"), "users", ["employee_id"], unique=False
        )
        op.create_index(
            op.f("ix_users_org_unit_id"), "users", ["org_unit_id"], unique=False
        )
        op.create_index(op.f("ix_users_account_type"), "users", ["account_type"], unique=False)

    # Create guest_accounts table
    if not table_exists("guest_accounts"):
        op.create_table(
            "guest_accounts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("guest_type", sa.String(length=50), nullable=False),
            sa.Column("valid_from", sa.DateTime(timezone=True), nullable=False),
            sa.Column("valid_until", sa.DateTime(timezone=True), nullable=False),
            sa.Column("sponsor_id", sa.Integer(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["sponsor_id"], ["users.id"], ondelete="SET NULL"),
            sa.UniqueConstraint("user_id"),
        )
        op.create_index(op.f("ix_guest_accounts_user_id"), "guest_accounts", ["user_id"], unique=False)
        op.create_index(op.f("ix_guest_accounts_valid_until"), "guest_accounts", ["valid_until"], unique=False)

    # Create attendances table
    if not table_exists("attendances"):
        op.create_table(
            "attendances",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("employee_id", sa.Integer(), nullable=False, comment="Employee ID from workforce service"),
            sa.Column("org_unit_id", sa.Integer(), nullable=True, comment="Org unit ID for display purposes"),
            sa.Column("attendance_date", sa.Date(), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="absent"),
            sa.Column("check_in_time", sa.DateTime(timezone=True), nullable=True),
            sa.Column("check_out_time", sa.DateTime(timezone=True), nullable=True),
            sa.Column("work_hours", sa.Numeric(5, 2), nullable=True, comment="Calculated work hours in decimal (e.g., 8.5 for 8 hours 30 minutes)"),
            sa.Column("created_by", sa.Integer(), nullable=True, comment="User/Employee ID who created this record"),
            sa.Column("check_in_submitted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("check_in_submitted_ip", sa.String(length=50), nullable=True),
            sa.Column("check_in_notes", sa.Text(), nullable=True),
            sa.Column("check_in_selfie_path", sa.String(length=500), nullable=True, comment="GCP storage path for check-in selfie (mandatory when check-in)"),
            sa.Column("check_out_submitted_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("check_out_submitted_ip", sa.String(length=50), nullable=True),
            sa.Column("check_out_notes", sa.Text(), nullable=True),
            sa.Column("check_out_selfie_path", sa.String(length=500), nullable=True, comment="GCP storage path for check-out selfie (mandatory when check-out)"),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_attendances_id"), "attendances", ["id"], unique=False)
        op.create_index(op.f("ix_attendances_employee_id"), "attendances", ["employee_id"], unique=False)
        op.create_index(op.f("ix_attendances_org_unit_id"), "attendances", ["org_unit_id"], unique=False)
        op.create_index(op.f("ix_attendances_attendance_date"), "attendances", ["attendance_date"], unique=False)

        # Composite index for common queries
        op.create_index("ix_attendances_employee_date", "attendances", ["employee_id", "attendance_date"], unique=False)

    # Create leave_requests table
    if not table_exists("leave_requests"):
        op.create_table(
            "leave_requests",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("employee_id", sa.Integer(), nullable=False),
            sa.Column("leave_type", sa.String(length=50), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=False),
            sa.Column("end_date", sa.Date(), nullable=False),
            sa.Column("total_days", sa.Integer(), nullable=False),
            sa.Column("reason", sa.Text(), nullable=False),
            sa.Column("created_by", sa.Integer(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("now()"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.CheckConstraint(
                "leave_type IN ('annual', 'maternity')",
                name="check_leave_type"
            ),
            sa.CheckConstraint(
                "total_days > 0",
                name="check_total_days_positive"
            ),
        )
        op.create_index(op.f("ix_leave_requests_id"), "leave_requests", ["id"], unique=False)
        op.create_index(op.f("ix_leave_requests_employee_id"), "leave_requests", ["employee_id"], unique=False)
        op.create_index(op.f("ix_leave_requests_leave_type"), "leave_requests", ["leave_type"], unique=False)

    # Create job_executions table
    if not table_exists("job_executions"):
        op.create_table(
            'job_executions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('job_id', sa.String(length=100), nullable=False, comment='Unique identifier job'),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, comment='Waktu mulai eksekusi'),
            sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True, comment='Waktu selesai eksekusi'),
            sa.Column('duration_seconds', sa.Numeric(precision=10, scale=3), nullable=True, comment='Durasi eksekusi dalam detik'),
            sa.Column('success', sa.Boolean(), nullable=False, server_default='false', comment='Status keberhasilan eksekusi'),
            sa.Column('message', sa.Text(), nullable=True, comment='Pesan hasil eksekusi'),
            sa.Column('error_trace', sa.Text(), nullable=True, comment='Stack trace jika error'),
            sa.Column('result_data', sa.JSON(), nullable=True, comment='Data hasil eksekusi (JSON)'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_job_executions_id'), 'job_executions', ['id'], unique=False)
        op.create_index(op.f('ix_job_executions_job_id'), 'job_executions', ['job_id'], unique=False)


def downgrade() -> None:
    # Drop job_executions table with IF EXISTS guard
    if table_exists("job_executions"):
        op.drop_index(op.f('ix_job_executions_job_id'), table_name='job_executions')
        op.drop_index(op.f('ix_job_executions_id'), table_name='job_executions')
        op.drop_table('job_executions')

    # Drop leave_requests table with IF EXISTS guard
    if table_exists("leave_requests"):
        op.drop_index(op.f("ix_leave_requests_leave_type"), table_name="leave_requests")
        op.drop_index(op.f("ix_leave_requests_employee_id"), table_name="leave_requests")
        op.drop_index(op.f("ix_leave_requests_id"), table_name="leave_requests")
        op.drop_table("leave_requests")

    # Drop attendances table with IF EXISTS guard
    if table_exists("attendances"):
        op.drop_index("ix_attendances_employee_date", table_name="attendances")
        op.drop_index(op.f("ix_attendances_attendance_date"), table_name="attendances")
        op.drop_index(op.f("ix_attendances_org_unit_id"), table_name="attendances")
        op.drop_index(op.f("ix_attendances_employee_id"), table_name="attendances")
        op.drop_index(op.f("ix_attendances_id"), table_name="attendances")
        op.drop_table("attendances")

    # Drop guest_accounts table with IF EXISTS guard
    if table_exists("guest_accounts"):
        op.drop_index(op.f("ix_guest_accounts_valid_until"), table_name="guest_accounts")
        op.drop_index(op.f("ix_guest_accounts_user_id"), table_name="guest_accounts")
        op.drop_table("guest_accounts")

    # Drop users table with IF EXISTS guard
    if table_exists("users"):
        op.drop_index(op.f("ix_users_account_type"), table_name="users")
        op.drop_index(op.f("ix_users_org_unit_id"), table_name="users")
        op.drop_index(op.f("ix_users_employee_id"), table_name="users")
        op.drop_index(op.f("ix_users_email"), table_name="users")
        op.drop_index(op.f("ix_users_sso_id"), table_name="users")
        op.drop_index(op.f("ix_users_id"), table_name="users")
        op.drop_table("users")