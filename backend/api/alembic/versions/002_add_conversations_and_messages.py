"""Add conversations and messages tables for AI chatbot

Revision ID: 002
Revises: 001
Create Date: 2026-01-11

Step 3: AI-Powered Chatbot - Database Schema
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create conversations and messages tables with indexes and foreign keys."""

    # Create conversations table
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on user_id for faster filtering
    op.create_index(
        op.f('ix_conversations_user_id'),
        'conversations',
        ['user_id'],
        unique=False
    )

    # Create composite index for sorted queries (user_id, updated_at DESC)
    # Useful for fetching recent conversations
    op.create_index(
        'ix_conversations_user_id_updated_at',
        'conversations',
        ['user_id', sa.text('updated_at DESC')],
        unique=False
    )

    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.String(length=10000), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index on user_id for faster filtering
    op.create_index(
        op.f('ix_messages_user_id'),
        'messages',
        ['user_id'],
        unique=False
    )

    # Create index on conversation_id for faster message retrieval
    op.create_index(
        op.f('ix_messages_conversation_id'),
        'messages',
        ['conversation_id'],
        unique=False
    )

    # Create composite index for sorted queries (conversation_id, created_at ASC)
    # Critical for fetching conversation history in chronological order
    op.create_index(
        'ix_messages_conversation_id_created_at',
        'messages',
        ['conversation_id', sa.text('created_at ASC')],
        unique=False
    )


def downgrade() -> None:
    """Drop messages and conversations tables."""

    # Drop messages table and its indexes first (due to foreign key to conversations)
    op.drop_index('ix_messages_conversation_id_created_at', table_name='messages')
    op.drop_index(op.f('ix_messages_conversation_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_user_id'), table_name='messages')
    op.drop_table('messages')

    # Drop conversations table and its indexes
    op.drop_index('ix_conversations_user_id_updated_at', table_name='conversations')
    op.drop_index(op.f('ix_conversations_user_id'), table_name='conversations')
    op.drop_table('conversations')
