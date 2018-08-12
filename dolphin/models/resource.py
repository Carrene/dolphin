
from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field, relationship

from .member import Member


class Resource(Member):
    __mapper_args__ = {'polymorphic_identity': 'resource'}

    team_id = Field(Integer, ForeignKey('team.id'), nullable=True)

    items = relationship('Item', back_populates='resource', protected=True)
    team = relationship('Team', back_populates='resources', protected=True)

