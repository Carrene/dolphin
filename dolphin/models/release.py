
from sqlalchemy import Integer, Enum, DateTime, Time, ForeignKey
from restfulpy.orm import Field, relationship

from .subscribable import Subscribable


class Release(Subscribable):
    __tablename__ = 'release'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    administrator_id = Field(Integer, ForeignKey('administrator.id'))
    status = Field(
        Enum(
            'started',
            'in-progress',
            'on-hold',
            'delayed',
            'complete',
            name='status'
        ),
        nullable=True
    )
    cutoff = Field(DateTime)

    administrator = relationship('Administrator', back_populates='releases', protected=True)

