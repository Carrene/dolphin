"""empty message

Revision ID: b1831b40283c
Revises: 338edc1fd974
Create Date: 2019-07-29 16:15:00.896873

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1831b40283c'
down_revision = '338edc1fd974'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('ALTER TABLE member RENAME name to first_name;')
    op.add_column(
        'member',
        sa.Column('last_name', sa.Unicode(length=20), nullable=True)
    )


def downgrade():
    op.execute('ALTER TABLE member RENAME first_name to name;')
    op.drop_column('member', 'last_name')

