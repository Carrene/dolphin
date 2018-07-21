
from sqlalchemy import Integer, Time, ForeignKey, DateTime, Enum
from restfulpy.orm import Field
from restfulpy.orm.mixins import TimestampMixin

from .subscribable import Subscribable


class Task(Subscribable):
    __tablename__ = 'task'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
#    tag_id = Field(Integer, ForeignKey('tag.id'))
#    stage_id = Field(Integer, ForeignKey('stage.id'))
    kind = Field(
        Enum('feature', 'enhancement', 'bug', name='kind'),
    )
    duration = Field(DateTime)
    status = Field(
        Enum('in-progress', 'on-hold', 'delayed', 'complete', name='status'),
    )


