from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field, relationship

from .stakeholder import Stakeholder


class Manager(Stakeholder):
    __tablename__ = 'manager'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('stakeholder.id'), primary_key=True)

    projects = relationship('Project', back_populates='manager', protected=True)
    releases = relationship('Release', back_populates='manager', protected=True)

