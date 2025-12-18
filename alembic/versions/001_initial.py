"""Initial migration - HRIS tables for SSO integration

Revision ID: 001_initial_sso
Create Date: 2024-12-12

Updated: 2024-12-14
- Separated User profile data from Employee employment data
- User table now stores profile replica from SSO
- Employee table links to User via user_id FK
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '001_initial_sso'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:

    # =========================================
    # org_units table - must be created first
    # =========================================
    op.create_table(
        'org_units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('path', sa.String(500), nullable=False),
        sa.Column('head_id', sa.Integer(), nullable=True),  # FK added later
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('updated_by', sa.String(36), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['parent_id'], ['org_units.id'], ondelete='SET NULL')
    )
    op.create_index('ix_org_units_code', 'org_units', ['code'], unique=True)
    op.create_index('ix_org_units_type', 'org_units', ['type'])
    op.create_index('ix_org_units_parent_id', 'org_units', ['parent_id'])
    op.create_index('ix_org_units_path', 'org_units', ['path'])
    op.create_index('ix_org_units_is_active', 'org_units', ['is_active'])
    op.create_index('ix_org_units_deleted_at', 'org_units', ['deleted_at'])

    # =========================================
    # users table - Profile replica from SSO
    # =========================================
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),  # SSO UUID as PK
        # Profile fields (synced from SSO)
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('phone', sa.String(50), nullable=True),
        sa.Column('gender', sa.String(20), nullable=True),
        sa.Column('avatar_path', sa.String(500), nullable=True),
        sa.Column('synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("gender IN ('male', 'female') OR gender IS NULL", name='ck_users_gender')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_name', 'users', ['name'])
    op.create_index('ix_users_is_active', 'users', ['is_active'])

    # =========================================
    # employees table - Employment data only
    # =========================================
    op.create_table(
        'employees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),  # FK to users.id (UUID)
        sa.Column('number', sa.String(50), nullable=False),
        sa.Column('position', sa.String(255), nullable=True),
        sa.Column('type', sa.String(20), nullable=True),  # on_site, hybrid, ho
        sa.Column('org_unit_id', sa.Integer(), nullable=True),
        sa.Column('supervisor_id', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('updated_by', sa.String(36), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_by', sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['org_unit_id'], ['org_units.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['supervisor_id'], ['employees.id'], ondelete='SET NULL'),
        sa.CheckConstraint("type IN ('on_site', 'hybrid', 'ho') OR type IS NULL", name='ck_employees_type')
    )
    op.create_index('ix_employees_number', 'employees', ['number'], unique=True)
    op.create_index('ix_employees_user_id', 'employees', ['user_id'], unique=True)
    op.create_index('ix_employees_org_unit_id', 'employees', ['org_unit_id'])
    op.create_index('ix_employees_supervisor_id', 'employees', ['supervisor_id'])
    op.create_index('ix_employees_is_active', 'employees', ['is_active'])
    op.create_index('ix_employees_deleted_at', 'employees', ['deleted_at'])

    # Add head_id FK to org_units (deferred due to circular dependency)
    op.create_foreign_key(
        'fk_org_units_head_id',
        'org_units', 'employees',
        ['head_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_org_units_head_id', 'org_units', ['head_id'])

    # =========================================
    # Roles table
    # =========================================
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

    # =========================================
    # Permissions table
    # =========================================
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

    # =========================================
    # User roles junction table
    # =========================================
    op.create_table(
        'user_roles',
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'role_id')
    )

    # =========================================
    # Role permissions junction table
    # =========================================
    op.create_table(
        'role_permissions',
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('permission_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )

    # =========================================
    # Attendance table
    # =========================================
    op.create_table(
        'attendance',
        sa.Column('id', sa.Integer(), nullable=False),
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
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_attendance_employee_id', 'attendance', ['employee_id'])
    op.create_index('ix_attendance_check_in', 'attendance', ['check_in'])

    # =========================================
    # Leave requests table
    # =========================================
    op.create_table(
        'leave_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('leave_type', sa.String(50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('approved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_leave_requests_employee_id', 'leave_requests', ['employee_id'])
    op.create_index('ix_leave_requests_status', 'leave_requests', ['status'])

    # =========================================
    # Work submissions table
    # =========================================
    op.create_table(
        'work_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('submission_date', sa.Date(), nullable=False),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='submitted'),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['employee_id'], ['employees.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_work_submissions_employee_id', 'work_submissions', ['employee_id'])

    # =========================================
    # Scheduled jobs table
    # =========================================
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
    
    # Drop FK constraint first before dropping employees table
    op.drop_constraint('fk_org_units_head_id', 'org_units', type_='foreignkey')
    op.drop_table('employees')
    op.drop_table('users')
    op.drop_table('org_units')
