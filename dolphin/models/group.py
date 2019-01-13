from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, String, BOOLEAN


class Group(DeclarativeBase):
    __tablename__ = 'group'

    id = Field(Integer, primary_key=True)

    title = Field(
        String,
        max_length=50,
        label='Title',
        not_none=False,
        required=True
    )
    public = Field(
        BOOLEAN,
        unique=True,
        nullable=True,
        required=False,
        not_none=False,
        label='Public'
    )

    projects = relationship('Project', back_populates='group', protected=True)

    def __repr__(self):
        return f'\tTitle: {self.title}, Public: {self.public}'
