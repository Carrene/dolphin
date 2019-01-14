from restfulpy.orm import DeclarativeBase, Field
from sqlalchemy import Integer, ForeignKey


class Skill(DeclarativeBase):
    __tablename__ = 'skill'

    phase_id = Field(
        Integer,
        ForeignKey('phase.id'),
        primary_key=True,
        label='Phase ID',
        required=True,
        nullable=False,
        not_none=True,
    )
    resource_id = Field(
        Integer,
        ForeignKey('member.id'),
        primary_key=True,
        label='Resource ID',
        required=True,
        nullable=False,
        not_none=True,
    )
