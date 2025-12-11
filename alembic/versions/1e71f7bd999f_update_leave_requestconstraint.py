"""update leave requestconstraint

Revision ID: 1e71f7bd999f
Revises: a74a4a122481
Create Date: 2025-11-22 12:36:14.184271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '1e71f7bd999f'
down_revision: Union[str, None] = 'a74a4a122481'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop old constraint
    op.drop_constraint('check_leave_type', 'leave_requests', type_='check')

    # Fix existing invalid data before applying new constraint
    op.execute("""
        UPDATE leave_requests
        SET leave_type = 'leave'
        WHERE leave_type NOT IN ('leave', 'holiday');
    """)

    # Create new constraint with 'leave' and 'holiday'
    op.create_check_constraint(
        'check_leave_type',
        'leave_requests',
        "leave_type IN ('leave', 'holiday')"
    )
    
def downgrade() -> None:
    # Drop new constraint
    op.drop_constraint('check_leave_type', 'leave_requests', type_='check')

    # Fix data so downgrade won't fail
    op.execute("""
        UPDATE leave_requests
        SET leave_type = 'annual'
        WHERE leave_type NOT IN ('annual', 'maternity');
    """)

    # Restore old constraint
    op.create_check_constraint(
        'check_leave_type',
        'leave_requests',
        "leave_type IN ('annual', 'maternity')"
    )
