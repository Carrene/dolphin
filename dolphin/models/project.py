
from sqlalchemy import Integer, String, Time, ForeignKey, Table, Enum, Date
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import relationship
from restfulpy.orm import DeclarativeBase, Field


class Project(DeclarativeBase):
    __tablename__ = 'project'

    id = Field(Integer, primary_key=True, autoincrement=True)
    description = Field(
        String,
        min_length=50,
        nullable=True,
        watermark='This is a description of summary'
    )
    status = Field(
        ENUM('in-progress', 'on-hold', 'delayed', 'complete', name='status'),
        nullable=False,
        max_length=20,
        example='Complete'
    )
    estimated_due_date = Field(Time, nullable=False, example='2080/08/16')
    manager = Field(String,nullable=False,max_length=50)

    workflow = Field(
        String,
        nullable=False
    )
    release_id = Field(Integer, ForeignKey('release.id'))
    # Loading strategy in relationship between 'Item' and 'Project' is
    # selectIn because number of records of project table is not much
    items = relationship('Item', backref='project', lazy='selectin')

