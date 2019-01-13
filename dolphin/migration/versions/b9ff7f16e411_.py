"""Group and Skill migration

Revision ID: b9ff7f16e411
Revises: e371cfc0cb1e
Create Date: 2019-01-13 16:22:51.211459

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm, Table, Integer, Column
from sqlalchemy.ext.declarative import declarative_base

from dolphin.models import Skill, Group, Resource, Phase

# revision identifiers, used by Alembic.
revision = 'b9ff7f16e411'
down_revision = 'e371cfc0cb1e'
branch_labels = None
depends_on = None

Base = declarative_base()

OldResource = Table(Resource.__tablename__, Base.metadata,
    Column('id', Integer),
    Column('phase_id', Integer)
)


PROJECT_GROUP_ID_CONSTRAIN_NAME = 'project_group_id_fkey'
GROUP_PUBLIC_UNIQUE_CONSTRAIN_NAME = 'group_public_key'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.create_table('skill',
        sa.Column('phase_id', sa.Integer(), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['phase_id'], ['phase.id'], ),
        sa.ForeignKeyConstraint(['resource_id'], ['member.id'], ),
        sa.PrimaryKeyConstraint('phase_id', 'resource_id')
    )

    resources = session.query(OldResource) \
        .filter(OldResource.c.phase_id.isnot(None)) \
        .all()

    for resource in resources:
        skill = Skill(phase_id=resource.phase_id, resource_id=resource.id)
        session.add(skill)

    op.add_column('group', sa.Column('public', sa.BOOLEAN(), nullable=True))
    op.create_unique_constraint(
        table_name='group',
        columns=['public'],
        constraint_name=GROUP_PUBLIC_UNIQUE_CONSTRAIN_NAME,
    )

    op.drop_constraint('member_phase_id_fkey', 'member', type_='foreignkey')
    op.drop_column('member', 'phase_id')

    public_group = Group(title='Public', public=True)
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
    # ### end Alembic commands ###
    op.create_foreign_key(
        source_table='project',
        referent_table='group',
        local_cols=['group_id'],
        remote_cols=['id'],
        constraint_name=PROJECT_GROUP_ID_CONSTRAIN_NAME,
    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        PROJECT_GROUP_ID_CONSTRAIN_NAME,
        'project',
        type_='foreignkey'
    )
    op.drop_column('project', 'group_id')
    op.add_column(
        'member',
        sa.Column('phase_id', sa.INTEGER(), autoincrement=False, nullable=True)
    )
    op.create_foreign_key(
        'member_phase_id_fkey',
        'member',
        'phase',
        ['phase_id'],
        ['id']
    )
    op.drop_constraint(
        GROUP_PUBLIC_UNIQUE_CONSTRAIN_NAME,
        'group',
        type_='unique'
    )
    op.drop_column('group', 'public')

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    skills = session.query(Skill) \
        .join(Resource, Skill.resource_id == Resource.id)\
        .all()

    for skill in skills:
        op.execute(
            f'UPDATE member SET phase_id={skill.phase_id}'
                f' WHERE id = {skill.resource_id}'
        )

    op.drop_table('skill')
    # ### end Alembic commands ###
