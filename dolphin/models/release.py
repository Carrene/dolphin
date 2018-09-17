
from sqlalchemy import Integer, Enum, DateTime, Time, ForeignKey
from restfulpy.orm import Field, relationship, ModifiedMixin, FilteringMixin, \
    OrderingMixin, PaginationMixin, DeclarativeBase

from .subscribable import Subscribable
from .project import Project


release_statuses = [
    'in-progress',
    'on-hold',
    'delayed',
    'complete',
]


class Release(ModifiedMixin, FilteringMixin, OrderingMixin, PaginationMixin,
              Subscribable):

    __tablename__ = 'release'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    status = Field(
        Enum(*release_statuses, name='release_status'),
        nullable=True
    )
    cutoff = Field(DateTime)

    projects = relationship(
        'Project',
        primaryjoin=id == Project.release_id,
        back_populates='release',
        protected=True
    )

