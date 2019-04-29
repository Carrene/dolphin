import datetime

from restfulpy.orm import Field, DeclarativeBase, OrderingMixin, \
    FilteringMixin, PaginationMixin, relationship
from sqlalchemy import Integer, Unicode, DateTime, ForeignKey


class Event(OrderingMixin, FilteringMixin, PaginationMixin, DeclarativeBase):
    __tablename__ = 'event'

    id = Field(
        Integer,
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
    )
    event_type_id = Field(
        Integer,
        ForeignKey('event_type.id'),
        python_type=int,
        watermark='lorem ipsum',
        label='Lorem ipsum',
        nullable=False,
        not_none=True,
        readonly=False,
        required=True,
    )
    title = Field(
        Unicode,
        max_length=50,
        min_length=1,
        label='lorem ipsum',
        watermark='lorem ipsum',
        example='lorem ipsum',
        nullable=False,
        not_none=True,
        required=True,
        python_type=str,
    )
    start_date= Field(
        DateTime,
        python_type=datetime,
        label='Start Date',
        pattern=
            r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])'
            r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$',
        pattern_description='ISO format and format like "yyyy-mm-dd" is valid',
        example='2018-02-02T1:12:12.000Z',
        watermark='Enter a start date',
        nullable=False,
        not_none=True,
        required=True,
    )
    end_date = Field(
        DateTime,
        python_type=datetime,
        label='End Date',
        pattern=
            r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])'
            r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$',
        pattern_description='ISO format and format like "yyyy-mm-dd" is valid',
        example='2018-02-02T1:12:12.000Z',
        watermark='Enter a end date',
        nullable=False,
        not_none=True,
        required=True,
    )
    description = Field(
        Unicode,
        min_length=1,
        max_length=512,
        label='Description',
        watermark='Lorem Ipsum',
        not_none=False,
        nullable=True,
        required=False,
        python_type=str,
        example='Lorem Ipsum',
    )
    event_type = relationship(
        'EventType',
        back_populates='events',
        protected=True,
    )

