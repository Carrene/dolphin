from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, ForeignKey, select, func, join
from sqlalchemy.orm import column_property

from .member import Member
from .issue import Issue
from .item import Item


class TeamResource(DeclarativeBase):
    __tablename__ = 'resourceteam'

    team = Field(Integer, ForeignKey('team.id'), primary_key=True)
    resource = Field(Integer, ForeignKey('member.id'), primary_key=True)


class Resource(Member):
    __mapper_args__ = {'polymorphic_identity': 'resource'}

    skill_id = Field(
        Integer,
        ForeignKey('skill.id'),
        label='Skills',
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

    load = column_property(
        select([func.sum(Issue.priority_value)]) \
        .select_from(
            join(Item, Issue, Item.issue_id == Issue.id),
        ) \
        .where(Item.member_id == 1)
    )

