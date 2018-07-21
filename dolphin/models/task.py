
from sqlalchemy import Integer, Time, ForeignKey, DateTime, Enum, String
from restfulpy.orm import Field, DeclarativeBase, TimestampMixin, relationship

from .subscribable import Subscribable


class Tag(DeclarativeBase):
    __tablename__ = 'tag'

    id = Field(Integer, primary_key=True)
    name = Field(String, max_length=40, unique=True, example='feature')

    tasks = relationship('Task', backref='tag')


class Task(Subscribable):
    __tablename__ = 'task'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    tag_id = Field(Integer, ForeignKey('tag.id'))
#    stage_id = Field(Integer, ForeignKey('stage.id'))
    kind = Field(
        Enum('feature', 'enhancement', 'bug', name='kind'),
    )
    duration = Field(DateTime)
    status = Field(
        Enum('in-progress', 'on-hold', 'delayed', 'complete', name='status'),
    )


