
from sqlalchemy import Integer, String, ForeignKey, Table, Enum, Column,\
    DateTime
from sqlalchemy.ext.declarative import declared_attr
from restfulpy.orm import DeclarativeBase, Field, TimestampMixin, relationship


#association_table = Table('subscriptions', DeclarativeBase.metadata,
#    Column('subscribable_id', Integer, ForeignKey('subscribable.id')),
#    Column('member_id', Integer, ForeignKey('member.id'))
#)


class Association(DeclarativeBase):
    __tablename__ = 'association'

    subscribable = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    member = Field(Integer, ForeignKey('member.id'), primary_key=True)


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
    due_date = Field(DateTime)

    members = relationship(
        'Member',
        secondary='association',
        back_populates='subscriptions',
    )

