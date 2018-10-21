from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, String, ForeignKey


class Phase(DeclarativeBase):
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
    items = relationship('Item', back_populates='phase', protected=True)

