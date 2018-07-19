
from sqlalchemy import Enum, Date, Time
from restfulpy.orm import Field, relationship

from .subscribable import Subscribable


class Release(Subscribable):
    __abstract__ = False
    __tablename__ = 'release'
    __mapper_args__ = {'polymorphic_identity': 'release'}

    due_date = Field(Time, example='16 hours')
    status = Field(
        Enum('in-progress', 'on-hold', 'delayed', 'complete', name='status'),
    )
    cutoff = Field(Date)


    projects = relationship('Project', backref='release')

