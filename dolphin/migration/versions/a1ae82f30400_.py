"""Added Group to Projects

Revision ID: a1ae82f30400
Revises: e371cfc0cb1e
Create Date: 2019-01-12 18:57:01.035153

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm

from dolphin.models import Group


# revision identifiers, used by Alembic.
revision = 'a1ae82f30400'
down_revision = 'e371cfc0cb1e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('group', sa.Column('is_public', sa.BOOLEAN(), nullable=True))
    op.create_unique_constraint(None, 'group', ['is_public'])
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    public_group = Group(title='Public', is_public=True)
    session.add(public_group)
    session.flush()

    op.add_column(
        'project',
        sa.Column(
            'group_id',
            sa.Integer(),
            nullable=False,
            default=public_group.id)
    )
    op.create_foreign_key(None, 'project', 'group', ['group_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'project', type_='foreignkey')
    op.drop_column('project', 'group_id')
    op.drop_constraint(None, 'group', type_='unique')
    op.drop_column('group', 'is_public')
    # ### end Alembic commands ###
