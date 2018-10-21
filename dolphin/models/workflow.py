from restfulpy.orm import DeclarativeBase, Field, relationship
from sqlalchemy import Integer, String


class Workflow(DeclarativeBase):
    __tablename__ = 'workflow'

    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=50)

    projects = relationship(
        'Project',
        back_populates='workflow',
        protected=True
    )

