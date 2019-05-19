from restfulpy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr

from .subscribable import Subscribable
from .envelop import Envelop


class Room(Subscribable):
    __abstract__ = True
    __mapper_args__ = {
        'polymorphic_identity': 'room',
    }

    @declared_attr
    def envelops(cls):
        return relationship('Envelop')

