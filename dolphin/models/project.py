
from sqlalchemy import Integer, Time, ForeignKey, Enum
from sqlalchemy.orm import relationship
from restfulpy.orm import Field

from .subscribable import Subscribable


class Project(Subscribable):
    __abstract__ = False
    __tablename__ = 'project'
    __mapper_args__ = {'polymorphic_identity': 'project'}

    release_id = Field(Integer, ForeignKey('release.id'))

    due_date = Field(Time, example='16 hours')
    status = Field(
        Enum('in-progress', 'on-hold', 'delayed', 'complete', name='status'),
    )
    phase = Field(
        Enum('Done', 'Design', 'Impelemention', 'Deployment', name='phase'),
    )

