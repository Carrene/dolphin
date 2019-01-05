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
    title = Field(
        String,
        max_length=50,
        min_length=1,
        label='Title',
        watermark='Enter the title',
        pattern=r'^[^\s].+[^\s]$',
        pattern_description='Spaces at the first and end of title is not valid',
        example='Sample Title',
        nullable=False,
        not_none=False,
        required=True,
        python_type=str,
        message='Lorem Ipsum',
    )
    description = Field(
        String,
        min_length=1,
        max_length=512,
        label='Description',
        watermark='Enter the description',
        not_none=False,
        nullable=True,
        required=False,
        python_type=str,
        message='Lorem Ipsum',
        example='Lorem Ipsum'
    )

    members = relationship(
        'Member',
        secondary='subscription',
        back_populates='subscribables',
        protected=True
    )

