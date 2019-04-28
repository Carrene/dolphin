import datetime

from restfulpy.orm import Field, DeclarativeBase, OrderingMixin, FilteringMixin, PaginationMixin
from sqlalchemy import Integer, Unicode, DateTime


class TimeCard(OrderingMixin, FilteringMixin, PaginationMixin, \
               DeclarativeBase):
    __tablename__ = 'timecard'

    id = Field(
        Integer,
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
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
    estimated_time = Field(
        Integer,
        python_type=int,
        watermark='estimated time',
        label='estimated time',
        nullable=False,
        not_none=True,
        required=True
    )
    summary = Field(
        Unicode,
        min_length=1,
        max_length=1024,
        label='Lorem Isum',
        watermark='Lorem Ipsum',
        not_none=False,
        nullable=True,
        required=False,
        python_type=str,
        example='Lorem Ipsum',
    )

