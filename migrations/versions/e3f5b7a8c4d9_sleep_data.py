"""Add sleep data models and update join_study_subject_api

Revision ID: e3f5b7a8c4d9
Revises: f267b6182686
Create Date: 2024-11-11 16:18:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3f5b7a8c4d9'
down_revision = 'f267b6182686'
branch_labels = None
depends_on = 'f267b6182686'


def upgrade():
    # ### Add new tables ###
    op.create_table(
        'sleep_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('study_subject_id', sa.Integer(), nullable=False),
        sa.Column('log_id', sa.BigInteger(), nullable=False),
        sa.Column('date_of_sleep', sa.Date(), nullable=False),
        sa.Column('duration', sa.Integer(), nullable=True),
        sa.Column('efficiency', sa.Integer(), nullable=True),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('info_code', sa.Integer(), nullable=True),
        sa.Column('is_main_sleep', sa.Boolean(), nullable=True),
        sa.Column('minutes_after_wakeup', sa.Integer(), nullable=True),
        sa.Column('minutes_asleep', sa.Integer(), nullable=True),
        sa.Column('minutes_awake', sa.Integer(), nullable=True),
        sa.Column('minutes_to_fall_asleep', sa.Integer(), nullable=True),
        sa.Column('log_type', sa.String(), nullable=True),
        sa.Column('start_time', sa.DateTime(), nullable=True),
        sa.Column('time_in_bed', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['study_subject_id'], ['study_subject.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('log_id')
    )
    op.create_index('ix_sleep_log_date_of_sleep', 'sleep_log',
                    ['date_of_sleep'], unique=False)
    op.create_index('ix_sleep_log_log_id', 'sleep_log',
                    ['log_id'], unique=True)
    op.create_index('ix_sleep_log_study_subject_id', 'sleep_log', [
                    'study_subject_id'], unique=False)

    op.create_table(
        'sleep_level',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sleep_log_id', sa.Integer(), nullable=False),
        sa.Column('date_time', sa.DateTime(), nullable=False),
        sa.Column('level', sa.String(), nullable=False),
        sa.Column('seconds', sa.Integer(), nullable=False),
        sa.Column('is_short', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['sleep_log_id'], ['sleep_log.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sleep_level_date_time', 'sleep_level',
                    ['date_time'], unique=False)
    op.create_index('idx_sleep_level_sleep_log_id_date_time', 'sleep_level', [
                    'sleep_log_id', 'date_time'], unique=False)

    op.create_table(
        'sleep_summary',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sleep_log_id', sa.Integer(), nullable=False),
        sa.Column('level', sa.String(), nullable=False),
        sa.Column('count', sa.Integer(), nullable=True),
        sa.Column('minutes', sa.Integer(), nullable=True),
        sa.Column('thirty_day_avg_minutes', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['sleep_log_id'], ['sleep_log.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # ### Modify join_study_subject_api ###
    with op.batch_alter_table('join_study_subject_api', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('last_sync_date', sa.Date(), nullable=True))
        batch_op.drop_constraint(
            'join_study_subject_api_access_key_uuid_key', type_='unique')
        batch_op.drop_constraint(
            'join_study_subject_api_refresh_key_uuid_key', type_='unique')
        batch_op.drop_column('access_key_uuid')
        batch_op.drop_column('refresh_key_uuid')

    # ### End Alembic commands ###


def downgrade():
    # ### Revert changes to join_study_subject_api ###
    with op.batch_alter_table('join_study_subject_api', schema=None) as batch_op:
        batch_op.add_column(sa.Column('refresh_key_uuid',
                            sa.String(), nullable=True))
        batch_op.add_column(sa.Column('access_key_uuid',
                            sa.String(), nullable=True))
        batch_op.create_unique_constraint(
            'join_study_subject_api_refresh_key_uuid_key', ['refresh_key_uuid'])
        batch_op.create_unique_constraint(
            'join_study_subject_api_access_key_uuid_key', ['access_key_uuid'])
        batch_op.drop_column('last_sync_date')

    # ### Drop new tables ###
    op.drop_table('sleep_summary')
    op.drop_index('idx_sleep_level_sleep_log_id_date_time',
                  table_name='sleep_level')
    op.drop_index('ix_sleep_level_date_time', table_name='sleep_level')
    op.drop_table('sleep_level')
    op.drop_index('ix_sleep_log_study_subject_id', table_name='sleep_log')
    op.drop_index('ix_sleep_log_log_id', table_name='sleep_log')
    op.drop_index('ix_sleep_log_date_of_sleep', table_name='sleep_log')
    op.drop_table('sleep_log')

    # ### End Alembic commands ###
