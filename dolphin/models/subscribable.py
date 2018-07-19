
from sqlalchemy import Integer, String, Time, ForeignKey, Table, Enum, Date
from sqlalchemy.orm import relationship
from restfulpy.orm import DeclarativeBase, Field, TimestampMixin


class Subscribable(DeclarativeBase, TimestampMixin):
    __abstract__ = True
    __tablename__ = 'subscribable'

    type_ = Field(String(50))
    __mapper_args__ = {'polymorphic_on':type_}

    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=50)
    description = Field(
        String,
        min_length=20,
        nullable=True,
        watermark='This is a description of summary'
    )
    entry_time = Field(Date, example='2080/08/16')

