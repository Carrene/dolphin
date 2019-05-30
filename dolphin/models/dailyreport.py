from datetime import datetime

from restfulpy.orm import Field, DeclarativeBase, OrderingMixin, \
    FilteringMixin, PaginationMixin, relationship
from sqlalchemy import Integer, Unicode, ForeignKey, Date, Float


class Dailyreport(OrderingMixin, FilteringMixin, PaginationMixin, \
               DeclarativeBase):
    __tablename__ = 'dailyreport'

    item_id = Field(
        Integer,
        ForeignKey('item.id'),
        python_type=int,
        nullable=False,
        watermark='Choose a assginment',
        label='Assginment',
        not_none=True,
        required=True,
        example='Lorem Ipsum'
    )
    id = Field(
        Integer,
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
    )
    date = Field(
        Date,
        python_type=datetime.date,
        label='Date',
        pattern=r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])',
        pattern_description='ISO format like "yyyy-mm-dd" is valid',
        example='2018-02-02',
        watermark='Date of daily report',
        nullable=False,
        not_none=True,
        required=False,
        readonly=True,
    )
    hours = Field(
        Float,
        python_type=float,
        watermark='Hours spent on the assignment',
        label='Hours',
        example=2.5,
        nullable=True,
        not_none=False,
        required=True,
    )
    note = Field(
        Unicode,
        min_length=1,
        max_length=1024,
        label='Notes',
        watermark='Lorem Ipsum',
        not_none=False,
        nullable=True,
        required=True,
        python_type=str,
        example='Lorem Ipsum',
    )

    item = relationship(
        'Item',
        back_populates='dailyreports'
    )

