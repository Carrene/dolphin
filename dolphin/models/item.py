from datetime import datetime, timedelta

from nanohttp import settings
from restfulpy.orm import Field, DeclarativeBase, relationship
from restfulpy.orm.metadata import MetadataField
from restfulpy.orm.mixins import TimestampMixin, OrderingMixin, \
    FilteringMixin, PaginationMixin
from sqlalchemy import Integer, ForeignKey, UniqueConstraint, DateTime, Enum, \
    String, select, func
from sqlalchemy.orm import column_property, synonym

from .dailyreport import Dailyreport


item_statuses = [
    'in-progress',
    'done',
]


class Item(TimestampMixin, OrderingMixin, FilteringMixin, PaginationMixin,
           DeclarativeBase):
    __tablename__ = 'item'

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

    issue = relationship(
        'Issue',
        foreign_keys=issue_id,
        back_populates='items',
        protected=False,
    )
    dailyreports = relationship(
        'Dailyreport',
        back_populates='item',
        cascade='delete',
        lazy='selectin',
        order_by='Dailyreport.id',
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

        if self.dailyreports[-1].date < datetime.now().date():
            return 'Overdue'

        if self.dailyreports[-1].note != None:
            return 'Submitted'

        return 'Due'

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

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='issue',
            key='issue',
            label='Lorem Ipsun',
            required=False,
            readonly=True,
            watermark='Lorem Ipsum',
            example='Lorem Ipsum',
            message='Lorem Ipsun',
        )
        yield MetadataField(
            name='responseTime',
            key='response_time',
            label='Response Time',
            required=False,
            readonly=True,
            watermark='Lorem Ipsum',
            example='Lorem Ipsum',
            message='Lorem Ipsun',
        )

        yield MetadataField(
            name='perspective',
            key='perspective',
            label='Perspective',
            required=False,
            readonly=True,
            not_none=True,
            watermark='Lorem Ipsum',
            example='Lorem Ipsum',
            message='Lorem Ipsun',
        )

    @staticmethod
    def _get_hours_from_timedelta( timedelta):
        return timedelta.seconds / 3600

