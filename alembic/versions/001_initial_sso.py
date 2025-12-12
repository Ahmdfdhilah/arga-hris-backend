"""Initial migration - HRIS tables for SSO integration

Revision ID: 001_initial_sso
Create Date: 2024-12-12
"""
from alembic import op
import sqlalchemy as sa


revision = '001_initial_sso'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table - minimal linking data
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sso_id', sa.String(36), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=True),
        sa.Column('org_unit_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_sso_id', 'users', ['sso_id'], unique=True)
    op.create_index('ix_users_employee_id', 'users', ['employee_id'], unique=False)
    op.create_index('ix_users_org_unit_id', 'users', ['org_unit_id'], unique=False)

    # Roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_roles_name', 'roles', ['name'], unique=True)

    # Permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource', sa.String(50), nullable=False),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_permissions_code', 'permissions', ['code'], unique=True)
    op.create_index('ix_permissions_resource', 'permissions', ['resource'], unique=False)
    op.create_index('ix_permissions_action', 'permissions', ['action'], unique=False)

    # User roles junction table
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # Role permissions junction table
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    # Attendance table
    op.create_table(
        'attendance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('check_in', sa.DateTime(timezone=True), nullable=False),
        sa.Column('check_out', sa.DateTime(timezone=True), nullable=True),
        sa.Column('check_in_latitude', sa.Float(), nullable=True),
        sa.Column('check_in_longitude', sa.Float(), nullable=True),
        sa.Column('check_out_latitude', sa.Float(), nullable=True),
        sa.Column('check_out_longitude', sa.Float(), nullable=True),
        sa.Column('check_in_address', sa.Text(), nullable=True),
        sa.Column('check_out_address', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='present'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('overtime_hours', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_attendance_user_id', 'attendance', ['user_id'])
    op.create_index('ix_attendance_employee_id', 'attendance', ['employee_id'])
    op.create_index('ix_attendance_check_in', 'attendance', ['check_in'])

    # Leave requests table
    op.create_table(
        'leave_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('leave_type', sa.String(50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_leave_requests_user_id', 'leave_requests', ['user_id'])
    op.create_index('ix_leave_requests_employee_id', 'leave_requests', ['employee_id'])
    op.create_index('ix_leave_requests_status', 'leave_requests', ['status'])

    # Work submissions table
    op.create_table(
        'work_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('submission_date', sa.Date(), nullable=False),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='submitted'),
        sa.Column('reviewed_by', sa.Integer(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['reviewed_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_work_submissions_user_id', 'work_submissions', ['user_id'])
    op.create_index('ix_work_submissions_employee_id', 'work_submissions', ['employee_id'])

    # Scheduled jobs table
    op.create_table(
        'scheduled_jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('job_type', sa.String(50), nullable=False),
        sa.Column('cron_expression', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run', sa.DateTime(timezone=True), nullable=True),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_scheduled_jobs_name', 'scheduled_jobs', ['name'], unique=True)


def downgrade() -> None:
    op.drop_table('scheduled_jobs')
    op.drop_table('work_submissions')
    op.drop_table('leave_requests')
    op.drop_table('attendance')
    op.drop_table('role_permissions')
    op.drop_table('user_roles')
    op.drop_table('permissions')
    op.drop_table('roles')
    op.drop_table('users')
