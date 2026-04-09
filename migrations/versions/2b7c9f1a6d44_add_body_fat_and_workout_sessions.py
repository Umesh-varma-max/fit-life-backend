"""add body fat and workout sessions

Revision ID: 2b7c9f1a6d44
Revises: f5b58c0adf38
Create Date: 2026-04-09
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b7c9f1a6d44'
down_revision = 'f5b58c0adf38'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('health_profiles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('body_fat_percentage', sa.Numeric(precision=5, scale=2), nullable=True))
        batch_op.add_column(sa.Column('body_fat_category', sa.String(length=50), nullable=True))

    op.create_table(
        'body_metric_references',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_dataset', sa.String(length=40), nullable=False),
        sa.Column('weight', sa.Numeric(precision=8, scale=3), nullable=True),
        sa.Column('height', sa.Numeric(precision=8, scale=5), nullable=True),
        sa.Column('bmi', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('body_fat_percentage', sa.Numeric(precision=8, scale=4), nullable=True),
        sa.Column('bfp_case', sa.String(length=50), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('bmi_case', sa.String(length=50), nullable=True),
        sa.Column('exercise_recommendation_plan', sa.Integer(), nullable=True),
        sa.Column('raw_payload', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('body_metric_references', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_body_metric_references_source_dataset'), ['source_dataset'], unique=False)
        batch_op.create_index(batch_op.f('ix_body_metric_references_bmi'), ['bmi'], unique=False)
        batch_op.create_index(batch_op.f('ix_body_metric_references_gender'), ['gender'], unique=False)
        batch_op.create_index(batch_op.f('ix_body_metric_references_age'), ['age'], unique=False)
        batch_op.create_index(batch_op.f('ix_body_metric_references_bmi_case'), ['bmi_case'], unique=False)
        batch_op.create_index(batch_op.f('ix_body_metric_references_exercise_recommendation_plan'), ['exercise_recommendation_plan'], unique=False)

    op.create_table(
        'workout_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('session_date', sa.DateTime(), nullable=False),
        sa.Column('day_of_week', sa.Enum('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun', name='workout_session_day_enum'), nullable=True),
        sa.Column('goal_label', sa.String(length=80), nullable=True),
        sa.Column('goal_key', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('current_exercise_index', sa.Integer(), nullable=True),
        sa.Column('exercises', sa.JSON(), nullable=True),
        sa.Column('completed_exercises', sa.JSON(), nullable=True),
        sa.Column('total_duration_seconds', sa.Integer(), nullable=True),
        sa.Column('total_calories_burned', sa.Integer(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('workout_sessions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_workout_sessions_user_id'), ['user_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_workout_sessions_session_date'), ['session_date'], unique=False)
        batch_op.create_index(batch_op.f('ix_workout_sessions_status'), ['status'], unique=False)


def downgrade():
    with op.batch_alter_table('workout_sessions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_workout_sessions_status'))
        batch_op.drop_index(batch_op.f('ix_workout_sessions_session_date'))
        batch_op.drop_index(batch_op.f('ix_workout_sessions_user_id'))
    op.drop_table('workout_sessions')

    with op.batch_alter_table('body_metric_references', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_body_metric_references_exercise_recommendation_plan'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_bmi_case'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_age'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_gender'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_bmi'))
        batch_op.drop_index(batch_op.f('ix_body_metric_references_source_dataset'))
    op.drop_table('body_metric_references')

    with op.batch_alter_table('health_profiles', schema=None) as batch_op:
        batch_op.drop_column('body_fat_category')
        batch_op.drop_column('body_fat_percentage')
