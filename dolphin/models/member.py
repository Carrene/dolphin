import os
from hashlib import sha256

from nanohttp import context
from sqlalchemy import Integer, String, Unicode, BigInteger
from sqlalchemy.orm import synonym
from restfulpy.principal import JwtPrincipal, JwtRefreshToken
from restfulpy.orm import DeclarativeBase, Field, TimestampMixin, \
    relationship, DBSession, SoftDeleteMixin, ModifiedMixin, FilteringMixin, \
    PaginationMixin, OrderingMixin
from cas import CASPrincipal

from .subscribable import Subscription


class Member(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
             SoftDeleteMixin, DeclarativeBase):

    __tablename__ = 'member'

    role = Field(String(50))
    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': __tablename__
    }

    reference_id = Field(Integer, unique=True)
    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=50)
    email = Field(
        Unicode(100),
        unique=True,
        index=True,
        pattern=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    )
    access_token = Field(Unicode(200), protected=True)
    phone = Field(BigInteger, unique=True, nullable=True)

    subscribables = relationship(
        'Subscribable',
        secondary='subscription',
        back_populates='members',
    )

    @property
    def roles(self):
        return []

    def create_jwt_principal(self):
        return CASPrincipal(dict(
            id=self.id,
            roles=self.roles,
            email=self.email,
            name=self.title,
            referenceId=self.reference_id,
        ))

    def create_refresh_principal(self):
        return JwtRefreshToken(dict(
            id=self.id
        ))

    @classmethod
    def current(cls):
        return DBSession.query(cls) \
            .filter(cls.reference_id == context.identity.reference_id) \
            .one()

