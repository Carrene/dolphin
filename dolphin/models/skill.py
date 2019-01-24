from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, ForeignKey, String


class Skill(DeclarativeBase):
    __tablename__ = 'skill'

    id = Field(Integer, primary_key=True, readonly=True)

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

    phases = relationship(
        'Phase',
        back_populates='skill',
        protected=True
    )
    resources = relationship(
        'Resource',
        back_populates='skill',
        protected=True
    )

