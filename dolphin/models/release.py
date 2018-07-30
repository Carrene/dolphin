
from sqlalchemy import Integer, Enum, DateTime, Time, ForeignKey
from restfulpy.orm import Field, relationship

from .subscribable import Subscribable


release_statuses = [
    'in-progress',
    'on-hold',
    'delayed',
    'complete',
]


class Release(Subscribable):
    __tablename__ = 'release'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    manager_id = Field(Integer, ForeignKey('manager.id'))
    status = Field(
        Enum(*release_statuses, name='release_status'),
        nullable=True
    )

    cutoff = Field(DateTime)

    manager = relationship(
        'Manager',
        back_populates='releases',
        protected=True
    )
