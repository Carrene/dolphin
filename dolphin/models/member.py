import uuid

from cas import CASPrincipal
from nanohttp import context
from restfulpy.orm import DeclarativeBase, Field, relationship, DBSession, \
    SoftDeleteMixin, ModifiedMixin, FilteringMixin, PaginationMixin, \
    OrderingMixin
from restfulpy.orm.metadata import MetadataField
from restfulpy.principal import JWTRefreshToken
from sqlalchemy import Integer, String, Unicode, BigInteger, select, bindparam
from sqlalchemy.orm import column_property

from .organization import OrganizationMember


class Member(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
             SoftDeleteMixin, DeclarativeBase):

    __tablename__ = 'member'

    role = Field(String(50))
    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': __tablename__
    }

    reference_id = Field(Integer, unique=True)
    id = Field(
        Integer,
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
        example=1,
        protected=False,
    )
    first_name = Field(
        Unicode(20),
        nullable=True,
        not_none=False,
        python_type=str,
        min_length=3,
        max_length=20,
        required=False,
        pattern=r'^[a-zA-Z]{1}[a-z-A-Z ,.\'-]{2,19}$',
        pattern_description='Only alphabetical characters, ., \' and space are'
            'valid',
        example='John',
        label='First Name',
    )
    last_name = Field(
        Unicode(20),
        nullable=True,
        not_none=False,
        python_type=str,
        min_length=3,
        max_length=20,
        required=False,
        pattern=r'^[a-zA-Z]{1}[a-z-A-Z ,.\'-]{2,19}$',
        pattern_description='Only alphabetical characters, ., \' and space are'
            'valid',
        example='Doe',
        label='Last Name',
    )
    title = Field(
        String,
        max_length=50,
        min_length=1,
        label='User Name',
        nullable=False,
        not_none=False,
        required=True,
        python_type=str,
        example='Lorem Ipsum',
    )
    email = Field(
        Unicode(100),
        unique=True,
        not_none=False,
        required=True,
        index=True,
        python_type=str,
        pattern=r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)',
        pattern_description='Invalid email format, example: user@example.com',
        example='user@example.com',
        label='Email',
    )
    access_token = Field(Unicode(512), protected=True)
    phone = Field(
        BigInteger,
        label='Phone',
        nullable=True,
        required=False,
        unique=True,
        example='Lorem Ipsum'
    )
    avatar = Field(
        Unicode(200),
        label='Avatar',
        nullable=True,
        unique=False,
        not_none=False,
        required=False,
        example='Lorem Ipsum'
    )

    subscribables = relationship(
        'Subscribable',
        secondary='subscription',
        back_populates='members',
    )

    projects = relationship(
        'Project',
        primaryjoin='Project.manager_id == Member.id',
        back_populates='manager',
        protected=True
    )

    secondary_projects = relationship(
        'Project',
        primaryjoin='Project.secondary_manager_id == Member.id',
        back_populates='secondary_manager',
        protected=True
    )

    releases = relationship(
        'Release',
        back_populates='manager',
        protected=True
    )

    items = relationship(
        'Item',
        back_populates='member',
        protected=True
    )
    organizations = relationship(
        'Organization',
        back_populates='members',
        secondary='organization_member',
        protected=True,
    )
    invitations = relationship(
        'Invitation',
        back_populates='by_member',
        protected=True
    )
    attachments = relationship('Attachment', lazy='selectin')
    groups = relationship(
        'Group',
        secondary='group_member',
        lazy='selectin',
        back_populates='members',
        protected=False,
    )
    specialties = relationship(
        'Specialty',
        secondary='specialty_member',
        back_populates='members',
        protected=False,
    )

    organization_role = column_property(
        select([OrganizationMember.role]) \
        .select_from(OrganizationMember) \
        .where(OrganizationMember.organization_id == bindparam(
            'organization_id',
            callable_=lambda: context.identity.payload['organizationId']
        )) \
        .where(OrganizationMember.member_id == id) \
        .correlate_except(OrganizationMember),
        deferred=True
    )

    @property
    def roles(self):
        return [self.role]

    def create_jwt_principal(self, session_id=None):
        if session_id is None:
            session_id = str(uuid.uuid4())

        return CASPrincipal(dict(
            id=self.id,
            roles=self.roles,
            email=self.email,
            firstName=self.first_name,
            lastName=self.last_name,
            title=self.title,
            avatar=self.avatar,
            referenceId=self.reference_id,
            sessionId=session_id,
        ))

    def create_refresh_principal(self):
        return JWTRefreshToken(dict(
            id=self.id
        ))

    @classmethod
    def current(cls):
        return DBSession.query(cls) \
            .filter(cls.reference_id == context.identity.reference_id) \
            .one()

    def __repr__(self):
        return f'\tTitle: {self.title}, Email: {self.email}\n'

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='groups',
            key='groups',
            label='Groups',
            required=False,
            readonly=True,
            example='lorem ipsum',
            message='lorem ipsum',
            watermark='lorem ipsum',
        )
        yield MetadataField(
            name='specialties',
            key='specialties',
            label='Specialties',
            required=False,
            readonly=True,
            example='lorem ipsum',
            message='lorem ipsum',
            watermark='lorem ipsum',
        )
        yield MetadataField(
            name='organizationRole',
            key='organization_role',
            label='Organization Role',
            example='lorem ipsum',
            readonly=True,
            watermark='lorem ipsum',
            type_=str,
            required=True,
            not_none=True,
        )

