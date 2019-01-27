"""empty message

Revision ID: 100c43e750ce
Revises: 1ac91251c69d
Create Date: 2019-01-27 11:46:20.779103

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Table, Integer, Column, orm
from sqlalchemy.ext.declarative import declarative_base

from dolphin.models import Skill, Phase


# revision identifiers, used by Alembic.
revision = '100c43e750ce'
down_revision = '1ac91251c69d'
branch_labels = None
depends_on = None


Base = declarative_base()

OldSkill = Table(Skill.__tablename__, Base.metadata,
    Column('phase_id', Integer),
    Column('resource_id', Integer)
)


PHASE_SKILL_ID_CONSTRAINT_NAME = 'phase_skill_id_fkey'
MEMBER_SKILL_ID_CONSTRAINT_NAME = 'member_skill_id_fkey'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.execute('DELETE FROM skill')

    op.drop_constraint('skill_phase_id_fkey', 'skill', type_='foreignkey')
    op.drop_constraint('skill_resource_id_fkey', 'skill', type_='foreignkey')
    op.drop_column('skill', 'phase_id')
    op.drop_column('skill', 'resource_id')

    op.execute('ALTER TABLE skill ADD COLUMN id SERIAL PRIMARY KEY;')

    op.add_column('skill', sa.Column('title', sa.String(length=50), nullable=False))

    op.add_column('member', sa.Column('skill_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        MEMBER_SKILL_ID_CONSTRAINT_NAME,
        'member',
        'skill',
        ['skill_id'],
        ['id']
    )

    op.add_column('phase', sa.Column('skill_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        PHASE_SKILL_ID_CONSTRAINT_NAME,
        'phase',
        'skill',
        ['skill_id'],
        ['id']
    )

    default_skill = session.query(Skill) \
        .filter(Skill.title == 'Project Manager') \
        .one()

    op.execute(f'UPDATE phase SET skill_id = {default_skill.id}')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.drop_constraint(
        PHASE_SKILL_ID_CONSTRAINT_NAME,
        'phase',
        type_='foreignkey'
    )
    op.drop_column('phase', 'skill_id')

    op.drop_constraint(
        MEMBER_SKILL_ID_CONSTRAINT_NAME,
        'member',
        type_='foreignkey'
    )
    op.drop_column('member', 'skill_id')

    op.drop_column('skill', 'title')
    op.drop_column('skill', 'id')

    op.execute('DELETE FROM skill')

    op.add_column('skill', sa.Column(
        'resource_id',
        sa.INTEGER(),
        autoincrement=False,
        nullable=False
    ))
    op.add_column('skill', sa.Column(
        'phase_id',
        sa.INTEGER(),
        autoincrement=False,
        nullable=False
    ))

    op.create_foreign_key(
        'skill_resource_id_fkey',
        'skill',
        'member',
        ['resource_id'],
        ['id']
    )
    op.create_foreign_key(
        'skill_phase_id_fkey',
        'skill',
        'phase',
        ['phase_id'],
        ['id']
    )

    # ### end Alembic commands ###

