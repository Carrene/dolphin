from datetime import datetime

from restfulpy.orm import DeclarativeBase, TimestampMixin, ModifiedMixin, \
    FilteringMixin, OrderingMixin, Field, relationship, MetadataField
from sqlalchemy import Integer, ForeignKey, DateTime, Unicode, func, \
    CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property

from ..validators import DATETIME_PATTERN


class Activity(ModifiedMixin, TimestampMixin, FilteringMixin, OrderingMixin,
               DeclarativeBase):

    __tablename__ = 'activity'

    id = Field(Integer, primary_key=True,)

    item_id = Field(Integer, ForeignKey('item.id'), protected=True)

    start_time = Field(
        DateTime,
        nullable=True,
        required=False,
        default=None,
        label='Start Time',
        name='start_time',
        pattern=DATETIME_PATTERN,
        watermark='lorem ipson',
        example='2019-01-28T13:18:42.717091',
        pattern_description='%Y-%m-%dT%H:%M:%S.%f'
    )
    end_time = Field(
        DateTime,
        CheckConstraint('end_time > start_time'),
        nullable=True,
        required=False,
        default=None,
        pattern=DATETIME_PATTERN,
        label='End Time',
        name='end_time',
        python_type=datetime,
        watermark='lorem ipson',
        example='2019-01-28T13:18:42.717091',
        pattern_description='%Y-%m-%dT%H:%M:%S.%f'
    )
    description = Field(
        Unicode(256),
        nullable=True,
        required=False,
        default='',
        min_length=0,
        label='description',
        name='description',
        python_type=str,
        watermark='lorem ipson',
    )


    item = relationship(
        'Item',
        protected=False,
        foreign_keys=item_id,
        uselist=False,
        readonly=True,
    )

    @hybrid_property
    def time_span(self):
        try:
            return (self.end_time - self.start_time).seconds
        except TypeError:
            return None

    @time_span.expression
    def time_span(self):
        # 'EPOCH' is used to convert timedelta to seconds
        func.extract('EPOCH', self.end_time - self.start_time)

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='timeSpan',
            key='time_span',
            label='Time Span',
            required=False,
            readonly=True,
            protected=False,
            type_=int,
            message='Activity duration in seconds',
            watermark='lorem ipsum',
            example='3600'
        )
