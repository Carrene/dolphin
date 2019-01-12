from restfulpy.orm import DeclarativeBase, Field, relationship, \
    FilteringMixin, OrderingMixin, PaginationMixin
from sqlalchemy import Integer, String, ForeignKey


class Phase(OrderingMixin, FilteringMixin, PaginationMixin, DeclarativeBase):
    __tablename__ = 'phase'

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

    id = Field(Integer, primary_key=True)
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
        unique=True,
        minimum=-1,
        label='order',
        watermark='Enter the order',
        example=1,
        nullable=False,
        not_none=True,
        required=True,
        python_type=str
    )

    workflow = relationship(
        'Workflow',
        back_populates='phases',
        protected=True
    )
    issues = relationship(
        'Issue',
        secondary='item',
        lazy='selectin',
        protected=True
    )
    members = relationship(
        'Member',
        secondary='item',
        lazy='selectin',
        protected=True
    )

    resources = relationship(
        'Resource',
        back_populates='phase',
        protected=True
    )

