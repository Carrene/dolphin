from restfulpy.orm import Field, relationship
from sqlalchemy import Integer, String
from restfulpy.orm import DeclarativeBase


class Skill(DeclarativeBase):
    __tablename__ = 'skill'

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
        String(50),
        max_length=50,
        min_length=1,
        label='Name',
        watermark='Enter the name',
        example='Sample Title',
        nullable=False,
        not_none=True,
        required=True,
        python_type=str
    )
    description = Field(
        String(512),
        max_length=512,
        label='Description',
        watermark='Lorem Ipusm',
        not_none=False,
        nullable=True,
        required=False,
        python_type=str,
        example='Lorem Ipsum'
    )
    specialties = relationship(
        'Specialty',
        back_populates='skill',
        protected=True
    )

