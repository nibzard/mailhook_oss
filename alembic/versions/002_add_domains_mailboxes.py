"""Add domains and mailboxes tables

Revision ID: 002_add_domains_mailboxes
Revises: 001_initial_schema
Create Date: 2024-01-15 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '002_add_domains_mailboxes'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create domains table
    op.create_table(
        'domains',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('domain', sa.String(length=253), nullable=False),
        sa.Column('unicode_domain', sa.String(length=253), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('verification_status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('verification_method', sa.String(length=20), nullable=True),
        sa.Column('verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('dns_records', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['tenant_id'],
            ['tenants.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('domain')
    )
    op.create_index('ix_domains_tenant_id', 'domains', ['tenant_id'], unique=False)
    op.create_index('ix_domains_domain', 'domains', ['domain'], unique=True)

    # Create mailboxes table
    op.create_table(
        'mailboxes',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=False),
        sa.Column('domain_id', sa.String(length=50), nullable=False),
        sa.Column('local_part', sa.String(length=64), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('sender_name', sa.String(length=255), nullable=False, server_default=''),
        sa.Column('spam_policy', sa.String(length=20), nullable=False, server_default='mark'),
        sa.Column('inbound_policy', sa.String(length=20), nullable=False, server_default='thread_trust'),
        sa.Column('filters', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{"allow": [], "deny": []}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['tenant_id'],
            ['tenants.id'],
            ondelete='CASCADE'
        ),
        sa.ForeignKeyConstraint(
            ['domain_id'],
            ['domains.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_mailboxes_tenant_id', 'mailboxes', ['tenant_id'], unique=False)
    op.create_index('ix_mailboxes_domain_id', 'mailboxes', ['domain_id'], unique=False)
    op.create_index('ix_mailboxes_domain_local_part', 'mailboxes', ['domain_id', 'local_part'], unique=True)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index('ix_mailboxes_domain_local_part', table_name='mailboxes')
    op.drop_index('ix_mailboxes_domain_id', table_name='mailboxes')
    op.drop_index('ix_mailboxes_tenant_id', table_name='mailboxes')
    op.drop_table('mailboxes')
    op.drop_index('ix_domains_domain', table_name='domains')
    op.drop_index('ix_domains_tenant_id', table_name='domains')
    op.drop_table('domains')
