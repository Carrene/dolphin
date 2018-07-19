
from sqlalchemy import Integer, String, Table, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from restfulpy.orm import DeclarativeBase, Field, relationship


class Release(DeclarativeBase):
    __tablename__ = 'release'

    id = Field(Integer, primary_key=True, autoincrement=True)
    title = Field(String, max_length=20, nullable=False)
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
    projects = relationship('Project', backref='release', lazy='selectin')

