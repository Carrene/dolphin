from restfulpy.orm import Field, DeclarativeBase, OrderingMixin, \
    FilteringMixin, PaginationMixin
from sqlalchemy import Integer, String, Unicode


class EventType(OrderingMixin, FilteringMixin, PaginationMixin,
                DeclarativeBase):
    __tablename__ = 'event_type'

    id = Field(
        Integer,
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
        example=1,
    )
    title = Field(
        Unicode,
        max_length=50,
        min_length=1,
        label='lorem ipsum',
        watermark='lorem ipsum',
        example='lorem ipsum',
        nullable=False,
        not_none=True,
        required=True,
        python_type=str
    )
    description = Field(
        Unicode,
        min_length=1,
        max_length=512,
        label='Description',
        watermark='Lorem Ipsum',
        not_none=False,
        nullable=True,
        required=False,
        python_type=str,
        example='Lorem Ipsum'
    )

