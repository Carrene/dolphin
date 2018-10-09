from restfulpy.orm import DeclarativeBase, Field, TimestampMixin, relationship
from sqlalchemy import Integer, String, ForeignKey


class Subscription(DeclarativeBase):
    __tablename__ = 'subscription'

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

    members = relationship(
        'Member',
        secondary='subscription',
        back_populates='subscribables',
        protected=True
    )

