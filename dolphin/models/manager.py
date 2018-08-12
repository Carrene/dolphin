from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field, relationship

from .stakeholder import Stakeholder


class Manager(Stakeholder):
    __mapper_args__ = {'polymorphic_identity': 'manager'}

    projects = relationship('Project', back_populates='manager', protected=True)

