
from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from restfulpy.orm import DeclarativeBase, Field


class Stage(DeclarativeBase):
    __tablename__ = 'stage'

    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=50)
    order = Field(Integer, unique=True)

    tasks = relationship('Task', backref='stage')
    items = relationship('Item', backref='stage')

