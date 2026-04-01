"""add details to activity logs

Revision ID: 8d2c1f7e9a10
Revises: f5b58c0adf38
Create Date: 2026-04-01 10:15:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = '8d2c1f7e9a10'
down_revision = 'f5b58c0adf38'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('activity_logs', sa.Column('details', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('activity_logs', 'details')
