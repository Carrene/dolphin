
from sqlalchemy import Integer, ForeignKey
from restfulpy.orm import Field

from .member import Member


class Guest(Member):
    __mapper_args__ = {'polymorphic_identity': 'guest'}

