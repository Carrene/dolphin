"""empty message

Revision ID: 5be0417cfc4c
Revises: 84d5fef5976a
Create Date: 2019-05-19 12:16:24.555494

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5be0417cfc4c'
down_revision = '84d5fef5976a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item', sa.Column('end_date', sa.DateTime(), nullable=True))
    op.add_column('item', sa.Column('start_date', sa.DateTime(), nullable=True))
    op.drop_column('item', 'end_time')
    op.drop_column('item', 'start_time')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'item',
        sa.Column(
            'start_time',
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True
        )
    )
    op.add_column(
        'item',
        sa.Column(
            'end_time',
            postgresql.TIMESTAMP(),
            autoincrement=False,
            nullable=True
        )
    )
    op.drop_column('item', 'start_date')
    op.drop_column('item', 'end_date')
    # ### end Alembic commands ###
