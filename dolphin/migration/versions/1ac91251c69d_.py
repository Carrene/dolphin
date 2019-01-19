"""Added seen_at column in subscription

Revision ID: 1ac91251c69d
Revises: 73746e131fec
Create Date: 2019-01-16 16:48:03.732520

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ac91251c69d'
down_revision = '73746e131fec'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'subscription',
        sa.Column('seen_at', sa.DateTime(), nullable=True),
    )
    op.execute(
        'UPDATE subscription SET seen_at=subscribable.created_at '
        'FROM subscribable '
        'WHERE subscription.subscribable_id = subscribable.id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('subscription', 'seen_at')
    # ### end Alembic commands ###
