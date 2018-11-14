from cas import CASPrincipal
from nanohttp import context
from restfulpy.orm import DeclarativeBase, Field, relationship, DBSession, \
    SoftDeleteMixin, ModifiedMixin, FilteringMixin, PaginationMixin, \
    OrderingMixin
from restfulpy.principal import JwtRefreshToken
from sqlalchemy import Integer, String, Unicode, BigInteger


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
    title = Field(
        String,
        max_length=50,
        min_length=1,
        label='Title',
        watermark='Enter the title',
        nullable=False,
        not_none=False,
        required=True,
        python_type=str,
        example='Lorem Ipsum',
        message='Lorem Ipsum'
    )
    email = Field(
        Unicode(100),
        label='Email',
        watermark='Enter you email',
        unique=True,
        not_none=False,
        required=True,
        index=True,
        pattern=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)',
        example='member@example.com',
        message='Lorem Ipsum'
    )
    access_token = Field(Unicode(512), protected=True)
    phone = Field(
        BigInteger,
        label='Phone',
        watermark='Enter your phone number',
        nullable=True,
        required=False,
        unique=True,
        example='Lorem Ipsum',
        message='Lorem Ipsum'
    )
    avatar = Field(
        Unicode(200),
        label='Avatar',
        nullable=True,
        unique=False,
        not_none=False,
        required=False,
        example='Lorem Ipsum',
        message='Lorem Ipsum'
    )

    subscribables = relationship(
        'Subscribable',
        secondary='subscription',
        back_populates='members',
    )

    containers = relationship('Container', back_populates='member', protected=True)

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

