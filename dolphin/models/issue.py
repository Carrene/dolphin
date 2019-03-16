from datetime import datetime

from auditor import observe
from nanohttp import context
from restfulpy.orm import Field, DeclarativeBase, relationship, OrderingMixin, FilteringMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, ForeignKey, Enum, select, func, bindparam, \
    DateTime, case, join
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property

from ..mixins import ModifiedByMixin
from .item import Item
from .member import Member
from .subscribable import Subscribable, Subscription


class IssueTag(DeclarativeBase):
    __tablename__ = 'issue_tag'

    tag_id = Field(
        Integer,
        ForeignKey('tag.id'),
        primary_key=True
    )
    issue_id = Field(
        Integer,
        ForeignKey('issue.id'),
        primary_key=True
    )


class RelatedIssue(DeclarativeBase):
    __tablename__ = 'related_issue'

    issue_id = Field(Integer, ForeignKey('issue.id'), primary_key=True)
    related_issue_id = Field(Integer, ForeignKey('issue.id'), primary_key=True)


issue_statuses = [
    'to-do',
    'in-progress',
    'done',
    'complete',
    'on-hold',
]


issue_kinds = [
    'feature',
    'bug',
]


issue_priorities = [
    'low',
    'normal',
    'high',
]


class Boarding:
    ontime =    (1, 'on-time')
    delayed =   (2, 'delayed')
    frozen =    (3, 'frozen')
    atrisk =    (4, 'at-risk')


class Issue(OrderingMixin, FilteringMixin, PaginationMixin, ModifiedByMixin,
            Subscribable):

    __tablename__ = 'issue'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    _boarding = ['on-time', 'delayed']

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
    project_id = Field(
        Integer,
        ForeignKey('project.id'),
        python_type=int,
        nullable=True,
        watermark='Choose a project',
        label='Project',
        not_none=True,
        required=False,
        example='Lorem Ipsum'
    )
    room_id = Field(Integer, readonly=True)

    due_date = Field(
        DateTime,
        python_type=datetime,
        label='Target',
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
        default='bug',
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
        example='lorem ipsum',
    )

    attachments = relationship('Attachment', lazy='selectin')

    tags = relationship(
        'Tag',
        secondary='issue_tag',
        back_populates='issues',
        protected=False,
    )
    project = relationship(
        'Project',
        foreign_keys=[project_id],
        back_populates='issues',
        protected=True
    )
    members = relationship(
        'Member',
        secondary='item',
        back_populates='issues',
        lazy='selectin',
        protected=True,
    )

    draft_issue = relationship(
        'DraftIssue',
        back_populates='issue',
        protected=True,
    )

    draft_issues = relationship(
        'DraftIssue',
        back_populates='related_issues',
        protected=True,
    )

    items = relationship(
        'Item',
        protected=False,
        order_by=Item.created_at,
    )

    relations = relationship(
        'Issue',
        secondary='related_issue',
        primaryjoin=id == RelatedIssue.issue_id,
        secondaryjoin=id == RelatedIssue.related_issue_id,
        lazy='selectin',
    )

    is_subscribed = column_property(
        select([func.count(Subscription.member_id)])
        .select_from(
            join(Subscription, Member, Subscription.member_id == Member.id)
        )
        .where(Subscription.subscribable_id == id)
        .where(Member.reference_id == bindparam(
            'reference_id',
            callable_=lambda:
                context.identity.reference_id if context.identity else None
            )
        )
        .where(Subscription.one_shot.is_(None))
        .correlate_except(Subscription),
        deferred=True
    )

    seen_at = column_property(
        select([Subscription.seen_at])
        .select_from(
            join(Subscription, Member, Subscription.member_id == Member.id)
        )
        .where(Subscription.subscribable_id == id)
        .where(Member.reference_id == bindparam(
            'reference_id',
            callable_=lambda:
                context.identity.reference_id if context.identity else None
            )
        )
        .where(Subscription.one_shot.is_(None))
        .correlate_except(Subscription),
        deferred=True
    )

    @hybrid_property
    def boarding_value(self):
        if self.status == 'on-hold':
            return Boarding.frozen[0]

        elif self.due_date < datetime.now():
            return Boarding.delayed[0]

        return Boarding.ontime[0]

    @boarding_value.expression
    def boarding_value(cls):
        return case([
            (cls.status == 'on-hold', Boarding.frozen[0]),
            (cls.due_date < datetime.now(), Boarding.delayed[0]),
            (cls.due_date > datetime.now(), Boarding.ontime[0])
        ])

    @hybrid_property
    def boarding(self):
        if self.status == 'on-hold':
            return Boarding.frozen[1]

        elif self.due_date < datetime.now():
            return Boarding.delayed[1]

        return Boarding.ontime[1]

    @boarding.expression
    def boarding(cls):
        return case([
            (cls.status == 'on-hold', Boarding.frozen[1]),
            (cls.due_date < datetime.now(), Boarding.delayed[1]),
            (cls.due_date > datetime.now(), Boarding.ontime[1])
        ])

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='boarding',
            key='boarding',
            label='Tempo',
            required=False,
            readonly=True
        )
        yield MetadataField(
            name='isSubscribed',
            key='is_subscribed',
            label='Subscribe',
            required=False,
            readonly=True
        )
        yield MetadataField(
            name='tags',
            key='tags',
            label='Tags',
            required=False,
            readonly=True,
            not_none=False,
            watermark='Lorem Ipsum',
            example='Lorem Ipsum'
        )
        yield MetadataField(
            name='phaseId',
            key='phase_id',
            label='Phase',
            required=False,
            not_none=False,
            readonly=True,
            watermark='Lorem Ipsum',
            example='Lorem Ipsum',
            message='Lorem Ipsum',
        )
        yield MetadataField(
            name='tagId',
            key='tag_id',
            label='Tag',
            required=False,
            not_none=False,
            readonly=True,
            watermark='Lorem Ipsum',
            example='Lorem Ipsum',
            message='Lorem Ipsum',
        )
        yield MetadataField(
            name='seenAt',
            key='seen_at',
            label='seen at',
            required=False,
            readonly=True
        )
        yield MetadataField(
            name='relations',
            key='relations',
            label='Related Nuggets',
            required=False,
            readonly=True
        )
        yield MetadataField(
            name='boardingValue',
            key='boarding_value',
            label='boarding value',
            required=False,
            readonly=True
        )
        yield MetadataField(
            name='unread',
            key='unread',
            label='unread',
            required=False,
            readonly=True
        )

    def to_dict(self, include_relations=True):
        issue_dict = super().to_dict()
        issue_dict['boarding'] = self.boarding
        issue_dict['isSubscribed'] = True if self.is_subscribed else False
        issue_dict['seenAt'] \
            = self.seen_at.isoformat() if self.seen_at else None

        if include_relations:
            issue_dict['relations'] = []
            for x in self.relations:
                issue_dict['relations'].append(
                    x.to_dict(include_relations=False)
                )

        return issue_dict

    @classmethod
    def __declare_last__(cls):
        super().__declare_last__()
        observe(cls, ['modified_at', 'project_id', 'modified_by'])

    def get_room_title(self):
        return f'{self.title.lower()}-{self.project_id}'

