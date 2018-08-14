from sqlalchemy import Integer, String, Unicode, BigInteger
from restfulpy.orm import DeclarativeBase, Field, TimestampMixin, relationship

from .subscribable import Subscription


class Member(TimestampMixin, DeclarativeBase):
    __tablename__ = 'member'

    role = Field(String(50))
    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': __tablename__
    }

    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=50)
    email = Field(
        Unicode(100),
        unique=True,
        index=True,
        nullable=True,
        pattern=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    )
    phone = Field(BigInteger, unique=True)

    subscribables = relationship(
        'Subscribable',
        secondary='subscription',
        back_populates='members',
    )

