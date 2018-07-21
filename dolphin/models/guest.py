
from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field

from .stakeholder import Stakeholder


class Guest(Stakeholder):
    __tablename__ = 'guest'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('stakeholder.id'), primary_key=True)

