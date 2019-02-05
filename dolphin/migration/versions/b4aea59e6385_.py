"""empty message

Revision ID: b4aea59e6385
Revises: 100c43e750ce
Create Date: 2019-01-31 13:11:58.389891

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b4aea59e6385'
down_revision = '100c43e750ce'
branch_labels = None
depends_on = None


ITEM_PHASE_ID_ISSUE_ID_MEMBER_ID_CONSTRAINT_NAME = 'item_phase_id_issue_id_member_id_key'


def upgrade():
    # This migration is removed because it was in a wrong place and make no
    # sense and it is moved to ea2e299a81af_.py
    pass


def downgrade():
    pass

