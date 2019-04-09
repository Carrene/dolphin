"""empty message

Revision ID: 8b5f59f842ae
Revises: fbf36ff71e51
Create Date: 2019-04-09 12:10:26.460573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b5f59f842ae'
down_revision = 'fbf36ff71e51'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('group_member',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ),
    sa.ForeignKeyConstraint(['member_id'], ['member.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'member_id')
    )
    op.create_table('skill_member',
    sa.Column('skill_id', sa.Integer(), nullable=False),
    sa.Column('member_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['member_id'], ['member.id'], ),
    sa.ForeignKeyConstraint(['skill_id'], ['skill.id'], ),
    sa.PrimaryKeyConstraint('skill_id', 'member_id')
    )
    op.add_column('group', sa.Column('description', sa.Unicode(), nullable=True))
    op.add_column('tag', sa.Column('description', sa.Unicode(), nullable=True))
    op.add_column('workflow', sa.Column('description', sa.Unicode(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    op.drop_column('workflow', 'description')
    op.drop_column('tag', 'description')
    op.drop_column('group', 'description')
    op.drop_table('skill_member')
    op.drop_table('group_member')
    # ### end Alembic commands ###
