import os
from hashlib import sha256

from nanohttp import context
from sqlalchemy import Integer, String, Unicode, BigInteger
from sqlalchemy.orm import synonym
from restfulpy.principal import JwtPrincipal, JwtRefreshToken
from restfulpy.orm import DeclarativeBase, Field, TimestampMixin, \
    relationship, DBSession

from .subscribable import Subscription


class Member(TimestampMixin, DeclarativeBase):
    __tablename__ = 'member'

    role = Field(String(50))
    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': __tablename__
    }

    id = Field(Integer, primary_key=True)
    title = Field(String, max_length=50)
    email = Field(
        Unicode(100),
        unique=True,
        index=True,
        pattern=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
    )
    _password = Field('password', Unicode(128), min_length=6, protected=True)
    phone = Field(BigInteger, unique=True)

    subscribables = relationship(
        'Subscribable',
        secondary='subscription',
        back_populates='members',
    )

    @property
    def roles(self):
        return []

    @classmethod
    def _hash_password(cls, password):
        salt = sha256()
        salt.update(os.urandom(60))
        salt = salt.hexdigest()

        hashed_pass = sha256()
        # Make sure password is a str because we cannot hash unicode objects
        hashed_pass.update((password + salt).encode('utf-8'))
        hashed_pass = hashed_pass.hexdigest()

        password = salt + hashed_pass
        return password

    def _set_password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""
        min_length = self.__class__.password.info['min_length']
        if len(password) < min_length:
            raise HTTPStatus(
                f'704 Please enter at least {min_length} characters '
                'for password.'
            )
        self._password = self._hash_password(password)

    def _get_password(self):
        """Return the hashed version of the password."""
        return self._password

    password = synonym(
        '_password',
        descriptor=property(_get_password, _set_password),
        info=dict(protected=True)
    )

    def validate_password(self, password):
        hashed_pass = sha256()
        hashed_pass.update((password + self.password[:64]).encode('utf-8'))
        return self.password[64:] == hashed_pass.hexdigest()

    def create_jwt_principal(self):
        return JwtPrincipal(dict(
            id=self.id,
            roles=self.roles,
            email=self.email,
            name=self.title
        ))

    def create_refresh_principal(self):
        return JwtRefreshToken(dict(
            id=self.id
        ))

    @classmethod
    def current(cls):
        return DBSession.query(cls) \
            .filter(cls.email == context.identity.email) \
            .one()

