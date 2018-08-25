from sqlalchemy import Integer, String
from restfulpy.orm import Field, DeclarativeBase, relationship


class Team(DeclarativeBase):
    __tablename__ = 'team'

    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=40, unique=True)
    resources = relationship(
        'Resource',
        secondary='resourceteam',
        back_populates='teams',
        protected=True
    )

