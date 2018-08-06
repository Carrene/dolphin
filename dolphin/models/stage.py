
from sqlalchemy import Integer, String, ForeignKey
from restfulpy.orm import DeclarativeBase, Field, relationship


class Stage(DeclarativeBase):
    __tablename__ = 'stage'

    project_id = Field(Integer, ForeignKey('project.id'))
    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=50)
    order = Field(Integer, unique=True)

    project = relationship(
        'Project',
        back_populates='stages',
        foreign_keys=[project_id],
        protected=True
    )
    items = relationship('Item', back_populates='stage', protected=True)

