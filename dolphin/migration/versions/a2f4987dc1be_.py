"""Modified the created by mixin

Revision ID: a2f4987dc1be
Revises: 508a09c9f43a
Create Date: 2019-06-26 14:31:26.661081

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = 'a2f4987dc1be'
down_revision = '508a09c9f43a'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'issue',
        sa.Column('created_by_member_id', sa.Integer(), nullable=True)
    )
    op.add_column(
        'issue',
        sa.Column('created_by_reference_id', sa.Integer(), nullable=True)
    )
    op.drop_column('issue', 'created_by')
    op.execute('UPDATE issue SET created_by_reference_id = 34;')
    op.execute('UPDATE issue SET created_by_member_id = 33;')
    op.execute(
        'ALTER TABLE issue ALTER COLUMN created_by_member_id SET NOT NULL'
    )
    op.execute(
        'ALTER TABLE issue ALTER COLUMN created_by_reference_id SET NOT NULL'
    )


def downgrade():
    op.add_column(
        'issue',
        sa.Column('created_by', sa.INTEGER(), nullable=True)
    )
    op.drop_column('issue', 'created_by_reference_id')
    op.drop_column('issue', 'created_by_member_id')

    op.execute('UPDATE issue SET created_by = 33;')
    op.execute('ALTER TABLE issue ALTER COLUMN created_by SET NOT NULL')

