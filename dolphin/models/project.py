
from sqlalchemy import Integer, Time, ForeignKey, Enum
from sqlalchemy.orm import backref
from restfulpy.orm import Field, relationship, SoftDeleteMixin

from .subscribable import Subscribable


project_statuses = [
    'in-progress',
    'on-hold',
    'delayed',
    'complete',
]


project_phases = [
    'design',
    'development',
    'deployment',
    'done'
]


class Project(SoftDeleteMixin, Subscribable):
    __tablename__ = 'project'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    manager_id = Field(Integer, ForeignKey('manager.id'))
    release_id = Field(Integer, ForeignKey('release.id'))

    status = Field(
        Enum(*project_statuses, name='project_status'),
        nullable=True
    )
    phase = Field(
        Enum(*project_phases, name='project_phase'),
        nullable=True
    )

    manager = relationship(
        'Manager',
        foreign_keys=[manager_id],
        back_populates='projects',
        protected=True
    )
    stages = relationship(
        'Stage',
        back_populates='project',
        protected=True
    )
    releases = relationship(
        'Release',
        foreign_keys=[release_id],
        backref='projects',
        protected=True
    )

