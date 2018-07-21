from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
from restfulpy.orm import Field

from .stakeholder import Stakeholder


class Admin(Stakeholder):
    __tablename__ = 'admin'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('stakeholder.id'), primary_key=True)

    projects = relationship('Project', backref='admin')
    releases = relationship('Release', backref='admin')

