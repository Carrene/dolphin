"""empty message

Revision ID: 5f206088190d
Revises: 936c432ce331
Create Date: 2019-06-16 13:00:31.184805

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import orm

from dolphin.models import Item, Issue, IssuePhase

from datetime import datetime, timedelta

from nanohttp import settings
from restfulpy.orm import Field, DeclarativeBase, relationship
from restfulpy.orm.metadata import MetadataField
from restfulpy.orm.mixins import TimestampMixin, OrderingMixin, \
    FilteringMixin, PaginationMixin
from sqlalchemy import Integer, ForeignKey, UniqueConstraint, DateTime, Enum, \
    String, select, func
from sqlalchemy.orm import column_property, synonym

from dolphin.models.dailyreport import Dailyreport


item_statuses = [
    'in-progress',
    'done',
]


class OldItem(TimestampMixin, OrderingMixin, FilteringMixin, PaginationMixin,
           DeclarativeBase):
    __tablename__ = 'old_item'

    id = Field(
        Integer,
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
        example=1,
        protected=False,
    )
    start_date = Field(
        DateTime,
        python_type=datetime,
        label='Start Date',
        pattern=
            r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])'
            r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$',
        pattern_description='ISO format and format like "yyyy-mm-dd" is valid',
        example='2018-02-02T1:12:12.000Z',
        nullable=True,
        not_none=False,
        required=False,
        readonly=False,
    )
    end_date = Field(
        DateTime,
        python_type=datetime,
        label='Target Date',
        pattern=
            r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])'
            r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$',
        pattern_description='ISO format and format like "yyyy-mm-dd" is valid',
        example='2018-02-02T1:12:12.000Z',
        nullable=True,
        not_none=False,
        required=False,
        readonly=False,
    )
    estimated_hours = Field(
        Integer,
        python_type=int,
        label='Estimated Hours',
        watermark='Enter hours you estimate',
        readonly=False,
        nullable=True,
        not_none=False,
        required=False,
    )
    _status = Field(
        Enum(*item_statuses, name='item_status'),
        python_type=str,
        default='in-progress',
        label='Status',
        watermark='Choose a status',
        nullable=True,
        required=False,
        example='Lorem Ipsum'
    )
    description = Field(
        String,
        min_length=1,
        max_length=512,
        label='Description',
        watermark='Enter the description',
        not_none=False,
        nullable=True,
        required=False,
        python_type=str,
        example='Lorem Ipsum'
    )
    phase_id = Field(
        Integer,
        ForeignKey('phase.id'),
        python_type=int,
        nullable=False,
        watermark='Choose a phase',
        label='Phase',
        not_none=True,
        required=True,
        example='Lorem Ipsum'
    )
    issue_id = Field(
        Integer,
        ForeignKey('issue.id'),
        python_type=int,
        nullable=False,
        watermark='Choose an issue',
        label='Issue',
        not_none=True,
        required=True,
        example='Lorem Ipsum'
    )
    member_id = Field(
        Integer,
        ForeignKey('member.id'),
        python_type=int,
        nullable=False,
        watermark='Choose a member',
        label='Member',
        not_none=True,
        required=True,
        example='Lorem Ipsum'
    )
    _last_status_change = Field(
        DateTime,
        python_type=datetime,
        nullable=True,
        protected=True,
    )

    hours_worked = column_property(
        select([func.sum(Dailyreport.hours)])
        .where(Dailyreport.item_id == id)
    )

    UniqueConstraint(phase_id, issue_id, member_id)

    @property
    def perspective(self):
        if len(self.dailyreports) == 0:
            return 'Due'

        for dailyreport in self.dailyreports:
            if dailyreport.note == None \
                    and dailyreport.date < datetime.now().date():
                return 'Overdue'

        if self.dailyreports[-1].note == None \
                and self.dailyreports[-1].date == datetime.now().date():
            return 'Due'

        return 'Submitted'

    def _set_status(self, status):
        if status == 'in-progress':
            self._last_status_change = datetime.now()

        self._status = status

    def _get_status(self):
        return self._status

    status = synonym(
        '_status',
        descriptor=property(_get_status, _set_status),
        info=dict(protected=True)
    )

    @property
    def response_time(self):
        if self.status == 'in-progress':
          return (
              (self._last_status_change or self.created_at) + \
              timedelta(hours=settings.item.response_time)
          ) - datetime.now()

    def to_dict(self):
        item_dict = super().to_dict()
        item_dict['responseTime'] = \
            self._get_hours_from_timedelta(self.response_time) \
            if self.response_time else None

        item_dict['hoursWorked'] = self.hours_worked
        item_dict['perspective'] = self.perspective
        return item_dict

    @staticmethod
    def _get_hours_from_timedelta( timedelta):
        return timedelta.seconds / 3600


# revision identifiers, used by Alembic.
revision = '5f206088190d'
down_revision = '936c432ce331'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    session = orm.Session(bind=bind)

    # ### commands auto generated by Alembic - please adjust! ###
    import pudb; pudb.set_trace()  # XXX BREAKPOINT
    op.create_table(
        'issue_phase',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phase_id', sa.Integer(), nullable=False),
        sa.Column('issue_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['issue_id'], ['issue.id'], ),
        sa.ForeignKeyConstraint(['phase_id'], ['phase.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute(
        "CREATE TYPE issue_stage AS ENUM ('triage', 'backlog', 'working', 'on-hold');"
    )
    op.execute(
        "ALTER TABLE issue ADD stage issue_stage;"
    )
    op.add_column('issue', sa.Column('is_done', sa.Boolean(), nullable=True))
    op.drop_column('issue', 'status')


    op.add_column('item', sa.Column('issue_phase_id', sa.Integer(), nullable=True))
    old_items = session.query(OldItem).all()
    for item in old_items:
        issue_phase = session.query(IssuePhase) \
            .filter(IssuePhase.issue_id == item.issue_id, IssuePhase.phase_id == item.phase_id) \
            .one_or_none()
        if issue_phase is None:
            issue_phase = IssuePhase(
                issue_id=item.issue_id,
                phase_id=item.phase_id,
            )
            session.add(issue_phase)
            session.commit()

        new_item = session.query(Item).get(item.id)
        new_item.issue_phase_id = issue_phase.id
        session.commit()

    op.drop_constraint('item_phase_id_issue_id_member_id_key', 'item', type_='unique')
    op.drop_constraint('item_issue_id_fkey', 'item', type_='foreignkey')
    op.drop_constraint('item_phase_id_fkey', 'item', type_='foreignkey')
    op.create_foreign_key(None, 'item', 'issue_phase', ['issue_phase_id'], ['id'])
    op.drop_column('item', '_last_status_change')
    op.drop_column('item', 'phase_id')
    op.drop_column('item', '_status')
    op.drop_column('item', 'issue_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('item', sa.Column('issue_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('item', sa.Column('_status', postgresql.ENUM('in-progress', 'done', name='item_status'), autoincrement=False, nullable=True))
    op.add_column('item', sa.Column('phase_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('item', sa.Column('_last_status_change', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'item', type_='foreignkey')
    op.create_foreign_key('item_phase_id_fkey', 'item', 'phase', ['phase_id'], ['id'])
    op.create_foreign_key('item_issue_id_fkey', 'item', 'issue', ['issue_id'], ['id'])
    op.create_unique_constraint('item_phase_id_issue_id_member_id_key', 'item', ['phase_id', 'issue_id', 'member_id'])
    op.drop_column('item', 'issue_phase_id')
    op.add_column('issue', sa.Column('status', postgresql.ENUM('to-do', 'in-progress', 'on-hold', 'complete', 'done', name='issues_status'), autoincrement=False, nullable=False))
    op.drop_column('issue', 'stage')
    op.drop_column('issue', 'is_done')
    op.drop_table('issue_phase')
    # ### end Alembic commands ###

