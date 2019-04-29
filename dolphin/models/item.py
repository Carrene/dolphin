from datetime import datetime

from restfulpy.orm import Field, DeclarativeBase, relationship
from restfulpy.orm.mixins import TimestampMixin
from sqlalchemy import Integer, ForeignKey, UniqueConstraint, DateTime, Enum


item_statuses = [
    'to-do',
    'in-progress',
    'on-hold',
    'delayed',
    'complete',
]


class Item(TimestampMixin, DeclarativeBase):
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
    start_time = Field(
        DateTime,
        python_type=datetime,
        label='Assignment Start Time',
        pattern=
            r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])'
            r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$',
        pattern_description='ISO format and format like "yyyy-mm-dd" is valid',
        example='2018-02-02T1:12:12.000Z',
        nullable=True,
        not_none=False,
        required=False,
        readonly=True,
    )
    end_time = Field(
        DateTime,
        python_type=datetime,
        label='Assignment Start Time',
        pattern=
            r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])'
            r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$',
        pattern_description='ISO format and format like "yyyy-mm-dd" is valid',
        example='2018-02-02T1:12:12.000Z',
        nullable=True,
        not_none=False,
        required=False,
        readonly=True,
    )
    status = Field(
        Enum(*item_statuses, name='item_status'),
        python_type=str,
        default='to-do',
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
    phase_id = Field(Integer, ForeignKey('phase.id'))
    issue_id = Field(Integer, ForeignKey('issue.id'))
    member_id = Field(Integer, ForeignKey('member.id'))

    issues = relationship(
        'Issue',
        foreign_keys=issue_id,
        back_populates='items'
    )

    UniqueConstraint(phase_id, issue_id, member_id)

