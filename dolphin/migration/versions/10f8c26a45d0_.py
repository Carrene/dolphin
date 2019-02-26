"""Revert on_shot subscription

Revision ID: 10f8c26a45d0
Revises: 33ff760bd18c
Create Date: 2019-02-26 18:51:16.311743

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '10f8c26a45d0'
down_revision = '33ff760bd18c'
branch_labels = None
depends_on = None


SUBSCRIPTION_PK_TITLE = 'subscription_pkey'


def upgrade():
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


def downgrade():
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