from restfulpy.orm import Field, relationship, ModifiedMixin, FilteringMixin, \
    OrderingMixin, PaginationMixin
from sqlalchemy import Integer, Enum, DateTime, ForeignKey, select, func
from sqlalchemy.orm import column_property

from .project import Project
from .subscribable import Subscribable


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
        protected=True,
        lazy='selectin'
    )

    due_date = column_property(
        select([func.max(Project.due_date)]).\
            where(Project.release_id == id).\
            correlate_except(Project)
    )

    def to_dict(self):
        project_dict = super().to_dict()
        project_dict['dueDate'] = self.due_date
        return project_dict

