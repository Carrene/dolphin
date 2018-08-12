
from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field

from .stakeholder import Stakeholder


class Guest(Stakeholder):
    __mapper_args__ = {'polymorphic_identity': 'guest'}

