"""Add search and reminder indexes for Step 5

Revision ID: 004
Revises: 003
Create Date: 2026-01-30 15:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes for full-text search and reminder processing"""

    # Create task_tags table
    op.create_table(
        'task_tags',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('tag_name', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_task_tags_task_id', 'task_tags', ['task_id'])
    op.create_index('ix_task_tags_tag_name', 'task_tags', ['tag_name'])

    # Create reminders table
    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reminder_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reminders_task_id', 'reminders', ['task_id'])
    op.create_index('ix_reminders_user_id', 'reminders', ['user_id'])
    op.create_index('ix_reminders_reminder_at', 'reminders', ['reminder_at'])
    op.create_index('ix_reminders_sent', 'reminders', ['sent'])

    # Add GIN index for full-text search on tasks
    # Create tsvector column for full-text search (generated column)
    op.execute("""
        ALTER TABLE tasks ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            to_tsvector('english', coalesce(title, '') || ' ' || coalesce(description, ''))
        ) STORED
    """)

    # Create GIN index for fast full-text search
    op.create_index(
        'ix_tasks_search_vector',
        'tasks',
        ['search_vector'],
        postgresql_using='gin'
    )

    # Create composite index for reminder processing query
    # Query: SELECT * FROM reminders WHERE reminder_at <= NOW() AND sent = false
    op.create_index(
        'ix_reminders_due_unsent',
        'reminders',
        ['reminder_at', 'sent'],
        postgresql_where=sa.text('sent = false')
    )

    # Create composite index for task filtering by priority and due_date
    op.create_index(
        'ix_tasks_priority_due_date',
        'tasks',
        ['priority', 'due_date']
    )

    # Create index for recurring tasks query
    # Query: SELECT * FROM tasks WHERE next_occurrence <= NOW() AND recurrence_rule IS NOT NULL
    op.create_index(
        'ix_tasks_next_occurrence',
        'tasks',
        ['next_occurrence'],
        postgresql_where=sa.text('recurrence_rule IS NOT NULL')
    )


def downgrade() -> None:
    """Remove search and reminder indexes"""

    # Drop indexes
    op.drop_index('ix_tasks_next_occurrence', 'tasks')
    op.drop_index('ix_tasks_priority_due_date', 'tasks')
    op.drop_index('ix_reminders_due_unsent', 'reminders')
    op.drop_index('ix_tasks_search_vector', 'tasks')

    # Drop search_vector column
    op.drop_column('tasks', 'search_vector')

    # Drop reminders table indexes
    op.drop_index('ix_reminders_sent', 'reminders')
    op.drop_index('ix_reminders_reminder_at', 'reminders')
    op.drop_index('ix_reminders_user_id', 'reminders')
    op.drop_index('ix_reminders_task_id', 'reminders')

    # Drop reminders table
    op.drop_table('reminders')

    # Drop task_tags table indexes
    op.drop_index('ix_task_tags_tag_name', 'task_tags')
    op.drop_index('ix_task_tags_task_id', 'task_tags')

    # Drop task_tags table
    op.drop_table('task_tags')
