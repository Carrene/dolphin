from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship
from restfulpy.orm import Field, DeclarativeBase


class Team(DeclarativeBase):
    __tablename__ = 'team'

    id = Field(Integer, primary_key=True)
    name = Field(String, max_length=40, unique=True)
    resources = relationship('Resource', backref='team')

