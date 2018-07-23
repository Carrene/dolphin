
from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field, relationship

from .stakeholder import Stakeholder


class Resource(Stakeholder):
    __tablename__ = 'resource'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    team_id = Field(Integer, ForeignKey('team.id'))
    id = Field(Integer, ForeignKey('stakeholder.id'), primary_key=True)

    items = relationship('Item', back_populates='resource', protected=True)
    team = relationship('Team', back_populates='resources', protected=True)

