"""empty message

Revision ID: daaef7a0d527
Revises: 83f83a1005d0
Create Date: 2019-01-08 17:26:03.267826

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'daaef7a0d527'
down_revision = '83f83a1005d0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('member', sa.Column('phase_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'member', 'phase', ['phase_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'member', type_='foreignkey')
    op.drop_column('member', 'phase_id')
    # ### end Alembic commands ###
