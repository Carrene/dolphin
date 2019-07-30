"""Remove batch table and make hours and note field not none on dailyreport table

Revision ID: 97a523b69ef9
Revises: b1831b40283c
Create Date: 2019-07-30 18:25:58.658111

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '97a523b69ef9'
down_revision = 'b1831b40283c'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'dailyreport',
        'hours',
        existing_type=postgresql.DOUBLE_PRECISION(precision=53),
        nullable=False
    )
    op.alter_column(
        'dailyreport', 'note',
        existing_type=sa.VARCHAR(),
        nullable=False
    )
    op.add_column('issue', sa.Column('batch', sa.Integer(), nullable=True))
    op.drop_constraint('issue_batch_id_fkey', 'issue', type_='foreignkey')
    op.drop_column('issue', 'batch_id')
    op.drop_table('batch')


def downgrade():
    op.create_table(
        'batch',
        sa.Column(
            'id',
            sa.INTEGER(),
            autoincrement=True,
            nullable=False
        ),
        sa.Column(
            'title',
            sa.VARCHAR(length=50),
            autoincrement=False,
            nullable=False
        ),
        sa.Column(
            'project_id',
            sa.INTEGER(),
            autoincrement=False,
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ['project_id'],
            ['project.id'],
            name='batch_project_id_fkey'
        ),
        sa.PrimaryKeyConstraint(
            'id',
            name='batch_pkey'
        ),
        sa.UniqueConstraint(
            'title',
            'project_id',
            name='uix_title_project_id'
        )
    )
    op.add_column(
        'issue',
        sa.Column('batch_id', sa.INTEGER(), autoincrement=False, nullable=True)
    )
    op.create_foreign_key(
        'issue_batch_id_fkey',
        'issue',
        'batch',
        ['batch_id'],
        ['id']
    )
    op.drop_column('issue', 'batch')
    op.alter_column(
        'dailyreport',
        'note',
        existing_type=sa.VARCHAR(),
        nullable=True
    )
    op.alter_column(
        'dailyreport', 'hours',
        existing_type=postgresql.DOUBLE_PRECISION(precision=53),
        nullable=True
    )

