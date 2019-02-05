"""empty message

Revision ID: 7323ff813477
Revises: b4aea59e6385
Create Date: 2019-02-03 17:29:38.998866

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7323ff813477'
down_revision = '100c43e750ce'
branch_labels = None
depends_on = None


ATTACHMENT_ISSUE_ID_CONSTRAINT_NAME = 'attachment_issue_id_fkey'


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        'attachment',
        sa.Column('issue_id', sa.Integer(), nullable=True)
    )
    op.alter_column(
        'attachment',
        'project_id',
        existing_type=sa.INTEGER(),
        nullable=True
    )
    op.create_foreign_key(
        ATTACHMENT_ISSUE_ID_CONSTRAINT_NAME,
        'attachment',
        'issue',
        ['issue_id'],
        ['id']
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        ATTACHMENT_ISSUE_ID_CONSTRAINT_NAME,
        'attachment',
        type_='foreignkey'
    )
    op.alter_column(
        'attachment', 'project_id',
        existing_type=sa.INTEGER(),
        nullable=False
    )
    op.drop_column('attachment', 'issue_id')
    # ### end Alembic commands ###
