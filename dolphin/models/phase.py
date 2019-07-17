from restfulpy.orm import DeclarativeBase, Field, relationship, \
    FilteringMixin, OrderingMixin, PaginationMixin
from sqlalchemy import Integer, String, ForeignKey

from .specialty import Specialty


class Phase(OrderingMixin, FilteringMixin, PaginationMixin, DeclarativeBase):
    __tablename__ = 'phase'

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
    specialty_id = Field(
        Integer,
        ForeignKey('specialty.id'),
        label='Associated Specialtys',
        required=True,
        nullable=False,
        not_none=True,
    )
    workflow_id = Field(
        Integer,
        ForeignKey('workflow.id'),
        python_type=int,
        nullable=False,
        watermark='Choose a workflow',
        label='Workflow',
        not_none=True,
        required=False,
        example='Lorem Ipsum'
    )

    title = Field(
        String,
        max_length=50,
        min_length=1,
        label='Name',
        watermark='Enter the name',
        pattern=r'^[^\s].+[^\s]$',
        pattern_description='Spaces at the first and end of title is not valid',
        example='Sample Title',
        nullable=False,
        not_none=True,
        required=True,
        python_type=str
    )
    order = Field(
        Integer,
        minimum=-1,
        label='order',
        watermark='Enter the order',
        example=1,
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

    workflow = relationship(
        'Workflow',
        back_populates='phases',
        protected=True
    )
    issue_phases = relationship(
        'IssuePhase',
        lazy='selectin',
        back_populates='phase',
        protected=True
    )
    specialty = relationship(
        'Specialty',
        back_populates='phases',
        protected=True
    )

    def __repr__(self):
        return f'\tTitle: {self.title}\n'

