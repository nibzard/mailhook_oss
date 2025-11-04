"""Initial schema - tenants and api_keys tables

Revision ID: 001_initial_schema
Revises:
Create Date: 2024-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index('ix_tenants_name', 'tenants', ['name'], unique=False)

    # Create api_keys table
    op.create_table(
        'api_keys',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('key_type', sa.String(length=20), nullable=False),
        sa.Column('secret_hash', sa.String(length=64), nullable=False),
        sa.Column('truncated_secret', sa.String(length=12), nullable=False),
        sa.Column('tenant_id', sa.String(length=50), nullable=True),
        sa.Column('note', sa.String(length=500), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ['tenant_id'],
            ['tenants.id'],
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('secret_hash')
    )
    op.create_index('ix_api_keys_tenant_id', 'api_keys', ['tenant_id'], unique=False)
    op.create_index('ix_api_keys_secret_hash', 'api_keys', ['secret_hash'], unique=True)


def downgrade() -> None:
    """Downgrade database schema."""
    op.drop_index('ix_api_keys_secret_hash', table_name='api_keys')
    op.drop_index('ix_api_keys_tenant_id', table_name='api_keys')
    op.drop_table('api_keys')
    op.drop_index('ix_tenants_name', table_name='tenants')
    op.drop_table('tenants')
