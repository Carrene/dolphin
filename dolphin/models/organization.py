from nanohttp import settings, HTTPStatus, context
from restfulpy.orm import DeclarativeBase, Field, relationship, \
    ModifiedMixin, TimestampMixin, FilteringMixin, OrderingMixin, \
    PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Unicode, Integer, ForeignKey, Enum, JSON, func, and_, \
    select, bindparam
from sqlalchemy.orm import column_property
from sqlalchemy_media import Image, ImageAnalyzer, ImageValidator, \
    MagicAnalyzer, ContentTypeValidator
from sqlalchemy_media.constants import KB
from sqlalchemy_media.exceptions import DimensionValidationError, \
    AspectRatioValidationError, MaximumLengthIsReachedError, \
    ContentTypeValidationError


roles = [
    'owner',
    'member',
]


AVATAR_CONTENT_TYPES = [
    'image/jpeg',
    'image/png',
]


class OrganizationMember(DeclarativeBase):
    __tablename__ = 'organization_member'

    member_id = Field(
        Integer,
        ForeignKey('member.id'),
        primary_key=True
    )
    organization_id = Field(
        Integer,
        ForeignKey('organization.id'),
        primary_key=True
    )
    role = Field(
        Enum(*roles, name='roles'),
        python_type=str,
        label='role',
        watermark='Choose a roles',
        not_none=True,
        required=True,
    )


class Logo(Image):

    _internal_max_length = None
    _internal_min_length = None

    __pre_processors__ = [
        MagicAnalyzer(),
        ContentTypeValidator([
            'image/jpeg',
            'image/png',
        ]),
        ImageAnalyzer(),
        ImageValidator(
            minimum=(100, 100),
            maximum=(200, 200),
            min_aspect_ratio=1,
            max_aspect_ratio=1,
            content_types=['image/jpeg', 'image/png']
        ),
    ]

    __prefix__ = 'logo'

    @property
    def __max_length__(self):
        if self._internal_max_length is None:
            self._internal_max_length = \
                settings.attachments.organizations.logos.max_length * KB

        return self._internal_max_length

    @__max_length__.setter
    def __max_length__(self, v):
        self._internal_max_length = v

    @property
    def __min_length__(self):
        if self._internal_min_length is None:
            self._internal_min_length = \
                settings.attachments.organizations.logos.min_length * KB

        return self._internal_min_length

    @__min_length__.setter
    def __min_length__(self, v):
        self._internal_min_length = v


class Organization(OrderingMixin, FilteringMixin, PaginationMixin,
                   ModifiedMixin, TimestampMixin, DeclarativeBase):

    __tablename__ = 'organization'

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
    title = Field(
        Unicode(50),
        unique=True,
        index=True,
        min_length=1,
        max_length=50,
        pattern=r'^([0-9a-zA-Z]+-?[0-9a-zA-Z]*)*[\da-zA-Z]$',
        pattern_description='Lorem ipsum dolor sit amet',
        python_type=str,
        not_none=True,
        required=True,
        watermark='Enter your organization name',
        example='netalic',
        label='Name',
    )

    url = Field(
        Unicode(50),
        pattern=r'^(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/|www.)+'
            r'[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\.*)?$',
        pattern_description='Lorem ipsum dolor sit amet',
        min_length=1,
        max_length=50,
        python_type=str,
        required=False,
        nullable=True,
        not_none=False,
        watermark='Enter your URL',
        example='www.example.com',
        label='URL',
    )

    domain = Field(
        Unicode(50),
        pattern=r'^[^www.][a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]'
            r'{2,5}(:[0-9]{1,5})?$',
        pattern_description='Lorem ipsum dolor sit amet',
        min_length=1,
        max_length=50,
        python_type=str,
        required=False,
        nullable=True,
        not_none=False,
        watermark='Enter your domain',
        example='example.com',
        label='Domain',
    )

    _logo = Field(
        'logo',
        Logo.as_mutable(JSON),
        nullable=True,
        not_none=False,
        readonly=True,
        required=False,
        label='Logo',
        protected=False,
        json='logo',
    )

    members = relationship(
        'Member',
        secondary='organization_member',
        lazy='selectin',
        back_populates='organizations',
        protected=True,
    )

    invitations = relationship(
        'Invitation',
        back_populates='organization',
        protected=True
    )

    tags = relationship(
        'Tag',
        back_populates='organization',
        protected=True
    )

    members_count = column_property(
        select([func.count(OrganizationMember.member_id)])
        .select_from(OrganizationMember)
        .where(OrganizationMember.organization_id == id)
        .correlate_except(OrganizationMember)
    )

    @classmethod
    def __declare_last__(cls):
        from .member import Member

        cls.role = column_property(
            select([OrganizationMember.role])
            .select_from(OrganizationMember.__table__.join(
                Member,
                Member.id == OrganizationMember.member_id
            ))
            .where(and_(
                Member.email == bindparam(
                    'member_email',
                    callable_=lambda: context.identity.email \
                        if context.identity else None,
                ),
                OrganizationMember.organization_id == cls.id
            ))
            .correlate_except(OrganizationMember)
        )

    @property
    def logo(self):
        return self._logo.locate() if self._logo else None

    @logo.setter
    def logo(self, value):
        if value is not None:
            try:
                self._logo = Logo.create_from(value)

            except DimensionValidationError as e:
                raise HTTPStatus(f'625 {e}')

            except AspectRatioValidationError as e:
                raise HTTPStatus(
                    '622 Invalid aspect ratio Only 1/1 is accepted.'
                 )

            except ContentTypeValidationError as e:
                raise HTTPStatus(
                    f'623 Invalid content type, Valid options are: '\
                    f'{", ".join(type for type in AVATAR_CONTENT_TYPES)}'
                )

            except MaximumLengthIsReachedError as e:
                max_length = settings.attachments.organizations.logos.max_length
                raise HTTPStatus(
                    f'624 Cannot store files larger than: '\
                    f'{max_length * 1024} bytes'
                )

        else:
            self._logo = None

    def to_dict(self):
        organization = super().to_dict()
        organization['logo'] = self.logo
        return organization

    def __repr__(self):# pragma: no cover
        return f'\tTitle: {self.title}\n'

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='membersCount',
            key='members_count',
            label='Members count',
            required=False,
            readonly=True,
            protected=False,
            type_=int,
            watermark='lorem ipsum',
            example='10'
        )

        yield MetadataField(
            name='role',
            key='role',
            label='Role',
            required=False,
            readonly=True,
            protected=False,
            type_=str,
            watermark='lorem ipsum',
            example='owner'
        )

