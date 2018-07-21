
from sqlalchemy import Integer, Time, ForeignKey, Enum
from sqlalchemy.orm import relationship
from restfulpy.orm import Field

from .subscribable import Subscribable


class Project(Subscribable):
    __tablename__ = 'project'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
#    admin_id = Field(Integer, ForeignKey('admin.id'))
#    release_id = Field(Integer, ForeignKey('release.id'))

    status = Field(
        Enum('in-progress', 'on-hold', 'delayed', 'complete', name='status'),
    )
    phase = Field(
        Enum('Done', 'Design', 'Impelemention', 'Deployment', name='phase'),
    )

#    stages = relationship('Stage', backref='project')

