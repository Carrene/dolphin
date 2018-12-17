"""add organization

Revision ID: ef6e9f46fc46
Revises: 31f51bad2b24
Create Date: 2018-12-17 14:42:33.449580

"""
from alembic import op
import sqlalchemy as sa
from dolphin.models.organization import Logo, roles


# revision identifiers, used by Alembic.
revision = 'ef6e9f46fc46'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'organization',
        sa.Column('title', sa.Unicode(50), index=True),
        sa.Column('url', sa.Unicode(50), nullable=True),
        sa.Column('domain', sa.Unicode(50), nullable=True),
        sa.Column('_logo', Logo.as_mutable(sa.JSON), nullable=True)
    )
    op.create_table(
        'organization_member',
        sa.Column(
            'member_id',
            sa.Integer,
            sa.ForeignKey('member.id'),
            primary_key=True
        ),
        sa.Column(
            'organization_id',
            sa.Integer,
            sa.ForeignKey('organization.id'),
            primary_key=True
        ),
        sa.Column('role', sa.Enum(*roles, name='roles'))
    )


def downgrade():
    pass

