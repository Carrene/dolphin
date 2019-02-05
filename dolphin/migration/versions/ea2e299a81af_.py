"""Item migration

Revision ID: ea2e299a81af
Revises: 7323ff813477
Create Date: 2019-02-04 16:28:07.817784

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm

from dolphin.models import Item


# revision identifiers, used by Alembic.
revision = 'ea2e299a81af'
down_revision = '7323ff813477'
branch_labels = None
depends_on = None


ITEM_PHASE_ID_ISSUE_ID_MEMBER_ID_CONSTRAINT_NAME \
    = 'item_phase_id_issue_id_member_id_key'


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.drop_constraint('item_pkey', 'item', type_='primary')
    op.add_column('item', sa.Column('id', sa.Integer()))
    for index, item in enumerate(session.query(Item).all()):
        op.execute(
            f'UPDATE TABLE item SET id = {index} '
            f'WHERE issue_id = {item.issue_id} '
            f'AND phase_id = {item.phase_id} '
            f'AND member_id = {item.issue_id} '
        )

    op.execute('ALTER TABLE item ADD PRIMARY KEY (id)')

    op.create_unique_constraint(
        ITEM_PHASE_ID_ISSUE_ID_MEMBER_ID_CONSTRAINT_NAME,
        'item',
        ['phase_id', 'issue_id', 'member_id']
    )


def downgrade():
    op.drop_constraint(
        ITEM_PHASE_ID_ISSUE_ID_MEMBER_ID_CONSTRAINT_NAME,
        'item',
        type_='unique'
    )
    op.drop_column('activity', 'item_id')
    op.drop_column('item', 'id')
    op.execute(
        'ALTER TABLE item ADD PRIMARY KEY (phase_id,issue_id,member_id)'
    )
