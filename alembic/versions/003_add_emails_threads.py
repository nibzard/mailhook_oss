"""Add emails and threads tables

Revision ID: 003_add_emails_threads
Revises: 002_add_domains_mailboxes
Create Date: 2024-01-15 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '003_add_emails_threads'
down_revision: Union[str, None] = '002_add_domains_mailboxes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create threads table
    op.create_table(
        'threads',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('mailbox_id', sa.String(length=50), nullable=False),
        sa.Column('subject', sa.String(length=1000), nullable=False),
        sa.Column('participants', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('labels', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('message_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('has_attachments', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('has_hidden_messages', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('first_message_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('custom_summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('ai_summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('user_data', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['tenant_id'],
            ['tenants.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['mailbox_id'],
            ['mailboxes.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_threads_tenant_id', 'threads', ['tenant_id'], unique=False)
    op.create_index('ix_threads_mailbox_id', 'threads', ['mailbox_id'], unique=False)
    op.create_index('ix_threads_last_message_at', 'threads', ['last_message_at'], unique=False)

    # Create emails table
    op.create_table(
        'emails',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('mailbox_id', sa.String(length=50), nullable=False),
        sa.Column('thread_id', sa.String(length=50), nullable=False),
        sa.Column('message_id', sa.String(length=1000), nullable=False),
        sa.Column('subject', sa.String(length=1000), nullable=False),
        sa.Column('from_addr', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('to', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('cc', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('bcc', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('text', sa.Text(), nullable=False, server_default=''),
        sa.Column('html', sa.Text(), nullable=False, server_default=''),
        sa.Column('original_text', sa.Text(), nullable=False, server_default=''),
        sa.Column('original_html', sa.Text(), nullable=False, server_default=''),
        sa.Column('headers', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('attachments', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('labels', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('direction', sa.String(length=20), nullable=False, server_default='inbound'),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('custom_summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('ai_summary', sa.Text(), nullable=False, server_default=''),
        sa.Column('user_data', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['tenant_id'],
            ['tenants.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['mailbox_id'],
            ['mailboxes.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['thread_id'],
            ['threads.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_emails_tenant_id', 'emails', ['tenant_id'], unique=False)
    op.create_index('ix_emails_mailbox_id', 'emails', ['mailbox_id'], unique=False)
    op.create_index('ix_emails_thread_id', 'emails', ['thread_id'], unique=False)
    op.create_index('ix_emails_message_id', 'emails', ['message_id'], unique=False)
    op.create_index('ix_emails_received_at', 'emails', ['received_at'], unique=False)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index('ix_emails_received_at', table_name='emails')
    op.drop_index('ix_emails_message_id', table_name='emails')
    op.drop_index('ix_emails_thread_id', table_name='emails')
    op.drop_index('ix_emails_mailbox_id', table_name='emails')
    op.drop_index('ix_emails_tenant_id', table_name='emails')
    op.drop_table('emails')
    op.drop_index('ix_threads_last_message_at', table_name='threads')
    op.drop_index('ix_threads_mailbox_id', table_name='threads')
    op.drop_index('ix_threads_tenant_id', table_name='threads')
    op.drop_table('threads')
