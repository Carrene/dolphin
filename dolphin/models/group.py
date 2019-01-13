from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, String, BOOLEAN


class Group(DeclarativeBase):
    __tablename__ = 'group'

    id = Field(Integer, primary_key=True)

    title = Field(String, max_length=50)
    public = Field(BOOLEAN, unique=True, nullable=True)

    projects = relationship('Project', back_populates='group', protected=True)

    def __repr__(self):
        return f'\tTitle: {self.title}, Public: {self.public}'
