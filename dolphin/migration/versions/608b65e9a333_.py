"""empty message

Revision ID: 608b65e9a333
Revises: 9659db034551
Create Date: 2019-02-13 18:01:49.529705

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '608b65e9a333'
down_revision = '9659db034551'
branch_labels = None
depends_on = None


PROJECT_MANGER_ID_FKEY = 'project_manager_id_fkey'


def upgrade():
    op.execute('ALTER TABLE project RENAME COLUMN member_id TO manager_id;')
    op.execute(
        'ALTER TABLE project RENAME CONSTRAINT "project_member_id_fkey" '
        'TO "project_manager_id_fkey"; '
    )
    # ### end Alembic commands ###


def downgrade():
    op.execute('ALTER TABLE project RENAME COLUMN manager_id TO member_id;')
    op.execute(
        'ALTER TABLE project RENAME CONSTRAINT "project_manager_id_fkey" '
        'TO "project_member_id_fkey"; '
    )
    # ### end Alembic commands ###
