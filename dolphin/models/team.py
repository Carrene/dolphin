from restfulpy.orm import Field, DeclarativeBase, relationship
from sqlalchemy import Integer, String


class Team(DeclarativeBase):
    __tablename__ = 'team'

    id = Field(
        Integer,
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
        example=1,
        protected=False,
    )
    title = Field(String, max_length=40, unique=True)
    resources = relationship(
        'Resource',
        secondary='resourceteam',
        back_populates='teams',
        protected=True
    )

