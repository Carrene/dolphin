from restfulpy.orm import DeclarativeBase, Field, TimestampMixin, relationship
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, String, ForeignKey, DateTime, BOOLEAN


class Subscription(DeclarativeBase):
    __tablename__ = 'subscription'

    id = Field(Integer, primary_key=True)

    subscribable_id = Field(
        Integer,
        ForeignKey('subscribable.id'),
    )
    member_id = Field(Integer, ForeignKey('member.id'))

    seen_at = Field(
        DateTime,
        label='Seen At',
        nullable=True,
    )

    # The `one_shot` field fills with `True` value just if the member should be
    # notified about the subscribable whereas member hasn't subscribed the
    # subscribed yet.
    one_shot = Field(BOOLEAN, nullable=True)


class Subscribable(TimestampMixin, DeclarativeBase):
    __tablename__ = 'subscribable'

    type_ = Field(String(50), readonly=True)
    __mapper_args__ = {
        'polymorphic_on': type_,
        'polymorphic_identity': __tablename__
    }

    id = Field(
        Integer,
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
        example=1,
        protected=False,
    )
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

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='createdAt',
            key='created_at',
            label='Created',
            required=False,
            readonly=True
        )

    def get_room_title(self):
        raise NotImplementedError

