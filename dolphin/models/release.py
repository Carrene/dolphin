from datetime import datetime

from auditor import observe
from nanohttp import context
from restfulpy.orm import Field, relationship, ModifiedMixin, FilteringMixin, \
    OrderingMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, Enum, DateTime, ForeignKey, select, func, \
    join, bindparam
from sqlalchemy.orm import column_property

from .project import Project
from .subscribable import Subscribable, Subscription
from .member import Member


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

    id = Field(
        Integer,
        ForeignKey('subscribable.id'),
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
        example=1,
        protected=False,
    )
    manager_id = Field(
        Integer,
        ForeignKey('member.id'),
        python_type=int,
        watermark='Choose a member',
        label='Manager',
        nullable=False,
        not_none=True,
        readonly=False,
        required=True,
    )
    room_id = Field(
        Integer,
        readonly=True,
        nullable=False,
        python_type=int,
    )
    group_id = Field(
        Integer,
        ForeignKey('group.id'),
        python_type=int,
        watermark='Lorem Ipsum',
        label='Group',
        nullable=False,
        not_none=True,
        required=False,
        message='Lorem Ipsum',
    )
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
        label='Release Cutoff',
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
    launch_date= Field(
        DateTime,
        python_type=datetime,
        label='Release Date',
        pattern=
            r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])'
            r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$',
        pattern_description='ISO format and format like "yyyy-mm-dd" is valid',
        example='2018-02-02T1:12:12.000Z',
        watermark='Enter a launch date',
        nullable=False,
        not_none=True,
        required=True,
        readonly=False,
    )

    projects = relationship(
        'Project',
        primaryjoin=id == Project.release_id,
        back_populates='release',
        protected=False,
        lazy='selectin'
    )

    manager = relationship(
        'Member',
        foreign_keys=[manager_id],
        back_populates='releases',
        protected=True
    )
    group = relationship(
        'Group',
        back_populates='releases',
        protected=True,
    )
    is_subscribed = column_property(
        select([func.count(Subscription.member_id)])
        .select_from(
            join(Subscription, Member, Subscription.member_id == Member.id)
        )
        .where(Subscription.subscribable_id == id)
        .where(Member.reference_id == bindparam(
                'reference_id',
                callable_=lambda: context.identity.reference_id
            )
        )
        .correlate_except(Subscription),
        deferred=True
    )

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='projects',
            key='projects',
            label='Project',
            readonly=True,
            example='Lorem Ipsum',
            watermark='Lorem Ipsum',
            message='Lorem Ipsum',
        )

    def __repr__(self):
        return f'\tTitle: {self.title}\n'

    def get_room_title(self):
        return f'{self.title.lower()}-{self.manager_id}'

    def to_dict(self):
        release_dict = super().to_dict()
        release_dict['isSubscribed'] = True if self.is_subscribed else False
        return release_dict

    @classmethod
    def __declare_last__(cls):
        super().__declare_last__()
        observe(cls, ['modified_at'])

