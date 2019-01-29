from restfulpy.orm import DeclarativeBase, TimestampMixin, ModifiedMixin, \
    FilteringMixin, OrderingMixin, Field, relationship
from sqlalchemy import Integer, ForeignKey, DateTime, Unicode, CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property


class Activity(TimestampMixin, ModifiedMixin, FilteringMixin, OrderingMixin,
               DeclarativeBase):

    __tablename__ = 'activity'

    id = Field(Integer, primary_key=True)

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
    )

    @hybrid_property
    def time(self):
        return (self.end_time > self.start_time).seconds / 3600

    CheckConstraint('end_time > start_time', name='time_never_goes_back')
