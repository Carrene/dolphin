from datetime import datetime

from restfulpy.orm import DeclarativeBase, Field, TimestampMixin, relationship
from sqlalchemy import Integer, String, ForeignKey, DateTime, BOOLEAN


class Subscription(TimestampMixin, DeclarativeBase):
    __tablename__ = 'subscription'

    id = Field(Integer, primary_key=True)

    subscribable_id = Field(Integer, ForeignKey('subscribable.id'))
    member_id = Field(Integer, ForeignKey('member.id'))

    seen_at = Field(
        DateTime,
        label='Seen At',
        nullable=True,
    )

    on_shot = Field(BOOLEAN, nullable=True)


class Subscribable(TimestampMixin, DeclarativeBase):
    __tablename__ = 'subscribable'

    type_ = Field(String(50), readonly=True)
    __mapper_args__ = {
        'polymorphic_on': type_,
        'polymorphic_identity': __tablename__
    }

    id = Field(Integer, primary_key=True, readonly=True)
    title = Field(
        String,
        max_length=128,
        min_length=1,
        label='Name',
        watermark='Enter the name',
        pattern=r'^[^\s].+[^\s]$',
        pattern_description='Spaces at the first and end of title is not valid',
        example='Sample Title',
        nullable=False,
        not_none=False,
        required=True,
        python_type=str
    )
    description = Field(
        String,
        min_length=1,
        max_length=8192,
        label='Description',
        watermark='Enter the description',
        not_none=False,
        nullable=True,
        required=False,
        python_type=str,
        example='Lorem Ipsum'
    )

    members = relationship(
        'Member',
        secondary='subscription',
        back_populates='subscribables',
        protected=True
    )

