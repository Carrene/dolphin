from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, ForeignKey

from .member import Member


class TeamResource(DeclarativeBase):
    __tablename__ = 'resourceteam'

    team = Field(Integer, ForeignKey('team.id'), primary_key=True)
    resource = Field(Integer, ForeignKey('member.id'), primary_key=True)


class Resource(Member):
    __mapper_args__ = {'polymorphic_identity': 'resource'}

    phase_id = Field(Integer, ForeignKey('phase.id'), nullable=True)

    phase = relationship(
        'Phase',
        secondary='skill',
        lazy='selectin',
        back_populates='resources',
        protected=True,
    )

    teams = relationship(
        'Team',
        secondary='resourceteam',
        back_populates='resources',
        protected=True
    )

