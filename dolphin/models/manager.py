from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field, relationship

from .member import Member


class Manager(Member):
    __mapper_args__ = {'polymorphic_identity': 'manager'}

    projects = relationship('Project', back_populates='manager', protected=True)

