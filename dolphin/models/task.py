
from sqlalchemy import Integer, Time, ForeignKey, Date, Enum
from restfulpy.orm import Field
from restfulpy.orm.mixins import TimestampMixin

from .subscribable import Subscribable


class Task(Subscribable):
    __abstract__ = False
    __tablename__ = 'task'
    __mapper_args__ = {'polymorphic_identity': 'task'}

    project_id = Field('Project', ForeignKey('project.id'))
    kind= Field(
        Enum('feature', 'enhancement', 'bug', name='kind'),
    )
    duration = Field(Time, example='10 hours')
    status = Field(
        Enum('in-progress', 'on-hold', 'delayed', 'complete', name='status'),
    )

