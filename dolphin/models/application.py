import base64

from nanohttp import settings, context, HTTPStatus
from restfulpy.orm import DeclarativeBase, OrderingMixin, PaginationMixin, \
    FilteringMixin, Field, relationship
from sqlalchemy import Unicode, Integer, LargeBinary, ForeignKey, JSON
from sqlalchemy_media import Image, ImageAnalyzer, ImageValidator, \
    MagicAnalyzer, ContentTypeValidator
from sqlalchemy_media.constants import KB
from sqlalchemy_media.exceptions import DimensionValidationError, \
    AspectRatioValidationError, MaximumLengthIsReachedError, \
    ContentTypeValidationError


ICON_CONTENT_TYPES = ['image/jpeg', 'image/png']


class ApplicationMember(DeclarativeBase):
     __tablename__ = 'application_member'

     member_id = Field(Integer, ForeignKey('member.id'), primary_key=True)
     application_id = Field(
         Integer,
         ForeignKey('application.id'),
         primary_key=True
     )


class Icon(Image):

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
            content_types=ICON_CONTENT_TYPES,
        ),
    ]

    __prefix__ = 'icon'

    @property
    def __max_length__(self):
        if self._internal_max_length is None:
            self._internal_max_length = \
                settings.attachments.applications.icons.max_length * KB

        return self._internal_max_length

    @__max_length__.setter
    def __max_length__(self, v):
        self._internal_max_length = v

    @property
    def __min_length__(self):
        if self._internal_min_length is None:
            self._internal_min_length = \
                settings.attachments.applications.icons.min_length * KB

        return self._internal_min_length

    @__min_length__.setter
    def __min_length__(self, v):
        self._internal_min_length = v


class Application(DeclarativeBase, OrderingMixin, PaginationMixin,
                  FilteringMixin):
    __tablename__ = 'application'

    id = Field(Integer, primary_key=True)

    owner_id = Field(Integer, ForeignKey('member.id'))

    title = Field(
        Unicode(100),
        required=True,
        not_none=True,
        python_type=str,
        label='Title',
        min_length=1,
        max_length=100,
        watermark='Enter your title'
    )
    redirect_url = Field(
        Unicode(100),
        required=True,
        not_none=True,
        label='Redirect Uri',
        min_length=1,
        max_length=100,
        python_type=str,
        watermark='Enter your redirect url'
    )
    secret = Field(LargeBinary(32))
    _icon = Field(
        'icon',
        Icon.as_mutable(JSON),
        nullable=True,
        not_none=False,
        required=False,
        label='Icon',
        protected=False,
        json='icon',
    )

    owner = relationship(
        'Member',
        back_populates='applications',
        protected=True
    )

    members = relationship(
        'Member',
        secondary='application_member',
        lazy='selectin',
    )

    def to_dict(self):
        return dict(
            id=self.id,
            title=self.title,
            redirectUrl=self.safe_redirect_url,
            ownerId=self.safe_owner_id,
            secret=self.safe_secret,
            icon=self.icon,
        )

    def validate_secret(self, secret):
        try:
            return self.secret == base64.decodebytes(bytes(secret, 'utf-8'))
        except:
            return False

    def am_i_owner(self):
        return context.identity and self.owner_id == context.identity.id

    @property
    def safe_secret(self):
        return base64.encodebytes(self.secret) if self.am_i_owner() else None

    @property
    def safe_redirect_url(self):
        return self.redirect_url if self.am_i_owner() else None

    @property
    def safe_owner_id(self):
        return self.owner_id if self.am_i_owner() else None

    @property
    def icon(self):
        return self._icon.locate() if self._icon else None

    @icon.setter
    def icon(self, value):
        if value is not None:
            try:
                self._icon = Icon.create_from(value)

            except DimensionValidationError as e:
                raise HTTPStatus(f'618 {e}')

            except AspectRatioValidationError as e:
                raise HTTPStatus(
                    '619 Invalid aspect ratio Only 1/1 is accepted.'
                )

            except ContentTypeValidationError as e:
                raise HTTPStatus(
                    f'620 Invalid content type, Valid options are: '\
                    f'{", ".join(type for type in ICON_CONTENT_TYPES)}'
                )

            except MaximumLengthIsReachedError as e:
                max_length = settings.attachments.applications.icons.max_length
                raise HTTPStatus(
                    f'621 Cannot store files larger than: '\
                    f'{max_length * 1024} bytes'
                )

        else:
            self._icon = None

    def __repr__(self):
        return f'Application {self.id} {self.title}'

