from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, ForeignKey, select, func, join, case, and_
from sqlalchemy.orm import column_property
from sqlalchemy.ext.hybrid import hybrid_property

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

    load_value = column_property(
        select([func.sum(Issue.priority_value)]) \
        .select_from(
            join(Item, Issue, Item.issue_id == Issue.id),
        ) \
        .where(Item.member_id == Member.id)
    )

    @hybrid_property
    def load(self):
        if self.load_value is None:
            return None

        if 5 < self.load_value:
            return 'heavy'

        elif 3 <= self.load_value <= 5:
            return 'medium'

        elif 3 > self.load_value:
            return 'light'

    @load.expression
    def load(cls):
        return case([
            (None == cls.load_value, None),
            (5 < cls.load_value, 'heavy'),
            (and_(3 <= cls.load_value,  cls.load_value <= 5), 'medium'),#<= 5
            (3 > cls.load_value, 'low')
        ])

