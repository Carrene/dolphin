from datetime import datetime, timedelta

from nanohttp import settings
from restfulpy.orm import Field, DeclarativeBase, relationship
from restfulpy.orm.metadata import MetadataField
from restfulpy.orm.mixins import TimestampMixin, OrderingMixin, \
    FilteringMixin, PaginationMixin
from sqlalchemy import Integer, ForeignKey, DateTime, Enum, String, select, \
    func, Boolean, case, any_, text, exists, cast
from sqlalchemy.orm import column_property, synonym
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.ext.hybrid import hybrid_property

from .dailyreport import Dailyreport
from ..constants import ITEM_RESPONSE_TIME


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
    issue_phase_id = Field(
        Integer,
        ForeignKey('issue_phase.id'),
        python_type=int,
        nullable=False,
        watermark='Lorem Ipsum',
        label='Lorem Ipsum',
        not_none=True,
        required=True,
        example='Lorem Ipsum',
    )
    is_done = Field(
        Boolean,
        python_type=bool,
        label='Lorem Ipsum',
        message='Lorem Ipsum',
        watermark='Lorem Ipsum',
        readonly=False,
        nullable=True,
        not_none=False,
        required=False,
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
    need_estimate_timestamp = Field(
        DateTime,
        python_type=datetime,
        nullable=True,
        not_none=False,
        required=False,
        readonly=False,
    )
    issue_phase = relationship(
        'IssuePhase',
        foreign_keys=issue_phase_id,
        back_populates='items',
        protected=False,
    )
    member = relationship(
        'Member',
        foreign_keys=member_id,
        back_populates='items',
        protected=True,
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
        .group_by(Dailyreport.item_id)
    )
    status = column_property(
        case([
            (
                estimated_hours <= select([func.sum(Dailyreport.hours)])
                .where(Dailyreport.item_id == id)
                .group_by(Dailyreport.item_id),
                'complete'
            ),
            (
                exists(
                    select([Dailyreport.item_id])
                    .where(Dailyreport.item_id == id)
                    .group_by(Dailyreport.item_id)
                ),
                'in-progress'
            ),
        ], else_='to-do').label('status'),
        deferred=True
    )

    perspective = column_property(
        case([
            (
                select([func.count(Dailyreport.hours)])
                .where(Dailyreport.item_id == id)
                .as_scalar() == 0,
                'due'
            ),
            (
                func.date_part('DAY', func.now() - start_date) >
                select([func.count(Dailyreport.id)])
                .where(Dailyreport.item_id == id)
                .where(Dailyreport.date < datetime.now().date())
                .as_scalar(),
                'overdue'
            ),
            (
                exists(
                    select([Dailyreport.note])
                    .where(Dailyreport.item_id == id)
                    .where(Dailyreport.date == datetime.now().date())
                    .where(Dailyreport.note.is_(None))
                ),
                'due'
            )
        ], else_='submitted').label('perspective'),
        deferred=True
    )

    @hybrid_property
    def response_time(self):
        if self.need_estimate_timestamp:
            return self.need_estimate_timestamp - \
                   datetime.now() + \
                   timedelta(hours=ITEM_RESPONSE_TIME)

        return None

    @response_time.expression
    def response_time(cls):
        # The constant `ITEM_RESPONSE_TIME` used in query below is derived from
        # constants.py instead of `nanohttp.settings`. Because before setting
        # up the models, `Issue` model is loaded; So the response_time
        # expression is loaded at this time also. Thus, settings is not
        # initialized yet.
        return case([
            (
                cls.need_estimate_timestamp != None,
                (
                    func.date_part(
                        'day',
                        cls.need_estimate_timestamp - func.now()
                    ) * 24
                ) + \
                (
                    func.date_part(
                        'hour',
                        cls.need_estimate_timestamp - func.now()
                    )
                ) + \
                ITEM_RESPONSE_TIME
            )
        ])

    def to_dict(self):
        item_dict = super().to_dict()
        item_dict['responseTime'] = \
            self._get_hours(self.response_time) \
            if self.response_time else None

        item_dict['hoursWorked'] = self.hours_worked
        item_dict['perspective'] = self.perspective
        item_dict['issue'] = self.issue_phase.issue.to_dict()
        item_dict['phaseId'] = self.issue_phase.phase_id
        item_dict['status'] = self.status
        return item_dict

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
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
        yield MetadataField(
            name='issue',
            key='issue',
            label='Issue',
            required=False,
            readonly=True,
            not_none=True,
            watermark='Lorem Ipsum',
            example='Lorem Ipsum',
            message='Lorem Ipsun',
        )
        yield MetadataField(
            name='phaseId',
            key='phase_id',
            label='PhaseId',
            required=False,
            readonly=True,
            not_none=True,
            watermark='Lorem Ipsum',
            example='Lorem Ipsum',
            message='Lorem Ipsun',
        )

    @staticmethod
    def _get_hours(timedelta):
        hours = 0
        if timedelta.days > 0:
            hours = timedelta.days * 24

        return hours + (timedelta.seconds // 3600)

