
from sqlalchemy import Integer, Time, ForeignKey, Enum
from sqlalchemy.orm import backref
from restfulpy.orm import Field, relationship

from .subscribable import Subscribable


class Project(Subscribable):
    __tablename__ = 'project'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    administrator_id = Field(Integer, ForeignKey('administrator.id'))
    release_id = Field(Integer, ForeignKey('release.id'))

    status = Field(
        Enum('in-progress', 'on-hold', 'delayed', 'complete', name='status'),
        nullable=True
    )
    phase = Field(
        Enum('Design', 'Impelemention', 'Deployment', 'Done', name='phase'),
        nullable=True
    )

    administrator = relationship(
        'Administrator',
        foreign_keys=[administrator_id],
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

