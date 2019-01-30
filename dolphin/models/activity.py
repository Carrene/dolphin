from datetime import datetime

from restfulpy.orm import DeclarativeBase, TimestampMixin, ModifiedMixin, \
    FilteringMixin, OrderingMixin, Field, relationship, MetadataField
from sqlalchemy import Integer, ForeignKey, DateTime, Unicode, func, \
    CheckConstraint

from sqlalchemy.ext.hybrid import hybrid_property


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
        name='startTime',
        python_type=datetime,
        watermark='lorem ipson',
    )
    end_time = Field(
        DateTime,
        nullable=True,
        required=False,
        default=None,
        label='End Time',
        name='endTime',
        python_type=datetime,
        watermark='lorem ipson',
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
            return (self.end_time > self.start_time).seconds
        except TypeError:
            return None

    @time_span.expression
    def time_span(self):
        # 'EPOCH' is used to convert timedelta to seconds
        func.extract('EPOCH', self.end_time > self.start_time)

    CheckConstraint('end_time > start_time', name='time_never_goes_back')

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
