"""Add ForeignKey constraints to attendances and leave_requests

Revision ID: 003_add_fk_constraints
Revises: 002_add_holidays
Create Date: 2026-01-02
"""
from typing import Sequence, Union
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "003_add_fk_constraints"
down_revision: Union[str, None] = "002_add_holidays"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Clear orphaned data first - set to NULL where reference doesn't exist
    
    # Clear orphan employee_id in attendances
    op.execute("""
        UPDATE attendances 
        SET employee_id = NULL 
        WHERE employee_id IS NOT NULL 
        AND employee_id NOT IN (SELECT id FROM employees)
    """)
    
    # Delete attendances with NULL employee_id (since we need NOT NULL)
    op.execute("""
        DELETE FROM attendances 
        WHERE employee_id IS NULL
    """)
    
    # Clear orphan org_unit_id in attendances
    op.execute("""
        UPDATE attendances 
        SET org_unit_id = NULL 
        WHERE org_unit_id IS NOT NULL 
        AND org_unit_id NOT IN (SELECT id FROM org_units)
    """)
    
    # Clear orphan employee_id in leave_requests
    op.execute("""
        UPDATE leave_requests 
        SET employee_id = NULL 
        WHERE employee_id IS NOT NULL 
        AND employee_id NOT IN (SELECT id FROM employees)
    """)
    
    # Delete leave_requests with NULL employee_id (since we need NOT NULL)
    op.execute("""
        DELETE FROM leave_requests 
        WHERE employee_id IS NULL
    """)
    
    # Add FK from attendances.employee_id to employees.id
    op.create_foreign_key(
        "fk_attendances_employee_id",
        "attendances",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete="CASCADE",
    )
    
    # Add FK from attendances.org_unit_id to org_units.id
    op.create_foreign_key(
        "fk_attendances_org_unit_id",
        "attendances",
        "org_units",
        ["org_unit_id"],
        ["id"],
        ondelete="SET NULL",
    )
    
    # Add FK from leave_requests.employee_id to employees.id
    op.create_foreign_key(
        "fk_leave_requests_employee_id",
        "leave_requests",
        "employees",
        ["employee_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_leave_requests_employee_id", "leave_requests", type_="foreignkey")
    op.drop_constraint("fk_attendances_org_unit_id", "attendances", type_="foreignkey")
    op.drop_constraint("fk_attendances_employee_id", "attendances", type_="foreignkey")

