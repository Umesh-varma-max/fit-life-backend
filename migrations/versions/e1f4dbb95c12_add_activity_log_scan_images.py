"""Add scan image persistence to activity logs

Revision ID: e1f4dbb95c12
Revises: b7f3029f4a21
Create Date: 2026-04-10 11:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = 'e1f4dbb95c12'
down_revision = 'b7f3029f4a21'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column['name'] for column in inspector.get_columns('activity_logs')}

    with op.batch_alter_table('activity_logs', schema=None) as batch_op:
        if 'image_blob' not in columns:
            batch_op.add_column(sa.Column('image_blob', sa.LargeBinary(), nullable=True))
        if 'image_mime_type' not in columns:
            batch_op.add_column(sa.Column('image_mime_type', sa.String(length=100), nullable=True))
        if 'image_filename' not in columns:
            batch_op.add_column(sa.Column('image_filename', sa.String(length=255), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column['name'] for column in inspector.get_columns('activity_logs')}

    with op.batch_alter_table('activity_logs', schema=None) as batch_op:
        if 'image_filename' in columns:
            batch_op.drop_column('image_filename')
        if 'image_mime_type' in columns:
            batch_op.drop_column('image_mime_type')
        if 'image_blob' in columns:
            batch_op.drop_column('image_blob')
