from sqlalchemy import Integer, String, Unicode, BigInteger
from restfulpy.orm import DeclarativeBase, Field, TimestampMixin


class Stakeholder(TimestampMixin, DeclarativeBase):
    __tablename__ = 'stakeholder'

    type_ = Field(String(50))
    __mapper_args__ = {
        'polymorphic_on': type_,
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

