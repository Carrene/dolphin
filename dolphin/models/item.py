
from sqlalchemy import Integer, String, Time, ForeignKey, Table, Enum, Date
from sqlalchemy.dialects.postgresql import ENUM
from restfulpy.orm import DeclarativeBase, Field


class Item(DeclarativeBase):
    __tablename__ = 'item'

    id = Field(Integer, primary_key=True, autoincrement=True)
    description = Field(
        String,
        min_length=50,
        nullable=True,
        watermark='This is a description of summary'
    )
    kind= Field(
        ENUM('feature', 'enhancement', 'bug', name='kind'),
        nullable=False,
    )
    start = Field(Date, nullable=False, example='2080/08/16')
    end = Field(Date, nullable=False, example='2080/08/16')
    duration = Field(Time, nullable=False, example='10 hours')
    status = Field(
        ENUM('in-progress', 'on-hold', 'delayed', 'complete', name='status'),
        nullable=False,
        max_length=20,
        example='Complete'
    )
    assignee = Field(String, max_length=50, nullable=False)
    phase = Field(
        String,
        nullable=False,
        max_length=20
    )
    project_id = Field('Project', ForeignKey('project.id'))

