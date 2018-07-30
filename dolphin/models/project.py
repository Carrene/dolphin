
from sqlalchemy import Integer, Time, ForeignKey, Enum
from sqlalchemy.orm import backref
from restfulpy.orm import Field, relationship

from .subscribable import Subscribable


project_statuses = [
    'in-progress',
    'on-hold',
    'delayed',
    'complete',
]


class Project(Subscribable):
    __tablename__ = 'project'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    manager_id = Field(Integer, ForeignKey('manager.id'))
    release_id = Field(Integer, ForeignKey('release.id'))

    status = Field(
        Enum(*project_statuses, name='project_status'),
        nullable=True
    )
    phase = Field(Enum(
        'design',
        'impelemention',
        'deployment',
        'done',
        name='project_phase'
    ), nullable=True)

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
        protected=True
    )

