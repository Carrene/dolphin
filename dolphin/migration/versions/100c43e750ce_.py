"""empty message

Revision ID: 100c43e750ce
Revises: 1ac91251c69d
Create Date: 2019-01-27 11:46:20.779103

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Table, Integer, Column, orm
from sqlalchemy.ext.declarative import declarative_base

from dolphin.models import Specialty, Phase


# revision identifiers, used by Alembic.
revision = '100c43e750ce'
down_revision = '1ac91251c69d'
branch_labels = None
depends_on = None


Base = declarative_base()


OldSpecialty = Table(
    Specialty.__tablename__,
    Base.metadata,
    Column('phase_id', Integer),
    Column('resource_id', Integer)
)


PHASE_SKILL_ID_CONSTRAINT_NAME = 'phase_specialty_id_fkey'
MEMBER_SKILL_ID_CONSTRAINT_NAME = 'member_specialty_id_fkey'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.execute('DELETE FROM specialty')

    op.drop_constraint('specialty_phase_id_fkey', 'specialty', type_='foreignkey')
    op.drop_constraint('specialty_resource_id_fkey', 'specialty', type_='foreignkey')
    op.drop_column('specialty', 'phase_id')
    op.drop_column('specialty', 'resource_id')

    op.execute('ALTER TABLE specialty ADD COLUMN id SERIAL PRIMARY KEY;')

    op.add_column('specialty', sa.Column('title', sa.String(length=50), nullable=False))

    op.add_column('member', sa.Column('specialty_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        MEMBER_SKILL_ID_CONSTRAINT_NAME,
        'member',
        'specialty',
        ['specialty_id'],
        ['id']
    )

    op.add_column('phase', sa.Column('specialty_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        PHASE_SKILL_ID_CONSTRAINT_NAME,
        'phase',
        'specialty',
        ['specialty_id'],
        ['id']
    )

    default_specialty = session.query(Specialty) \
        .filter(Specialty.title == 'Project Manager') \
        .one()

    op.execute(f'UPDATE phase SET specialty_id = {default_specialty.id}')

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
    op.drop_column('phase', 'specialty_id')

    op.drop_constraint(
        MEMBER_SKILL_ID_CONSTRAINT_NAME,
        'member',
        type_='foreignkey'
    )
    op.drop_column('member', 'specialty_id')

    op.drop_column('specialty', 'title')
    op.drop_column('specialty', 'id')

    op.execute('DELETE FROM specialty')

    op.add_column('specialty', sa.Column(
        'resource_id',
        sa.INTEGER(),
        autoincrement=False,
        nullable=False
    ))
    op.add_column('specialty', sa.Column(
        'phase_id',
        sa.INTEGER(),
        autoincrement=False,
        nullable=False
    ))

    op.create_foreign_key(
        'specialty_resource_id_fkey',
        'specialty',
        'member',
        ['resource_id'],
        ['id']
    )
    op.create_foreign_key(
        'specialty_phase_id_fkey',
        'specialty',
        'phase',
        ['phase_id'],
        ['id']
    )
    # ### end Alembic commands ###

