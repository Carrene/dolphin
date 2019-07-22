from restfulpy.orm import DeclarativeBase, Field, relationship, \
    OrderingMixin, FilteringMixin, PaginationMixin
from sqlalchemy import Integer, ForeignKey, String


class SpecialtyMember(DeclarativeBase):
    __tablename__ = 'specialty_member'

    specialty_id = Field(
        Integer,
        ForeignKey('specialty.id'),
        primary_key=True
    )
    member_id = Field(
        Integer,
        ForeignKey('member.id'),
        primary_key=True
    )


class Specialty(OrderingMixin, FilteringMixin, PaginationMixin, DeclarativeBase):
    __tablename__ = 'specialty'

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
    skill_id = Field(
        Integer,
        ForeignKey('skill.id'),
        label='Associated Skill',
        required=True,
        nullable=False,
        not_none=True,
    )

    phases = relationship(
        'Phase',
        back_populates='specialty',
        protected=True
    )
    resources = relationship(
        'Resource',
        back_populates='specialty',
        protected=True
    )
    members = relationship(
        'Member',
        secondary='specialty_member',
        back_populates='specialties',
        protected=True,
    )
    skill = relationship(
        'Skill',
        back_populates='specialty',
        protected=True
    )

