"""add rbac tables

Revision ID: 90607a685ea0
Revises: 001_initial_tables
Create Date: 2025-10-29 15:28:56.261923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = '90607a685ea0'
down_revision: Union[str, None] = '001_initial_tables'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    # Create roles table
    if not table_exists('roles'):
        op.create_table(
            'roles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('is_system', sa.Boolean(), nullable=False, server_default='false'),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_roles_id'), 'roles', ['id'], unique=False)
        op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)

    # Create permissions table
    if not table_exists('permissions'):
        op.create_table(
            'permissions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('code', sa.String(length=100), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('resource', sa.String(length=50), nullable=False),
            sa.Column('action', sa.String(length=50), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_permissions_id'), 'permissions', ['id'], unique=False)
        op.create_index(op.f('ix_permissions_code'), 'permissions', ['code'], unique=True)
        op.create_index(op.f('ix_permissions_resource'), 'permissions', ['resource'], unique=False)
        op.create_index(op.f('ix_permissions_action'), 'permissions', ['action'], unique=False)

    # Create user_roles table
    if not table_exists('user_roles'):
        op.create_table(
            'user_roles',
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('role_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('user_id', 'role_id')
        )

    # Create role_permissions table
    if not table_exists('role_permissions'):
        op.create_table(
            'role_permissions',
            sa.Column('role_id', sa.Integer(), nullable=False),
            sa.Column('permission_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('role_id', 'permission_id')
        )

    # Seed roles (only if table was just created or is empty)
    connection = op.get_bind()
    result = connection.execute(sa.text("SELECT COUNT(*) FROM roles")).scalar()
    
    if result == 0:
        roles_table = sa.table(
            'roles',
            sa.column('name', sa.String),
            sa.column('description', sa.Text),
            sa.column('is_system', sa.Boolean),
        )

        op.bulk_insert(
            roles_table,
            [
                {'name': 'super_admin', 'description': 'Full system access with all permissions', 'is_system': True},
                {'name': 'hr_admin', 'description': 'HR department with employee, org unit, attendance, payroll access', 'is_system': True},
                {'name': 'org_unit_head', 'description': 'Team/unit manager with limited employee and attendance access', 'is_system': True},
                {'name': 'employee', 'description': 'Regular employee with self-service access only', 'is_system': True},
                {'name': 'guest', 'description': 'Temporary users (intern, contractor) with limited access', 'is_system': True},
            ]
        )

    # Seed permissions (only if table was just created or is empty)
    result = connection.execute(sa.text("SELECT COUNT(*) FROM permissions")).scalar()
    
    if result == 0:
        permissions_table = sa.table(
            'permissions',
            sa.column('code', sa.String),
            sa.column('description', sa.Text),
            sa.column('resource', sa.String),
            sa.column('action', sa.String),
        )

        op.bulk_insert(
            permissions_table,
            [
                # Employee permissions
                {'code': 'employee.read', 'description': 'View employee data (all employees)', 'resource': 'employee', 'action': 'read'},
                {'code': 'employee.create', 'description': 'Create new employee', 'resource': 'employee', 'action': 'create'},
                {'code': 'employee.update', 'description': 'Update employee data', 'resource': 'employee', 'action': 'update'},
                {'code': 'employee.delete', 'description': 'Delete/deactivate employee', 'resource': 'employee', 'action': 'delete'},
                {'code': 'employee.soft_delete', 'description': 'Archive employee (soft delete)', 'resource': 'employee', 'action': 'soft_delete'},
                {'code': 'employee.restore', 'description': 'Restore archived employee', 'resource': 'employee', 'action': 'restore'},
                {'code': 'employee.view_deleted', 'description': 'View archived/deleted employees', 'resource': 'employee', 'action': 'view_deleted'},
                {'code': 'employee.export', 'description': 'Export employee data', 'resource': 'employee', 'action': 'export'},

                # Org unit permissions
                {'code': 'org_unit.read', 'description': 'View organization units', 'resource': 'org_unit', 'action': 'read'},
                {'code': 'org_unit.create', 'description': 'Create organization unit', 'resource': 'org_unit', 'action': 'create'},
                {'code': 'org_unit.update', 'description': 'Update organization unit', 'resource': 'org_unit', 'action': 'update'},
                {'code': 'org_unit.delete', 'description': 'Delete organization unit', 'resource': 'org_unit', 'action': 'delete'},
                {'code': 'org_unit.soft_delete', 'description': 'Archive org unit (soft delete)', 'resource': 'org_unit', 'action': 'soft_delete'},
                {'code': 'org_unit.restore', 'description': 'Restore archived org unit', 'resource': 'org_unit', 'action': 'restore'},
                {'code': 'org_unit.view_deleted', 'description': 'View archived/deleted org units', 'resource': 'org_unit', 'action': 'view_deleted'},

                # Leave Request permissions
                {'code': 'leave_request.read_own', 'description': 'View own leave requests', 'resource': 'leave_request', 'action': 'read_own'},
                {'code': 'leave_request.read', 'description': 'View specific leave request by ID', 'resource': 'leave_request', 'action': 'read'},
                {'code': 'leave_request.read_all', 'description': 'View all leave requests', 'resource': 'leave_request', 'action': 'read_all'},
                {'code': 'leave_request.create', 'description': 'Create leave request', 'resource': 'leave_request', 'action': 'create'},
                {'code': 'leave_request.update', 'description': 'Update leave request', 'resource': 'leave_request', 'action': 'update'},
                {'code': 'leave_request.delete', 'description': 'Delete leave request', 'resource': 'leave_request', 'action': 'delete'},
                {'code': 'leave_request.approve', 'description': 'Approve/reject leave request', 'resource': 'leave_request', 'action': 'approve'},

                # Attendance permissions
                {'code': 'attendance.create', 'description': 'Create attendance (check-in/check-out)', 'resource': 'attendance', 'action': 'create'},
                {'code': 'attendance.read_own', 'description': 'View own attendance history', 'resource': 'attendance', 'action': 'read_own'},
                {'code': 'attendance.read_team', 'description': 'View team/subordinates attendance', 'resource': 'attendance', 'action': 'read_team'},
                {'code': 'attendance.read', 'description': 'View specific attendance by ID', 'resource': 'attendance', 'action': 'read'},
                {'code': 'attendance.read_all', 'description': 'View all attendances with filters', 'resource': 'attendance', 'action': 'read_all'},
                {'code': 'attendance.update', 'description': 'Update attendance record', 'resource': 'attendance', 'action': 'update'},
                {'code': 'attendance.approve', 'description': 'Approve attendance corrections', 'resource': 'attendance', 'action': 'approve'},
                {'code': 'attendance.export', 'description': 'Export attendance data', 'resource': 'attendance', 'action': 'export'},

                # User permissions
                {'code': 'user.read', 'description': 'View user data', 'resource': 'user', 'action': 'read'},
                {'code': 'user.read_own', 'description': 'View own user profile', 'resource': 'user', 'action': 'read_own'},
                {'code': 'user.update', 'description': 'Update user data', 'resource': 'user', 'action': 'update'},
                {'code': 'user.update_own', 'description': 'Update own basic profile', 'resource': 'user', 'action': 'update_own'},
                {'code': 'user.create', 'description': 'Create new user', 'resource': 'user', 'action': 'create'},
                {'code': 'user.delete', 'description': 'Delete/deactivate user', 'resource': 'user', 'action': 'delete'},

                # Guest Account permissions
                {'code': 'guest.read', 'description': 'View guest accounts', 'resource': 'guest', 'action': 'read'},
                {'code': 'guest.create', 'description': 'Create guest account', 'resource': 'guest', 'action': 'create'},
                {'code': 'guest.update', 'description': 'Update guest account', 'resource': 'guest', 'action': 'update'},
                {'code': 'guest.delete', 'description': 'Delete guest account', 'resource': 'guest', 'action': 'delete'},

                # Role permissions (for future role management)
                {'code': 'role.read', 'description': 'View roles', 'resource': 'role', 'action': 'read'},
                {'code': 'role.create', 'description': 'Create custom roles', 'resource': 'role', 'action': 'create'},
                {'code': 'role.update', 'description': 'Update roles', 'resource': 'role', 'action': 'update'},
                {'code': 'role.delete', 'description': 'Delete custom roles', 'resource': 'role', 'action': 'delete'},
                {'code': 'role.assign', 'description': 'Assign roles to users', 'resource': 'role', 'action': 'assign'},

                # Payroll permissions (future)
                {'code': 'payroll.read', 'description': 'View payroll data', 'resource': 'payroll', 'action': 'read'},
                {'code': 'payroll.create', 'description': 'Process payroll', 'resource': 'payroll', 'action': 'create'},
                {'code': 'payroll.update', 'description': 'Update payroll data', 'resource': 'payroll', 'action': 'update'},
                {'code': 'payroll.approve', 'description': 'Approve payroll', 'resource': 'payroll', 'action': 'approve'},
                {'code': 'payroll.export', 'description': 'Export payroll data', 'resource': 'payroll', 'action': 'export'},

                # Work Submission permissions
                {'code': 'work_submission.read_own', 'description': 'View own work submissions', 'resource': 'work_submission', 'action': 'read_own'},
                {'code': 'work_submission.read', 'description': 'View specific work submission by ID', 'resource': 'work_submission', 'action': 'read'},
                {'code': 'work_submission.read_all', 'description': 'View all work submissions', 'resource': 'work_submission', 'action': 'read_all'},
                {'code': 'work_submission.create', 'description': 'Create work submission', 'resource': 'work_submission', 'action': 'create'},
                {'code': 'work_submission.update', 'description': 'Update work submission', 'resource': 'work_submission', 'action': 'update'},
                {'code': 'work_submission.delete', 'description': 'Delete work submission', 'resource': 'work_submission', 'action': 'delete'},
                {'code': 'work_submission.upload_file', 'description': 'Upload files to work submission', 'resource': 'work_submission', 'action': 'upload_file'},
                {'code': 'work_submission.delete_file', 'description': 'Delete files from work submission', 'resource': 'work_submission', 'action': 'delete_file'},
            ]
        )

    # Seed role_permissions (only if table is empty)
    result = connection.execute(sa.text("SELECT COUNT(*) FROM role_permissions")).scalar()
    
    if result == 0:
        # super_admin gets ALL permissions
        connection.execute(sa.text("""
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT r.id, p.id
            FROM roles r
            CROSS JOIN permissions p
            WHERE r.name = 'super_admin'
        """))
        
        # hr_admin gets employee, org_unit, leave_request, attendance, user, guest, work_submission permissions
        # NOTE: Excludes hard delete, only includes soft_delete for employee and org_unit
        # restore and view_deleted are exclusive to super_admin
        connection.execute(sa.text("""
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT r.id, p.id
            FROM roles r
            CROSS JOIN permissions p
            WHERE r.name = 'hr_admin'
            AND (
                (p.resource IN ('employee', 'org_unit', 'leave_request', 'attendance', 'user', 'guest', 'payroll', 'work_submission')
                 AND p.action NOT IN ('delete'))
                OR (p.resource = 'role' AND p.action = 'read')
                OR (p.resource = 'employee' AND p.action = 'soft_delete')
                OR (p.resource = 'org_unit' AND p.action = 'soft_delete')
            )
        """))

        # org_unit_head gets limited employee, attendance, leave_request, work_submission permissions
        connection.execute(sa.text("""
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT r.id, p.id
            FROM roles r
            CROSS JOIN permissions p
            WHERE r.name = 'org_unit_head'
            AND p.code IN (
                'employee.read',
                'org_unit.read',
                'attendance.create',
                'attendance.read_own',
                'attendance.read_team',
                'attendance.approve',
                'leave_request.read_own',
                'work_submission.read_own',
                'work_submission.read',
                'work_submission.create',
                'work_submission.update',
                'work_submission.upload_file',
                'work_submission.delete_file',
                'user.read_own',
                'user.update_own'
            )
        """))

        # employee gets self-service permissions (own data only)
        connection.execute(sa.text("""
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT r.id, p.id
            FROM roles r
            CROSS JOIN permissions p
            WHERE r.name = 'employee'
            AND p.code IN (
                'employee.read',
                'org_unit.read',
                'attendance.create',
                'attendance.read_own',
                'leave_request.read_own',
                'work_submission.read_own',
                'work_submission.read',
                'work_submission.create',
                'work_submission.update',
                'work_submission.upload_file',
                'work_submission.delete_file',
                'user.read_own',
                'user.update_own',
                'payroll.read'
            )
        """))

        # guest gets minimal permissions (attendance and own profile only)
        connection.execute(sa.text("""
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT r.id, p.id
            FROM roles r
            CROSS JOIN permissions p
            WHERE r.name = 'guest'
            AND p.code IN (
                'attendance.create',
                'attendance.read_own',
                'user.read_own',
                'user.update_own'
            )
        """))


def downgrade() -> None:
    # Drop tables with IF EXISTS guard
    if table_exists('role_permissions'):
        op.drop_table('role_permissions')
    
    if table_exists('user_roles'):
        op.drop_table('user_roles')
    
    if table_exists('permissions'):
        op.drop_index(op.f('ix_permissions_action'), table_name='permissions')
        op.drop_index(op.f('ix_permissions_resource'), table_name='permissions')
        op.drop_index(op.f('ix_permissions_code'), table_name='permissions')
        op.drop_index(op.f('ix_permissions_id'), table_name='permissions')
        op.drop_table('permissions')
    
    if table_exists('roles'):
        op.drop_index(op.f('ix_roles_name'), table_name='roles')
        op.drop_index(op.f('ix_roles_id'), table_name='roles')
        op.drop_table('roles')