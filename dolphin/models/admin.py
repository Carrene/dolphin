from .member import Member


class Admin(Member):
    __mapper_args__ = {'polymorphic_identity': 'admin'}

