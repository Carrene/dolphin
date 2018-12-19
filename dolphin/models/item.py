from datetime import datetime

from restfulpy.orm import Field, DeclarativeBase, relationship
from restfulpy.orm.mixins import TimestampMixin
from sqlalchemy import DateTime, Integer, ForeignKey, Enum


item_statuses = [
    'in-progress',
    'on-hold',
    'delayed',
    'complete',
]


class Item(TimestampMixin, DeclarativeBase):
    __tablename__ = 'item'

    phase_id = Field(Integer, ForeignKey('phase.id'), primary_key=True)
    issue_id = Field(Integer, ForeignKey('issue.id'), primary_key=True)
    resource_id = Field(Integer, ForeignKey('member.id'), nullable=True)
    status = Field(
        Enum(*item_statuses, name='item_status'),
        python_type=str,
        label='Status',
        watermark='Choose a status',
        nullable=True,
        required=False,
        example='Lorem Ipsum',
        message='Lorem Ipsum'
    )
    end = Field(
        DateTime,
        python_type=datetime,
        label='End',
        pattern=
            r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])'
            r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$',
        pattern_description='ISO format and format like "yyyy-mm-dd" is valid',
        example='2018-02-02T1:12:12.000Z',
        watermark='Enter a end time',
        nullable=True,
        required=False,
        message='Lorem Ipsum'
    )

    resource = relationship('Resource', back_populates='items', protected=True)

