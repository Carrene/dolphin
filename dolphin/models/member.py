import os
import uuid
from hashlib import sha256

from cas import CASPrincipal
from nanohttp import context
from restfulpy.orm import DeclarativeBase, Field, relationship, DBSession, \
    SoftDeleteMixin, ModifiedMixin, FilteringMixin, PaginationMixin, \
    OrderingMixin
from restfulpy.principal import JwtRefreshToken
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, String, Unicode, BigInteger, select,  \
    bindparam, JSON
from sqlalchemy.orm import column_property, synonym
from sqlalchemy_media import Image, ImageAnalyzer, ImageValidator, \
    MagicAnalyzer, ContentTypeValidator

from .organization import OrganizationMember


AVATAR_CONTENT_TYPES = ['image/jpeg', 'image/png']


class Avatar(Image):

    _internal_max_length = None
    _internal_min_length = None

    __pre_processors__ = [
        MagicAnalyzer(),
        ContentTypeValidator([ 'image/jpeg', 'image/png', ]),
        ImageAnalyzer(),
        ImageValidator(
            minimum=(200, 200),
            maximum=(300, 300),
            min_aspect_ratio=1,
            max_aspect_ratio=1,
            content_types=AVATAR_CONTENT_TYPES
        ),
    ]

    __prefix__ = 'avatar'

    @property
    def __max_length__(self):
        if self._internal_max_length is None:
            self._internal_max_length = \
                settings.attachments.members.avatars.max_length * KB

        return self._internal_max_length

    @__max_length__.setter
    def __max_length__(self, v):
        self._internal_max_length = v

    @property
    def __min_length__(self):
        if self._internal_min_length is None:
            self._internal_min_length = \
                settings.attachments.members.avatars.min_length * KB

        return self._internal_min_length

    @__min_length__.setter
    def __min_length__(self, v):
        self._internal_min_length = v


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
    _avatar = Field(
        'avatar',
        Avatar.as_mutable(JSON),
        nullable=True,
        protected=False,
        json='avatar',
        not_none=False,
        label='Avatar',
        required=False,
    )
    _password = Field(
        'password',
        Unicode(128),
        index=True,
        protected=True,
        json='password',
        pattern=r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).+$',
        pattern_description='Password must include at least one uppercase, one'
            'lowercase and one number',
        example='ABCabc123',
        watermark=None,
        label='Password',
        message=None,
        min_length=6,
        max_length=20,
        required=True,
        python_type=str,
        not_none=True,
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
        protected=False,
    )
    skills = relationship(
        'Skill',
        secondary='skill_member',
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
    def avatar(self):
        return self._avatar.locate() if self._avatar else None

    @avatar.setter
    def avatar(self, value):
        if value is not None:
            try:
                self._avatar = Avatar.create_from(value)

            except DimensionValidationError as e:
                raise HTTPStatus(f'618 {e}')

            except AspectRatioValidationError as e:
                raise HTTPStatus(
                    '619 Invalid aspect ratio Only 1/1 is accepted.'
                )

            except ContentTypeValidationError as e:
                raise HTTPStatus(
                    f'620 Invalid content type, Valid options are: '\
                    f'{", ".join(type for type in AVATAR_CONTENT_TYPES)}'
                )

            except MaximumLengthIsReachedError as e:
                max_length = settings.attachments.members.avatars.max_length
                raise HTTPStatus(
                    f'621 Cannot store files larger than: '\
                    f'{max_length * 1024} bytes'
                )

        else:
            self._avatar = None

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

    @classmethod
    def current(cls):
        return DBSession.query(cls) \
            .filter(cls.email == context.identity.email) \
            .one()

    def to_dict(self):
        if not isinstance(context.identity, AccessToken):
            result = super().to_dict()
            result['avatar'] = self.avatar
            return result

        member = dict.fromkeys(SCOPES.keys(), None)
        member['id'] = self.id
        if context.identity.scopes is None:
            return member

        for scope in context.identity.scopes:
            member[scope] = SCOPES[scope](self)

        return member

    @classmethod
    def _create_activation_session(cls, phone):
        ocra_suite = OCRASuite(
            'time',
            settings.phone.activation_code.length,
            settings.phone.activation_code.hash_algorithm,
            settings.phone.activation_code.time_interval,
            settings.phone.activation_code.challenge_limit
        )
        seed = settings.phone.activation_code.seed
        return TimeBasedChallengeResponse(
            ocra_suite,
            derivate_seed(seed, str(phone))
        )

    @classmethod
    def generate_activation_code(cls, phone, id):
        session = cls._create_activation_session(phone)
        return session.generate(challenge=id)

    @classmethod
    def verify_activation_code(cls, phone, id, code):
        session = cls._create_activation_session(phone)
        result, ___ = session.verify(
            code,
            str(id),
            settings.phone.activation_code.window
        )
        return result

    @classmethod
    def create_otp(cls, phone, id):
        return OTPSMS(
            receiver=phone,
            code=cls.generate_activation_code(phone, str(id))
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
            readonly=True,
            example='lorem ipsum',
            message='lorem ipsum',
            watermark='lorem ipsum',
        )
        yield MetadataField(
            name='skills',
            key='skills',
            label='Skills',
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

