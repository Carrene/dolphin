from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field, relationship

from .stakeholder import Stakeholder


class Administrator(Stakeholder):
    __tablename__ = 'administrator'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('stakeholder.id'), primary_key=True)

    projects = relationship('Project', back_populates='administrator', protected=True)
    releases = relationship('Release', back_populates='administrator', protected=True)

