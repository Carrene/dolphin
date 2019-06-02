
from restfulpy.orm import Field, DeclarativeBase, relationship
from sqlalchemy import Integer, Unicode


class Github(DeclarativeBase):
    __tablename__ = 'github'

    id = Field(
        Integer,
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
    )
   token = Field(
        Unicode,
        max_length=50,
        min_length=30,
        label='token',
        watermark='lorem ipsum',
        example='lorem ipsum',
        nullable=False,
        not_none=True,
        required=True,
        python_type=str,
        readonly=False,
        message='Lorem ipsum',
    )
    members = relationship(
        'Member',
        lazy='selectin',
        back_populates='github',
        protected=True,
    )

