
from sqlalchemy import Integer, Time, ForeignKey, Enum
from sqlalchemy.orm import backref
from restfulpy.orm import Field, relationship, SoftDeleteMixin, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin

from .issue import Issue
from .subscribable import Subscribable


project_statuses = [
    'in-progress',
    'on-hold',
    'delayed',
    'done',
]


class Project(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
              SoftDeleteMixin, Subscribable):

    __tablename__ = 'project'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    manager_id = Field(Integer, ForeignKey('member.id'))
    group_id = Field(Integer, ForeignKey('group.id'), nullable=True)

    status = Field(
        Enum(*project_statuses, name='project_status'),
        nullable=True
    )

    manager = relationship(
        'Manager',
        foreign_keys=[manager_id],
        back_populates='projects',
        protected=True
    )
    phases = relationship(
        'Phase',
        back_populates='project',
        protected=True
    )
    releases = relationship(
        'Release',
        secondary='releaseproject',
        back_populates='projects',
        protected=True
    )
    issues = relationship(
        'Issue',
        primaryjoin=id == Issue.project_id,
        back_populates='project',
        protected=True
    )
    group = relationship(
        'Group',
        back_populates='projects',
        protected=True
    )
