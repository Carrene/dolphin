"""Convert the skill model to the specialty

Revision ID: 338edc1fd974
Revises: 36e21154d542
Create Date: 2019-07-17 10:47:52.103737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '338edc1fd974'
down_revision = '36e21154d542'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'specialty',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=512), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'specialty_member',
        sa.Column('specialty_id', sa.Integer(), nullable=False),
        sa.Column('member_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['member_id'], ['member.id'], ),
        sa.ForeignKeyConstraint(['specialty_id'], ['specialty.id'], ),
        sa.PrimaryKeyConstraint('specialty_id', 'member_id'),
    )
    op.execute(
        'insert into specialty (id, title, description) '
        'select id, title, description from skill;'
    )
    op.execute('ALTER TABLE phase RENAME COLUMN skill_id TO specialty_id;')
    op.execute('ALTER TABLE member RENAME COLUMN skill_id TO specialty_id;')
    op.create_foreign_key(
        None,
        'member',
        'specialty',
        ['specialty_id'],
        ['id'],
    )
    op.create_foreign_key(
        None,
        'phase',
        'specialty',
        ['specialty_id'],
        ['id'],
    )
    op.execute(
        'insert into specialty_member (specialty_id, member_id) '
        'select skill_id, member_id from skill_member;'
    )

    op.drop_constraint('member_skill_id_fkey', 'member', type_='foreignkey')
    op.drop_constraint('phase_skill_id_fkey', 'phase', type_='foreignkey')
    op.drop_table('skill_member')
    op.drop_table('skill')


def downgrade():
    op.create_table(
        'skill',
        sa.Column(
            'id',
            sa.INTEGER(),
            server_default=sa.text("nextval('skill_id_seq'::regclass)"),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column(
            'title',
            sa.VARCHAR(length=50),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            'description',
            sa.VARCHAR(length=512),
            autoincrement=False,
            nullable=True,
        ),
        sa.PrimaryKeyConstraint('id', name='skill_pkey'),
        postgresql_ignore_search_path=False
    )
    op.create_table(
        'skill_member',
        sa.Column(
            'skill_id',
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            'member_id',
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['member_id'],
            ['member.id'],
            name='skill_member_member_id_fkey',
        ),
        sa.ForeignKeyConstraint(
            ['skill_id'],
            ['skill.id'],
            name='skill_member_skill_id_fkey',
        ),
        sa.PrimaryKeyConstraint(
            'skill_id',
            'member_id',
            name='skill_member_pkey',
        )
    )
    op.execute(
        'insert into skill(id, title, description) '
        'select id, title, description from specialty;'
    )
    op.execute(
        'insert into skill_member (skill_id, member_id) '
        'select specialty_id, member_id from specialty_member;'
    )
    op.execute('ALTER TABLE phase RENAME COLUMN specialty_id TO skill_id;')
    op.execute('ALTER TABLE member RENAME COLUMN specialty_id TO skill_id;')
    op.create_foreign_key(
        'phase_skill_id_fkey',
        'phase',
        'skill',
        ['skill_id'],
        ['id']
    )
    op.create_foreign_key(
        'member_skill_id_fkey',
        'member',
        'skill',
        ['skill_id'],
        ['id']
    )

    op.drop_constraint('member_specialty_id_fkey', 'member', type_='foreignkey')
    op.drop_constraint('phase_specialty_id_fkey', 'phase', type_='foreignkey')
    op.drop_table('specialty_member')
    op.drop_table('specialty')

