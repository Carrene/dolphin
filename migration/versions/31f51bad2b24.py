"""Add name to member

Revision ID: 31f51bad2b24
Revises:
Create Date: 2018-11-26 20:25:49.834678

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31f51bad2b24'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('member', sa.Column('name', sa.Unicode(20), nullable=True))


def downgrade():
    pass
