"""Initial migration - HRIS tables

Revision ID: 001_initial
Create Date: 2024-12-18

Complete schema matching all SQLAlchemy models:
- org_units, users, employees, roles, permissions
- user_roles, role_permissions (junction tables)
- attendances, leave_requests, work_submissions
- job_executions
- employee_assignments (temporary replacements)
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # =========================================
    # org_units table
    # =========================================
    op.create_table(
        "org_units",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", sa.String(100), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("level", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("path", sa.String(500), nullable=False),
        sa.Column("head_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
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
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["parent_id"], ["org_units.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_org_units_id", "org_units", ["id"])
    op.create_index("ix_org_units_code", "org_units", ["code"], unique=True)
    op.create_index("ix_org_units_type", "org_units", ["type"])
    op.create_index("ix_org_units_parent_id", "org_units", ["parent_id"])
    op.create_index("ix_org_units_path", "org_units", ["path"])
    op.create_index("ix_org_units_is_active", "org_units", ["is_active"])
    op.create_index("ix_org_units_deleted_at", "org_units", ["deleted_at"])
    op.create_index(
        "ix_org_units_path_pattern", "org_units", ["path"], postgresql_using="btree"
    )

    # =========================================
    # users table
    # =========================================
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("gender", sa.String(20), nullable=True),
        sa.Column("avatar_path", sa.String(500), nullable=True),
        sa.Column(
            "synced_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
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
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # =========================================
    # employees table
    # =========================================
    op.create_table(
        "employees",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(36), nullable=True),
        sa.Column("number", sa.String(50), nullable=False),
        sa.Column("position", sa.String(255), nullable=True),
        sa.Column("type", sa.String(20), nullable=True),
        sa.Column("org_unit_id", sa.Integer(), nullable=True),
        sa.Column("supervisor_id", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
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
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_by", sa.String(36), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["org_unit_id"], ["org_units.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(
            ["supervisor_id"], ["employees.id"], ondelete="SET NULL"
        ),
        sa.CheckConstraint(
            "type IN ('on_site', 'hybrid', 'ho') OR type IS NULL",
            name="ck_employees_type",
        ),
    )
    op.create_index("ix_employees_id", "employees", ["id"])
    op.create_index("ix_employees_number", "employees", ["number"], unique=True)
    op.create_index("ix_employees_user_id", "employees", ["user_id"], unique=True)
    op.create_index("ix_employees_org_unit_id", "employees", ["org_unit_id"])
    op.create_index("ix_employees_supervisor_id", "employees", ["supervisor_id"])
    op.create_index("ix_employees_is_active", "employees", ["is_active"])
    op.create_index("ix_employees_deleted_at", "employees", ["deleted_at"])
    op.create_index(
        "ix_employees_number_search", "employees", ["number"], postgresql_using="btree"
    )

    # Add head_id FK to org_units (deferred)
    op.create_foreign_key(
        "fk_org_units_head_id",
        "org_units",
        "employees",
        ["head_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_org_units_head_id", "org_units", ["head_id"])

    # =========================================
    # roles table
    # =========================================
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_system", sa.Boolean(), nullable=False, server_default="false"),
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
    op.create_index("ix_roles_id", "roles", ["id"])
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    # =========================================
    # permissions table
    # =========================================
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("resource", sa.String(50), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
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
    op.create_index("ix_permissions_id", "permissions", ["id"])
    op.create_index("ix_permissions_code", "permissions", ["code"], unique=True)
    op.create_index("ix_permissions_resource", "permissions", ["resource"])
    op.create_index("ix_permissions_action", "permissions", ["action"])

    # =========================================
    # user_roles junction table
    # =========================================
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.String(36), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        # Temporary assignment support
        sa.Column("is_temporary", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assignment_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )
    op.create_index("ix_user_roles_is_temporary", "user_roles", ["is_temporary"])
    op.create_index("ix_user_roles_valid_until", "user_roles", ["valid_until"])

    # =========================================
    # role_permissions junction table
    # =========================================
    op.create_table(
        "role_permissions",
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["permission_id"], ["permissions.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    # =========================================
    # attendances table
    # =========================================
    op.create_table(
        "attendances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("org_unit_id", sa.Integer(), nullable=True),
        sa.Column("attendance_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="absent"),
        sa.Column("check_in_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("check_out_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("work_hours", sa.Numeric(5, 2), nullable=True),
        sa.Column("overtime_hours", sa.Numeric(5, 2), nullable=True),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("check_in_submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("check_in_submitted_ip", sa.String(50), nullable=True),
        sa.Column("check_in_notes", sa.Text(), nullable=True),
        sa.Column("check_in_selfie_path", sa.String(500), nullable=True),
        sa.Column("check_in_latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("check_in_longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("check_in_location_name", sa.String(500), nullable=True),
        sa.Column("check_out_submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("check_out_submitted_ip", sa.String(50), nullable=True),
        sa.Column("check_out_notes", sa.Text(), nullable=True),
        sa.Column("check_out_selfie_path", sa.String(500), nullable=True),
        sa.Column("check_out_latitude", sa.Numeric(10, 8), nullable=True),
        sa.Column("check_out_longitude", sa.Numeric(11, 8), nullable=True),
        sa.Column("check_out_location_name", sa.String(500), nullable=True),
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
    op.create_index("ix_attendances_id", "attendances", ["id"])
    op.create_index("ix_attendances_employee_id", "attendances", ["employee_id"])
    op.create_index("ix_attendances_org_unit_id", "attendances", ["org_unit_id"])
    op.create_index(
        "ix_attendances_attendance_date", "attendances", ["attendance_date"]
    )

    # =========================================
    # leave_requests table
    # =========================================
    op.create_table(
        "leave_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("leave_type", sa.String(50), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("total_days", sa.Integer(), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_by", sa.String(36), nullable=True),
        # Replacement/Acting support
        sa.Column("replacement_employee_id", sa.Integer(), nullable=True),
        sa.Column("assignment_id", sa.Integer(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["replacement_employee_id"], ["employees.id"], ondelete="SET NULL"
        ),
        sa.CheckConstraint(
            "leave_type IN ('leave', 'holiday')", name="check_leave_type"
        ),
        sa.CheckConstraint("total_days > 0", name="check_total_days_positive"),
    )
    op.create_index("ix_leave_requests_id", "leave_requests", ["id"])
    op.create_index("ix_leave_requests_employee_id", "leave_requests", ["employee_id"])
    op.create_index("ix_leave_requests_leave_type", "leave_requests", ["leave_type"])
    op.create_index(
        "ix_leave_requests_replacement_employee_id",
        "leave_requests",
        ["replacement_employee_id"],
    )
    op.create_index(
        "ix_leave_requests_assignment_id", "leave_requests", ["assignment_id"]
    )

    # =========================================
    # work_submissions table
    # =========================================
    op.create_table(
        "work_submissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("submission_month", sa.Date(), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "files",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="[]",
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(36), nullable=True),
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
        sa.UniqueConstraint(
            "employee_id", "submission_month", name="uq_employee_submission_month"
        ),
        sa.CheckConstraint(
            "status IN ('draft', 'submitted')", name="check_submission_status_valid"
        ),
    )
    op.create_index("ix_work_submissions_id", "work_submissions", ["id"])
    op.create_index(
        "ix_work_submissions_employee_id", "work_submissions", ["employee_id"]
    )
    op.create_index(
        "ix_work_submissions_submission_month", "work_submissions", ["submission_month"]
    )
    op.create_index("ix_work_submissions_status", "work_submissions", ["status"])

    # =========================================
    # employee_assignments table
    # =========================================
    op.create_table(
        "employee_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("replaced_employee_id", sa.Integer(), nullable=False),
        sa.Column("org_unit_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("leave_request_id", sa.Integer(), nullable=False),
        sa.Column("reason", sa.String(500), nullable=True),
        sa.Column("created_by", sa.String(36), nullable=True),
        sa.Column("updated_by", sa.String(36), nullable=True),
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
        sa.ForeignKeyConstraint(["employee_id"], ["employees.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["replaced_employee_id"], ["employees.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["org_unit_id"], ["org_units.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["leave_request_id"], ["leave_requests.id"], ondelete="CASCADE"
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'active', 'expired', 'cancelled')",
            name="ck_employee_assignments_status",
        ),
        sa.CheckConstraint(
            "end_date >= start_date",
            name="ck_employee_assignments_date_range",
        ),
        sa.CheckConstraint(
            "employee_id != replaced_employee_id",
            name="ck_employee_assignments_different_employees",
        ),
    )
    op.create_index("ix_employee_assignments_id", "employee_assignments", ["id"])
    op.create_index(
        "ix_employee_assignments_employee_id", "employee_assignments", ["employee_id"]
    )
    op.create_index(
        "ix_employee_assignments_replaced_employee_id",
        "employee_assignments",
        ["replaced_employee_id"],
    )
    op.create_index(
        "ix_employee_assignments_org_unit_id", "employee_assignments", ["org_unit_id"]
    )
    op.create_index(
        "ix_employee_assignments_leave_request_id",
        "employee_assignments",
        ["leave_request_id"],
    )
    op.create_index(
        "ix_employee_assignments_status", "employee_assignments", ["status"]
    )
    op.create_index(
        "ix_employee_assignments_status_dates",
        "employee_assignments",
        ["status", "start_date", "end_date"],
    )

    # Add FK from user_roles.assignment_id to employee_assignments
    op.create_foreign_key(
        "fk_user_roles_assignment_id",
        "user_roles",
        "employee_assignments",
        ["assignment_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Add FK from leave_requests.assignment_id to employee_assignments
    op.create_foreign_key(
        "fk_leave_requests_assignment_id",
        "leave_requests",
        "employee_assignments",
        ["assignment_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # =========================================
    # job_executions table
    # =========================================
    op.create_table(
        "job_executions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.String(100), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Numeric(10, 3), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("error_trace", sa.Text(), nullable=True),
        sa.Column("result_data", postgresql.JSON(astext_type=sa.Text()), nullable=True),
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
    op.create_index("ix_job_executions_id", "job_executions", ["id"])
    op.create_index("ix_job_executions_job_id", "job_executions", ["job_id"])


def downgrade() -> None:
    # Drop FK constraints first
    op.drop_constraint(
        "fk_leave_requests_assignment_id", "leave_requests", type_="foreignkey"
    )
    op.drop_constraint("fk_user_roles_assignment_id", "user_roles", type_="foreignkey")

    op.drop_table("job_executions")
    op.drop_table("employee_assignments")
    op.drop_table("work_submissions")
    op.drop_table("leave_requests")
    op.drop_table("attendances")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_constraint("fk_org_units_head_id", "org_units", type_="foreignkey")
    op.drop_table("employees")
    op.drop_table("users")
    op.drop_table("org_units")
