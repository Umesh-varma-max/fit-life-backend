"""Restore missing historical revision placeholder.

Revision ID: 8d2c1f7e9a10
Revises: f5b58c0adf38
Create Date: 2026-04-01 12:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = '8d2c1f7e9a10'
down_revision = 'f5b58c0adf38'
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    existing_columns = {column['name'] for column in inspector.get_columns('activity_logs')}
    if 'details' not in existing_columns:
        op.add_column('activity_logs', sa.Column('details', sa.JSON(), nullable=True))


def downgrade():
    inspector = sa.inspect(op.get_bind())
    existing_columns = {column['name'] for column in inspector.get_columns('activity_logs')}
    if 'details' in existing_columns:
        op.drop_column('activity_logs', 'details')
