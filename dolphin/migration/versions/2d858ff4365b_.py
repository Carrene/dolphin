"""Add is_batch_leader field to issue

Revision ID: 2d858ff4365b
Revises: 97a523b69ef9
Create Date: 2019-07-31 17:56:19.150462

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2d858ff4365b'
down_revision = '97a523b69ef9'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'issue',
        sa.Column('is_batch_leader', sa.Boolean(), nullable=True)
    )


def downgrade():
    op.drop_column('issue', 'is_batch_leader')

