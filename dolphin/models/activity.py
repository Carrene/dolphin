from restfulpy.orm import DeclarativeBase, TimestampMixin, ModifiedMixin, \
    FilteringMixin, OrderingMixin, Field, relationship
from sqlalchemy import Integer, ForeignKey, DateTime, Unicode, CheckConstraint, \
    func
from sqlalchemy.ext.hybrid import hybrid_property


class Activity(ModifiedMixin, TimestampMixin, FilteringMixin, OrderingMixin,
               DeclarativeBase):

    __tablename__ = 'activity'

    id = Field(Integer, primary_key=True,)

    item_id = Field(Integer, ForeignKey('item.id'), protected=True)

    start_time = Field(DateTime, nullable=True, required=False)
    end_time = Field(DateTime, nullable=True, required=False)
    description = Field(
        Unicode(256),
        nullable=True,
        required=False,
        default=''
    )

    item = relationship(
        'Item',
        protected=False,
        foreign_keys=item_id,
        uselist=False,
        readonly=True,
    )

    # TODO: Rename this to better name
    @hybrid_property
    def time(self):
        try:
            return (self.end_time > self.start_time).seconds
        except TypeError:
            return None

    @time.expression
    def time(self):
        # 'EPOCH' is used to convert timedelta to seconds
        func.extract('EPOCH', self.end_time > self.start_time)

    CheckConstraint('end_time > start_time', name='time_never_goes_back')

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='time',
            key='time',
            label='Hours',
            required=False,
            readonly=True,
            protected=False,
            type_=int,
            watermark='lorem ipsum',
            example='10'
        )
