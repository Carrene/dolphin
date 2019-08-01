"""Added skill table

Revision ID: 1c26290cdc15
Revises: 2d858ff4365b
Create Date: 2019-08-01 13:30:28.721106

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

from dolphin.models import Skill


# revision identifiers, used by Alembic.
revision = '1c26290cdc15'
down_revision = '2d858ff4365b'
branch_labels = None
depends_on = None


SPECIALTY_SKILL_ID_FK = 'specialty_skill_id_fk'


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    op.create_table(
        'skill',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column(
        'specialty',
        sa.Column('skill_id', sa.Integer(), nullable=True)
    )
    op.create_foreign_key(
        SPECIALTY_SKILL_ID_FK,
        'specialty',
        'skill',
        ['skill_id'],
        ['id']
    )
    skill = Skill(
        title='Development',
    )
    session.add(skill)
    session.commit()
    op.execute(f'UPDATE specialty SET skill_id = {skill.id};')
    op.execute('ALTER TABLE specialty ALTER COLUMN skill_id SET NOT NULL')

def downgrade():
    op.drop_constraint(SPECIALTY_SKILL_ID_FK, 'specialty', type_='foreignkey')
    op.drop_column('specialty', 'skill_id')
    op.drop_table('skill')

