"""empty message

Revision ID: 83f83a1005d0
Revises: 337b551307f3
Create Date: 2019-01-01 12:15:22.266465

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '83f83a1005d0'
down_revision = '337b551307f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('draft_issue',
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('modified_at', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('issue_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['issue_id'], ['issue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('draft_issue_tag',
    sa.Column('tag_id', sa.Integer(), nullable=False),
    sa.Column('draft_issue_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['draft_issue_id'], ['draft_issue.id'], ),
    sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ),
    sa.PrimaryKeyConstraint('tag_id', 'draft_issue_id')
    )
    op.add_column('issue', sa.Column('priority', sa.Enum('low', 'normal', 'high', name='priority'), nullable=True))
    op.alter_column('issue', 'project_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.add_column('item', sa.Column('member_id', sa.Integer(), nullable=False))
    op.drop_constraint('item_resource_id_fkey', 'item', type_='foreignkey')
    op.create_foreign_key(None, 'item', 'member', ['member_id'], ['id'])
    op.drop_column('item', 'resource_id')
    op.drop_column('item', 'end')
    op.drop_column('item', 'id')
    op.drop_column('item', 'status')
    op.add_column('tag', sa.Column('organization_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'tag', 'organization', ['organization_id'], ['id'])
    op.add_column('workflow', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('workflow', sa.Column('modified_at', sa.DateTime(), nullable=True))
    op.add_column('workflow', sa.Column('removed_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('workflow', 'removed_at')
    op.drop_column('workflow', 'modified_at')
    op.drop_column('workflow', 'created_at')
    op.drop_constraint(None, 'tag', type_='foreignkey')
    op.drop_column('tag', 'organization_id')
    op.drop_constraint(None, 'project', type_='foreignkey')
    op.add_column('item', sa.Column('status', postgresql.ENUM('in-progress', 'on-hold', 'delayed', 'complete', name='item_status'), autoincrement=False, nullable=True))
    op.add_column('item', sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False))
    op.add_column('item', sa.Column('end', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('item', sa.Column('resource_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.create_foreign_key('item_resource_id_fkey', 'item', 'member', ['resource_id'], ['id'])
    op.drop_column('item', 'member_id')
    op.alter_column('issue', 'project_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.drop_column('issue', 'priority')
    op.drop_table('draft_issue_tag')
    op.drop_table('draft_issue')
    # ### end Alembic commands ###
