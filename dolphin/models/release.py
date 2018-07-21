
from sqlalchemy import Integer, Enum, DateTime, Time, ForeignKey
from restfulpy.orm import Field, relationship

from .subscribable import Subscribable


class Release(Subscribable):
    __tablename__ = 'release'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    admin_id = Field(Integer, ForeignKey('admin.id'))
    status = Field(
        Enum('in-progress', 'on-hold', 'delayed', 'complete', name='status'),
    )
    cutoff = Field(DateTime)

    projects = relationship('Project', backref='release')


