from datetime import datetime

from nanohttp import context
from restfulpy.orm import Field, DeclarativeBase, relationship, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy.orm import column_property
from sqlalchemy import Integer, ForeignKey, Enum, select, func, bindparam, \
    DateTime, String, Column, Table, case
from sqlalchemy.ext.hybrid import hybrid_property

from .subscribable import Subscribable, Subscription


association_table = Table('issue_tag', DeclarativeBase.metadata,
    Column('issue_id', Integer, ForeignKey('issue.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


issue_statuses = [
    'in-progress',
    'on-hold',
    'to-do',
    'done',
    'complete',
]


issue_kinds = [
    'feature',
    'bug',
]


DELAYED = 'delayed'
ONTIME = 'on-time'


issue_priorities = [
    'low',
    'normal',
    'high',
]


class Tag(DeclarativeBase, OrderingMixin, FilteringMixin, PaginationMixin):

    __tablename__ = 'tag'

    id = Field(Integer, primary_key=True)

    organization_id = Field(Integer, ForeignKey('organization.id'))

    title = Field(
        String,
        max_length=50,
        min_length=1,
        label='Title',
        watermark='Enter the title',
        example='lorem ipsum',
        message='lorem ipsum',
        nullable=False,
        not_none=True,
        required=True,
        python_type=str
    )

    issues = relationship(
        'Issue',
        secondary=association_table,
        back_populates='tags'
    )

    organization = relationship(
        'Organization',
        back_populates='tags',
        protected=True
    )


class Issue(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
            Subscribable):

    __tablename__ = 'issue'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    project_id = Field(Integer, ForeignKey('project.id'))
    room_id = Field(Integer)

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    due_date = Field(
        DateTime,
        python_type=datetime,
        label='Target Date',
        pattern=
            r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])'
            r'(T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z)?)?$',
        pattern_description='ISO format and format like "yyyy-mm-dd" is valid',
        example='2018-02-02T1:12:12.000Z',
        watermark='Enter a target',
        nullable=False,
        not_none=True,
        required=True,
    )
    kind = Field(
        Enum(*issue_kinds, name='kind'),
        python_type=str,
        label='Type',
        watermark='Choose a type',
        nullable=False,
        not_none=True,
        required=True,
    )
    days = Field(
        Integer,
        python_type=int,
        label='Days',
        watermark='How many days do you estimate?',
        minimum=1,
        maximum=1000,
        nullable=False,
        not_none=False,
        required=False
    )
    status = Field(
        Enum(*issue_statuses, name='issues_status'),
        python_type=str,
        label='Status',
        watermark='Choose a status',
        not_none=True,
        required=False,
        default='on-hold',
        message='lorem ipsum',
        example='lorem ipsum',
    )

    priority = Field(
        Enum(*issue_priorities, name='priority'),
        python_type=str,
        label='Priority',
        nullable=False,
        not_none=True,
        required=True,
        default='low',
        watermark='lorem ipsum',
        message='lorem ipsum',
        example='lorem ipsum',
    )

    tags = relationship(
        'Tag',
        secondary=association_table,
        back_populates='issues',
        protected=True
    )
    project = relationship(
        'Project',
        foreign_keys=[project_id],
        back_populates='issues',
        protected=True
    )
    phases = relationship(
        'Phase',
        secondary='item',
        back_populates='issues',
        lazy='selectin',
        protected=True,
    )
    members = relationship(
        'Member',
        secondary='item',
        back_populates='issues',
        lazy='selectin',
        protected=True,
    )

    is_subscribed = column_property(
        select([func.count(Subscription.member)]) \
        .where(Subscription.subscribable == id) \
        .where(Subscription.member == bindparam(
                'member_id',
                callable_=lambda: context.identity.id
            )
        ) \
        .correlate_except(Subscription)
    )

    @hybrid_property
    def boarding(self):
        if self.due_date < datetime.now():
            return DELAYED

        return ONTIME

    @boarding.expression
    def boarding(cls):
        return case([
            (cls.due_date < datetime.now(), DELAYED),
            (cls.due_date > datetime.now(), ONTIME)
        ])


    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            'boarding',
            'boarding',
            label='Pace',
            required=False,
            readonly=True
        )
        yield MetadataField(
            'isSubscribed',
            'isSubscribed',
            label='Subscribe',
            required=False,
            readonly=True
        )

    def to_dict(self):
        issue_dict = super().to_dict()
        issue_dict['boarding'] = self.boarding
        issue_dict['isSubscribed'] = True if self.is_subscribed else False
        return issue_dict

