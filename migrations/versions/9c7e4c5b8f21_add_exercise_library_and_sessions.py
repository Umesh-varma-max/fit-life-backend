"""Add exercise library, body metric references, workout sessions, and BFP support.

Revision ID: 9c7e4c5b8f21
Revises: f5b58c0adf38
Create Date: 2026-04-08 11:05:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = '9c7e4c5b8f21'
down_revision = '8d2c1f7e9a10'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('health_profiles', sa.Column('body_fat_percentage', sa.Numeric(precision=5, scale=2), nullable=True))
    op.add_column('health_profiles', sa.Column('body_fat_category', sa.String(length=50), nullable=True))

    op.create_table(
        'body_metric_references',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_dataset', sa.String(length=20), nullable=False),
        sa.Column('weight', sa.Numeric(precision=7, scale=3), nullable=True),
        sa.Column('height', sa.Numeric(precision=7, scale=3), nullable=True),
        sa.Column('bmi', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column('body_fat_percentage', sa.Numeric(precision=6, scale=3), nullable=True),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('bmi_case', sa.String(length=50), nullable=True),
        sa.Column('exercise_recommendation_plan', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('body_metric_references', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_body_metric_references_age'), ['age'], unique=False)
        batch_op.create_index(batch_op.f('ix_body_metric_references_bmi'), ['bmi'], unique=False)
        batch_op.create_index(batch_op.f('ix_body_metric_references_body_fat_percentage'), ['body_fat_percentage'], unique=False)
        batch_op.create_index(batch_op.f('ix_body_metric_references_exercise_recommendation_plan'), ['exercise_recommendation_plan'], unique=False)
        batch_op.create_index(batch_op.f('ix_body_metric_references_gender'), ['gender'], unique=False)
        batch_op.create_index(batch_op.f('ix_body_metric_references_source_dataset'), ['source_dataset'], unique=False)

    op.create_table(
        'exercise_library',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(length=80), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('body_parts', sa.JSON(), nullable=True),
        sa.Column('target_muscles', sa.JSON(), nullable=True),
        sa.Column('secondary_muscles', sa.JSON(), nullable=True),
        sa.Column('equipments', sa.JSON(), nullable=True),
        sa.Column('keywords', sa.JSON(), nullable=True),
        sa.Column('instructions', sa.JSON(), nullable=True),
        sa.Column('exercise_tips', sa.JSON(), nullable=True),
        sa.Column('variations', sa.JSON(), nullable=True),
        sa.Column('related_exercise_ids', sa.JSON(), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('exercise_type', sa.String(length=50), nullable=True),
        sa.Column('overview', sa.Text(), nullable=True),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('gif_url', sa.Text(), nullable=True),
        sa.Column('video_url', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('exercise_library', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_exercise_library_external_id'), ['external_id'], unique=True)
        batch_op.create_index(batch_op.f('ix_exercise_library_name'), ['name'], unique=False)

    op.create_table(
        'workout_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('goal', sa.String(length=50), nullable=True),
        sa.Column('day_of_week', sa.String(length=10), nullable=True),
        sa.Column('session_name', sa.String(length=150), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('current_exercise_index', sa.Integer(), nullable=True),
        sa.Column('plan_snapshot', sa.JSON(), nullable=True),
        sa.Column('completed_exercises', sa.JSON(), nullable=True),
        sa.Column('total_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('total_calories_burned', sa.Integer(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('workout_sessions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_workout_sessions_status'), ['status'], unique=False)
        batch_op.create_index(batch_op.f('ix_workout_sessions_user_id'), ['user_id'], unique=False)


def downgrade():
    with op.batch_alter_table('workout_sessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_workout_sessions_user_id'))
        batch_op.drop_index(batch_op.f('ix_workout_sessions_status'))
    op.drop_table('workout_sessions')

    with op.batch_alter_table('exercise_library', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_exercise_library_name'))
        batch_op.drop_index(batch_op.f('ix_exercise_library_external_id'))
    op.drop_table('exercise_library')

    with op.batch_alter_table('body_metric_references', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_body_metric_references_source_dataset'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_gender'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_exercise_recommendation_plan'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_body_fat_percentage'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_bmi'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_age'))
    op.drop_table('body_metric_references')

    op.drop_column('health_profiles', 'body_fat_category')
    op.drop_column('health_profiles', 'body_fat_percentage')
