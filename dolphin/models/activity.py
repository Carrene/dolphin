from datetime import datetime

from nanohttp import context
from restfulpy.orm import DeclarativeBase, TimestampMixin, ModifiedMixin, \
    FilteringMixin, OrderingMixin, Field, relationship, MetadataField
from sqlalchemy import Integer, ForeignKey, DateTime, Unicode, func, \
    CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property

from ..validators import DATETIME_PATTERN, iso_to_datetime


DESCRIPTION_LENGTH = 256
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'


class Activity(ModifiedMixin, TimestampMixin, FilteringMixin, OrderingMixin,
               DeclarativeBase):

    __tablename__ = 'activity'

    id = Field(Integer, primary_key=True,)

    item_id = Field(Integer, ForeignKey('item.id'), protected=True)

    start_time = Field(
        DateTime,
        CheckConstraint('end_time > start_time'),
        CheckConstraint('start_time <= now() at time zone \'utc\''),
        nullable=True,
        required=False,
        not_none=False,
        default=None,
        label='Start Time',
        watermark='lorem ipson',
        example='2019-01-28T13:18:42.717091',
        pattern_description=ISO_FORMAT,
        python_type=(iso_to_datetime, '771 Invalid startTime Format')
    )
    end_time = Field(
        DateTime,
        CheckConstraint('end_time > start_time'),
        CheckConstraint('end_time <= now() at time zone \'utc\''),
        nullable=True,
        required=False,
        not_none=False,
        default=None,
        label='End Time',
        watermark='lorem ipson',
        example='2019-01-28T13:18:42.717091',
        pattern_description=ISO_FORMAT,
        python_type=(iso_to_datetime, '772 Invalid endTime Format')
    )
    description = Field(
        Unicode(DESCRIPTION_LENGTH),
        max_length=(DESCRIPTION_LENGTH, '773 Invalid description Format'),
        nullable=True,
        required=False,
        default='',
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

    @classmethod
    def extract_data_from_request(cls):
        for c in cls.iter_json_columns(
                include_protected_columns=False,
                include_readonly_columns=False
        ):
            info = cls.get_column_info(c)
            param_name = info.get('json')

            if param_name in context.form:

                if hasattr(c, 'property') and hasattr(c.property, 'mapper'):
                    raise HTTPBadRequest('Invalid attribute')

                value = context.form[param_name]
                yield c, value
