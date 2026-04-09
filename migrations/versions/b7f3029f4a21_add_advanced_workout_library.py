"""Add advanced workout library and body metric references

Revision ID: b7f3029f4a21
Revises: 0a1f2b3c4d5e
Create Date: 2026-04-09 16:45:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = 'b7f3029f4a21'
down_revision = '0a1f2b3c4d5e'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    health_profile_columns = {column['name'] for column in inspector.get_columns('health_profiles')}
    if 'body_fat_percentage' not in health_profile_columns or 'body_fat_category' not in health_profile_columns:
        with op.batch_alter_table('health_profiles', schema=None) as batch_op:
            if 'body_fat_percentage' not in health_profile_columns:
                batch_op.add_column(sa.Column('body_fat_percentage', sa.Numeric(precision=6, scale=2), nullable=True))
            if 'body_fat_category' not in health_profile_columns:
                batch_op.add_column(sa.Column('body_fat_category', sa.String(length=50), nullable=True))

    tables = set(inspector.get_table_names())
    if 'body_metric_references' not in tables:
        op.create_table(
            'body_metric_references',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('source', sa.String(length=40), nullable=False),
            sa.Column('gender', sa.String(length=20), nullable=False),
            sa.Column('age', sa.Integer(), nullable=False),
            sa.Column('height_m', sa.Numeric(precision=6, scale=4), nullable=False),
            sa.Column('weight_kg', sa.Numeric(precision=7, scale=3), nullable=False),
            sa.Column('bmi', sa.Numeric(precision=6, scale=3), nullable=False),
            sa.Column('bmi_case', sa.String(length=50), nullable=True),
            sa.Column('body_fat_percentage', sa.Numeric(precision=6, scale=3), nullable=True),
            sa.Column('body_fat_case', sa.String(length=50), nullable=True),
            sa.Column('recommendation_plan', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('body_metric_references', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_body_metric_references_source'), ['source'], unique=False)
            batch_op.create_index(batch_op.f('ix_body_metric_references_gender'), ['gender'], unique=False)
            batch_op.create_index(batch_op.f('ix_body_metric_references_age'), ['age'], unique=False)
            batch_op.create_index(batch_op.f('ix_body_metric_references_bmi'), ['bmi'], unique=False)
            batch_op.create_index(batch_op.f('ix_body_metric_references_bmi_case'), ['bmi_case'], unique=False)
            batch_op.create_index(batch_op.f('ix_body_metric_references_body_fat_case'), ['body_fat_case'], unique=False)
            batch_op.create_index(batch_op.f('ix_body_metric_references_recommendation_plan'), ['recommendation_plan'], unique=False)

    if 'exercise_library' not in tables:
        op.create_table(
            'exercise_library',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('external_id', sa.String(length=120), nullable=False),
            sa.Column('name', sa.String(length=160), nullable=False),
            sa.Column('slug', sa.String(length=180), nullable=False),
            sa.Column('source', sa.String(length=50), nullable=True),
            sa.Column('level', sa.String(length=50), nullable=True),
            sa.Column('category', sa.String(length=80), nullable=True),
            sa.Column('force', sa.String(length=50), nullable=True),
            sa.Column('mechanic', sa.String(length=50), nullable=True),
            sa.Column('equipment', sa.String(length=120), nullable=True),
            sa.Column('primary_muscles', sa.JSON(), nullable=True),
            sa.Column('secondary_muscles', sa.JSON(), nullable=True),
            sa.Column('instructions', sa.JSON(), nullable=True),
            sa.Column('image_urls', sa.JSON(), nullable=True),
            sa.Column('image_url', sa.String(length=500), nullable=True),
            sa.Column('demo_media_url', sa.String(length=500), nullable=True),
            sa.Column('tags', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('exercise_library', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_exercise_library_external_id'), ['external_id'], unique=True)
            batch_op.create_index(batch_op.f('ix_exercise_library_name'), ['name'], unique=False)
            batch_op.create_index(batch_op.f('ix_exercise_library_slug'), ['slug'], unique=False)
            batch_op.create_index(batch_op.f('ix_exercise_library_source'), ['source'], unique=False)
            batch_op.create_index(batch_op.f('ix_exercise_library_level'), ['level'], unique=False)
            batch_op.create_index(batch_op.f('ix_exercise_library_category'), ['category'], unique=False)
            batch_op.create_index(batch_op.f('ix_exercise_library_equipment'), ['equipment'], unique=False)

    if 'workout_sessions' not in tables:
        op.create_table(
            'workout_sessions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('day', sa.String(length=10), nullable=False),
            sa.Column('goal', sa.String(length=50), nullable=True),
            sa.Column('session_title', sa.String(length=160), nullable=True),
            sa.Column('plan_snapshot', sa.JSON(), nullable=False),
            sa.Column('current_exercise_index', sa.Integer(), nullable=True),
            sa.Column('completed_exercises', sa.JSON(), nullable=True),
            sa.Column('total_duration_seconds', sa.Integer(), nullable=True),
            sa.Column('total_calories_burned', sa.Numeric(precision=8, scale=2), nullable=True),
            sa.Column('started_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        with op.batch_alter_table('workout_sessions', schema=None) as batch_op:
            batch_op.create_index(batch_op.f('ix_workout_sessions_user_id'), ['user_id'], unique=False)
            batch_op.create_index(batch_op.f('ix_workout_sessions_status'), ['status'], unique=False)


def downgrade():
    with op.batch_alter_table('workout_sessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_workout_sessions_status'))
        batch_op.drop_index(batch_op.f('ix_workout_sessions_user_id'))
    op.drop_table('workout_sessions')

    with op.batch_alter_table('exercise_library', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_exercise_library_equipment'))
        batch_op.drop_index(batch_op.f('ix_exercise_library_category'))
        batch_op.drop_index(batch_op.f('ix_exercise_library_level'))
        batch_op.drop_index(batch_op.f('ix_exercise_library_source'))
        batch_op.drop_index(batch_op.f('ix_exercise_library_slug'))
        batch_op.drop_index(batch_op.f('ix_exercise_library_name'))
        batch_op.drop_index(batch_op.f('ix_exercise_library_external_id'))
    op.drop_table('exercise_library')

    with op.batch_alter_table('body_metric_references', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_body_metric_references_recommendation_plan'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_body_fat_case'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_bmi_case'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_bmi'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_age'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_gender'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_source'))
    op.drop_table('body_metric_references')

    with op.batch_alter_table('health_profiles', schema=None) as batch_op:
        batch_op.drop_column('body_fat_category')
        batch_op.drop_column('body_fat_percentage')
