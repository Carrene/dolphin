from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field, relationship

from .stakeholder import Stakeholder


class Admin(Stakeholder):
    __tablename__ = 'admin'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('stakeholder.id'), primary_key=True)

    projects = relationship('Project', back_populates='admin', protected=True)
    releases = relationship('Release', back_populates='admin', protected=True)

