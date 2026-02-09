"""Add advanced task fields for Step 5

Revision ID: 003
Revises: 002
Create Date: 2026-01-30 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add advanced task management fields: priority, due_date, recurrence_rule, reminder_offset, next_occurrence"""

    # Add priority field (enum: low, medium, high, urgent)
    # Using VARCHAR instead of ENUM for easier migration across databases
    op.add_column('tasks', sa.Column('priority', sa.String(length=20), nullable=False, server_default='medium'))

    # Add due_date field (timestamp with timezone)
    op.add_column('tasks', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))

    # Add recurrence_rule field (iCal RRULE format, max 100 chars)
    op.add_column('tasks', sa.Column('recurrence_rule', sa.String(length=100), nullable=True))

    # Add reminder_offset field (minutes before due_date)
    op.add_column('tasks', sa.Column('reminder_offset', sa.Integer(), nullable=True))

    # Add next_occurrence field (for recurring tasks)
    op.add_column('tasks', sa.Column('next_occurrence', sa.DateTime(timezone=True), nullable=True))

    # Add check constraint for priority values
    op.create_check_constraint(
        'tasks_priority_check',
        'tasks',
        "priority IN ('low', 'medium', 'high', 'urgent')"
    )

    # Add check constraint for reminder_offset (must be positive)
    op.create_check_constraint(
        'tasks_reminder_offset_positive',
        'tasks',
        'reminder_offset IS NULL OR reminder_offset > 0'
    )


def downgrade() -> None:
    """Remove advanced task fields"""

    # Drop check constraints first
    op.drop_constraint('tasks_reminder_offset_positive', 'tasks', type_='check')
    op.drop_constraint('tasks_priority_check', 'tasks', type_='check')

    # Drop columns in reverse order
    op.drop_column('tasks', 'next_occurrence')
    op.drop_column('tasks', 'reminder_offset')
    op.drop_column('tasks', 'recurrence_rule')
    op.drop_column('tasks', 'due_date')
    op.drop_column('tasks', 'priority')
