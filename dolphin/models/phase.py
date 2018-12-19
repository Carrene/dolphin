from restfulpy.orm import DeclarativeBase, Field, relationship, \
    FilteringMixin, OrderingMixin, PaginationMixin
from sqlalchemy import Integer, String, ForeignKey


class Phase(OrderingMixin, FilteringMixin, PaginationMixin, DeclarativeBase):
    __tablename__ = 'phase'

    workflow_id = Field(Integer, ForeignKey('workflow.id'))

    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=50)
    order = Field(Integer, unique=True)

    workflow = relationship(
        'Workflow',
        back_populates='phases',
        protected=True
    )

    issues = relationship(
        'Issue',
        secondary='item',
        lazy='selectin',
        protected=False
    )

