"""Add token versioning and login tracking to users.

Revision ID: 0a1f2b3c4d5e
Revises: 9c7e4c5b8f21
Create Date: 2026-04-08 13:20:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = '0a1f2b3c4d5e'
down_revision = '9c7e4c5b8f21'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('token_version', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))
    op.alter_column('users', 'token_version', server_default=None)


def downgrade():
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'token_version')
