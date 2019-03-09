""" on_shot subscription

Revision ID: ef87b57af36e
Revises: c5b39d97cc75
Create Date: 2019-03-09 16:26:00.782763

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm

from dolphin.models import Subscription


# revision identifiers, used by Alembic.
revision = 'ef87b57af36e'
down_revision = 'c5b39d97cc75'
branch_labels = None
depends_on = None


SUBSCRIPTION_PK_TITLE = 'subscription_pkey'


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.add_column(
        'subscription',
        sa.Column('created_at', sa.DateTime(), nullable=False)
    )
    op.add_column(
        'subscription',
        sa.Column('one_shot', sa.BOOLEAN(), nullable=True)
    )
    op.drop_constraint(
        SUBSCRIPTION_PK_TITLE,
        'subscription',
        type_='primary'
    )
    op.add_column(
        'subscription',
        sa.Column('id', sa.Integer(), nullable=True, primary_key=True)
    )

    subscriptions = session.query(Subscription).all()
    for index, subscription in enumerate(subscriptions):
        subscription.id = index
    session.commit()

    op.execute('ALTER TABLE subscription ADD PRIMARY KEY (id)')
    op.execute('ALTER TABLE subscription ALTER COLUMN id SET NOT NULL')


def downgrade():
    op.drop_column('subscription', 'one_shot')
    op.drop_constraint(
        SUBSCRIPTION_PK_TITLE,
        'subscription',
        type_='primary'
    )
    op.drop_column('subscription', 'id')
    op.drop_column('subscription', 'created_at')
    op.execute(
        'ALTER TABLE subscription ADD PRIMARY KEY (subscribable_id, member_id)'
    )
