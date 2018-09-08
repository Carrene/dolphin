
from sqlalchemy import Integer, Time, ForeignKey, Enum
from sqlalchemy.orm import backref
from restfulpy.orm import Field, relationship, SoftDeleteMixin, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin

from .issue import Issue
from .subscribable import Subscribable


project_statuses = [
    'active',
    'on-hold',
    'queued',
    'done',
]


class Project(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
              SoftDeleteMixin, Subscribable):

    __tablename__ = 'project'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    _boarding = ['on-time', 'delayed', 'at-risk']

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    release_id = Field(Integer, ForeignKey('release.id'), nullable=True)
    manager_id = Field(Integer, ForeignKey('member.id'))
    group_id = Field(Integer, ForeignKey('group.id'), nullable=True)
    room_id = Field(Integer)

    status = Field(
        Enum(*project_statuses, name='project_status'),
        default='queued'
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
    release = relationship(
        'Release',
        foreign_keys=[release_id],
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

    @property
    def boardings(self):
        raise NotImplementedError

    @property
    def _boardings(self):
        return ['on-time', 'at-risk', 'delayed']

