
from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field

from .stakeholder import Stakeholder


class Resource(Stakeholder):
    __tablename__ = 'Resource'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

#    team_id = Field(Integer, ForeignKey('team.id'))
    id = Field(Integer, ForeignKey('stakeholder.id'), primary_key=True)


#    items = relationship('Item', backref='resource'))

