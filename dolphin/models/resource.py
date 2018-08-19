from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import DeclarativeBase, Field, relationship

from .member import Member


class TeamResource(DeclarativeBase):
    __tablename__ = 'resourceteam'

    team = Field(Integer, ForeignKey('team.id'), primary_key=True)
    resource = Field(Integer, ForeignKey('member.id'), primary_key=True)


class Resource(Member):
    __mapper_args__ = {'polymorphic_identity': 'resource'}

    items = relationship('Item', back_populates='resource', protected=True)
    teams = relationship(
        'Team',
        secondary='resourceteam',
        back_populates='resources',
        protected=True
    )

