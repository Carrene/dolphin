"""batch model

Revision ID: bc68448183f5
Revises: a2f4987dc1be
Create Date: 2019-07-01 17:55:27.123661

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc68448183f5'
down_revision = 'a2f4987dc1be'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('batch',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Unicode(length=50), nullable=False),
    sa.Column('project_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title', 'project_id', name='uix_title_project_id')
    )
    op.add_column('issue', sa.Column('batch_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'issue', 'batch', ['batch_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'issue', type_='foreignkey')
    op.drop_column('issue', 'batch_id')
    op.drop_table('batch')
    # ### end Alembic commands ###
