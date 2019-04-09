import uuid

from cas import CASPrincipal
from nanohttp import context
from restfulpy.orm import DeclarativeBase, Field, relationship, DBSession, \
    SoftDeleteMixin, ModifiedMixin, FilteringMixin, PaginationMixin, \
    OrderingMixin
from restfulpy.principal import JwtRefreshToken
from restfulpy.orm.metadata import MetadataField
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
    name = Field(
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
        example='John Doe',
        label='Full Name',
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

    phases = relationship(
        'Phase',
        back_populates='members',
        secondary='item',
        protected=True
    )
    issues = relationship(
        'Issue',
        back_populates='members',
        secondary='item',
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
        protected=True,
    )
    skills = relationship(
        'Skill',
        secondary='skill_member',
        back_populates='members',
        protected=True,
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
            name=self.name,
            title=self.title,
            avatar=self.avatar,
            referenceId=self.reference_id,
            sessionId=session_id,
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
            readonly=True
        )

