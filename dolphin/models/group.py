
from sqlalchemy import Integer, String, ForeignKey, Table, Enum, Column, \
    DateTime
from sqlalchemy.ext.declarative import declared_attr
from restfulpy.orm import DeclarativeBase, Field, TimestampMixin, relationship


class Group(DeclarativeBase):
    __tablename__ = 'group'

    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=50)

    projects = relationship(
        'Project',
        back_populates='group',
        protected=True
    )

