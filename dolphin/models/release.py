from datetime import datetime

from restfulpy.orm import Field, relationship, ModifiedMixin, FilteringMixin, \
    OrderingMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, Enum, DateTime, ForeignKey, select, func
from sqlalchemy.orm import column_property

from .project import Project
from .subscribable import Subscribable


release_statuses = [
    'in-progress',
    'on-hold',
    'delayed',
    'complete',
]


class Release(ModifiedMixin, FilteringMixin, OrderingMixin, PaginationMixin,
              Subscribable):

    __tablename__ = 'release'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    status = Field(
        Enum(*release_statuses, name='release_status'),
        python_type=str,
        label='Status',
        watermark='Choose a status',
        nullable=True,
        required=False,
        example='Lorem Ipsum'
    )
    cutoff = Field(
        DateTime,
        python_type=datetime,
        label='Cutoff',
        pattern=
            r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])'
            r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$',
        pattern_description='ISO format and format like "yyyy-mm-dd" is valid',
        example='2018-02-02T1:12:12.000Z',
        watermark='Enter a cutoff date',
        nullable=False,
        not_none=True,
        required=True
    )

    attachments = relationship('Attachment', lazy='selectin')
    projects = relationship(
        'Project',
        primaryjoin=id == Project.release_id,
        back_populates='release',
        protected=True,
        lazy='selectin'
    )

    due_date = column_property(
        select([func.max(Project.due_date)]).\
            where(Project.release_id == id).\
            correlate_except(Project)
    )

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='dueDate',
            key='due date',
            label='Target',
            readonly=True,
            example='Lorem Ipsum',
            watermark='Lorem Ipsum',
            message='Lorem Ipsum',
            not_none=True,
            required=True,
        )

    def to_dict(self):
        release_dict = super().to_dict()
        release_dict['dueDate'] = self.due_date.isoformat() \
            if self.due_date else None
        return release_dict

    def __repr__(self):
        return f'\tTitle: {self.title}\n'

