"""Add name to member

Revision ID: ef6e9f46fc46
Revises:
Create Date: 2018-11-26 20:25:49.834678

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
    op.create_table(
        'invitation',
        sa.Column(
            'by_member_id',
            sa.Integer,
            sa.ForeignKey('member.id'),
        ),
        sa.Column(
            'organization_id',
            sa.Integer,
            sa.ForeignKey('organization.id'),
        ),
        sa.Column('role', sa.Enum(*roles, name='roles')),
        sa.Column('accepted', sa.Boolean, default=False),
        sa.Column('expired_date', sa.DateTime, nullable=False),
        sa.Column('email', sa.Unicode(100), unique=True, index=True)
    )


def downgrade():
    pass

