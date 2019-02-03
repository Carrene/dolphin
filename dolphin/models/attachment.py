from nanohttp import settings, HTTPStatus, context
from sqlalchemy import Integer, JSON, ForeignKey, String, Boolean
from restfulpy.orm.metadata import FieldInfo
from restfulpy.orm import Field, DeclarativeBase, FilteringMixin, \
    SoftDeleteMixin, OrderingMixin, PaginationMixin, TimestampMixin
from sqlalchemy_media import File, MagicAnalyzer, ContentTypeValidator
from sqlalchemy_media.constants import KB
from sqlalchemy_media.exceptions import ContentTypeValidationError, \
    MaximumLengthIsReachedError

from .member import Member


is_mine_fieldinfo = FieldInfo(Boolean, not_none=True, readonly=True)


class FileAttachment(File):

    _internal_max_length = None
    _internal_min_length = None

    __pre_processors__ = [
        MagicAnalyzer(),
        ContentTypeValidator([
            'image/jpeg',
            'image/png',
            'text/plain',
            'image/jpg'
        ])
    ]

    @property
    def __max_length__(self):
        if self._internal_max_length is None:
            self._internal_max_length = \
                settings.attachments.files.max_length * KB

        return self._internal_max_length

    @__max_length__.setter
    def __max_length__(self, v):
        self._internal_max_length = v

    @property
    def __min_length__(self):
        if self._internal_min_length is None:
            self._internal_min_length = \
                settings.attachments.files.min_length * KB

        return self._internal_min_length

    @__min_length__.setter
    def __min_length__(self, v):
        self._internal_min_length = v


class Attachment(SoftDeleteMixin, FilteringMixin, OrderingMixin,
                 PaginationMixin, TimestampMixin, DeclarativeBase):
    __tablename__ = 'attachment'

    project_id = Field(
        Integer,
        ForeignKey('project.id'),
        python_type=int,
        watermark='Choose a project',
        label='Project',
        nullable=True,
        not_none=False,
        required=True,
        example='Lorem Ipsum'
    )
    release_id = Field(
        Integer,
        ForeignKey('release.id'),
        python_type=int,
        watermark='Choose a release',
        label='Project',
        nullable=True,
        not_none=False,
        required=True,
        example='Lorem Ipsum'
    )

    id = Field(Integer, primary_key=True)
    title = Field(
        String(100),
        python_type=str,
        max_length=100,
        min_length=1,
        label='Title',
        watermark='Enter the title',
        example='Sample Title',
        nullable=True,
        not_none=False,
        required=True
    )
    caption = Field(
        String(500),
        min_length=1,
        max_length=500,
        label='Caption',
        watermark='Enter the caption',
        not_none=False,
        nullable=True,
        required=False,
        python_type=str,
        example='Lorem Ipsum'
    )
    _file = Field(
        FileAttachment.as_mutable(JSON),
        nullable=True,
        protected=False,
        json='file'
    )
    sender_id = Field(Integer, ForeignKey('member.id'))

    @property
    def is_mine(self):
        return self.sender_id == Member.current().id

    @property
    def file(self):
        return self._file if self._file else None

    @file.setter
    def file(self, value):
        if value is not None:
            try:
                self._file = FileAttachment.create_from(value)

            except ContentTypeValidationError:
                raise HTTPStatus(
                    '710 The Mimetype Does Not Match The File Type'
                )

            except MaximumLengthIsReachedError:
                raise HTTPStatus('413 Request Entity Too Large')

        else:
            self._file = None

    def to_dict(self):
        attachment_dictionary = super().to_dict()
        attachment_dictionary.update(
            isMine=self.is_mine,
            file=dict(
                title=self.title,
                url=self.file.locate() \
                if self.file and not self.is_deleted else None,
                mymetype=self.file.content_type
            )
        )
        return attachment_dictionary

    @classmethod
    def json_metadata(cls):
        metadata = super().json_metadata()
        metadata['fields']['isMine'] = is_mine_fieldinfo.to_json()
        return metadata

