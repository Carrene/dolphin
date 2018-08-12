
from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field, relationship

from .stakeholder import Stakeholder


class Resource(Stakeholder):
    __mapper_args__ = {'polymorphic_identity': 'resource'}

    team_id = Field(Integer, ForeignKey('team.id'))

    items = relationship('Item', back_populates='resource', protected=True)
    team = relationship('Team', back_populates='resources', protected=True)

