from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, String, ForeignKey


class Phase(DeclarativeBase):
    __tablename__ = 'phase'

    project_id = Field(Integer, ForeignKey('project.id'))
    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=50)
    order = Field(Integer, unique=True)

    project = relationship(
        'Project',
        back_populates='phases',
        foreign_keys=[project_id],
        protected=True
    )
    items = relationship('Item', back_populates='phase', protected=True)

