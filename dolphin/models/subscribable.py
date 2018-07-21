
from sqlalchemy import Integer, String, Time, ForeignKey, Table, Enum, Date,\
	Column
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from restfulpy.orm import DeclarativeBase, Field, TimestampMixin


association_table = Table('subscription', DeclarativeBase.metadata,
    Column('subscribable_id', Integer, ForeignKey('subscribable.id')),
    Column('stakeholder_id', Integer, ForeignKey('stakeholder.id'))
)


class Subscribable(TimestampMixin, DeclarativeBase):
    __tablename__ = 'subscribable'

    type_ = Field(String(50))
    __mapper_args__ = {
        'polymorphic_on': type_,
        'polymorphic_identity': __tablename__
    }

    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=50)
    description = Field(
        String,
        min_length=20,
        nullable=True,
        watermark='This is a description of summary'
    )
    entry_time = Field(Date, example='2080/08/16')

    stakeholders = relationship(
        'stakeholder',
        secondary=association_table,
        backref='subscriptions'
    )

