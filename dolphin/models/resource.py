from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import column_property

from .member import Member


class TeamResource(DeclarativeBase):
    __tablename__ = 'resourceteam'

    team = Field(Integer, ForeignKey('team.id'), primary_key=True)
    resource = Field(Integer, ForeignKey('member.id'), primary_key=True)


class Resource(Member):
    __mapper_args__ = {'polymorphic_identity': 'resource'}

    skill_id = Field(
        Integer,
        ForeignKey('skill.id'),
        label='Skill ID',
        required=True,
        nullable=True,
        not_none=False,
    )

    teams = relationship(
        'Team',
        secondary='resourceteam',
        back_populates='resources',
        protected=True
    )
    skill = relationship(
        'Skill',
        back_populates='resources',
        protected=True
    )

