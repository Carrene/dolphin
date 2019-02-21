from datetime import datetime

from nanohttp import context
from restfulpy.orm import Field, DeclarativeBase, relationship, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, ForeignKey, Enum, select, func, bindparam, \
    DateTime, case, join
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property
from auditor import observe

from .item import Item
from .subscribable import Subscribable, Subscription
from .phase import Phase
from .tag import Tag
from .member import Member


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


issue_priorities = [
    'low',
    'normal',
    'high',
]


DELAYED = 'delayed'
ONTIME = 'on-time'


class Issue(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin, \
            Subscribable):

    __tablename__ = 'issue'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    _boarding = ['on-time', 'delayed']

    id = Field(
        Integer,
        ForeignKey('subscribable.id'),
        primary_key=True,
        label='ID',
        readonly=True,
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

    draft_issues = relationship(
        'DraftIssue',
        back_populates='issue',
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
        select([func.count(Subscription.member_id)]) \
        .select_from(
            join(Subscription, Member, Subscription.member_id == Member.id)
        ) \
        .where(Subscription.subscribable_id == id) \
        .where(Member.reference_id == bindparam(
                'reference_id',
                callable_=lambda: context.identity.reference_id
            )
        ) \
        .correlate_except(Subscription),
        deferred=True
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
            name='boarding',
            key='boarding',
            label='Pace',
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

    def to_dict(self, include_relations=True):
        issue_dict = super().to_dict()
        issue_dict['boarding'] = self.boarding
        issue_dict['isSubscribed'] = True if self.is_subscribed else False

        if include_relations:
            issue_dict['relations'] = []
            for x in self.relations:
                issue_dict['relations'].append(
                    x.to_dict(include_relations=False)
                )

        return issue_dict

    @classmethod
    def filter_by_request(cls, query):
        query = super().filter_by_request(query)

        if 'phaseId' in context.query:
            value = context.query['phaseId']
            item_cte = select([
                Item.issue_id,
                func.max(Item.id).label('max_item_id')
            ]) \
                .group_by(Item.issue_id) \
                .cte()

            query = query.join(Item, Item.issue_id == Issue.id)
            query = query.join(item_cte, item_cte.c.max_item_id == Item.id)
            query = cls._filter_by_column_value(
                query,
                Item.phase_id,
                value
            )

        if 'phaseTitle' in context.query:
            value = context.query['phaseTitle']
            if 'phaseId' in context.query:
                query = query.join(Phase, Item.phase_id == Phase.id)

            else:
                query = query \
                    .join(Item, Item.issue_id == Issue.id) \
                    .join(Phase, Item.phase_id == Phase.id)

            query = cls._filter_by_column_value(query, Phase.title, value)

        if 'tagId' in context.query:
            value = context.query['tagId']
            query = query.join(IssueTag, IssueTag.issue_id == Issue.id)
            query = cls._filter_by_column_value(query, IssueTag.tag_id, value)

        if 'tagTitle' in context.query:
            value = context.query['tagTitle']
            if 'tagId' in context.query:
                query = query.join(Tag, Tag.id == IssueTag.tag_id)

            else:
                query = query \
                    .join(IssueTag, IssueTag.issue_id == Issue.id) \
                    .join(Tag, Tag.id == IssueTag.tag_id)

            query = cls._filter_by_column_value(query, Tag.title, value)

        return query

    @classmethod
    def sort_by_request(cls, query):
        query = super().sort_by_request(query)
        external_columns = ('phaseId', 'tagId')
        sorting_expression = context.query.get('sort', '').strip()

        if not sorting_expression:
            return query

        sorting_columns = {
                c[1:] if c.startswith('-') else c:
                'desc' if c.startswith('-') else None
            for c in sorting_expression.split(',')
            if c.replace('-', '') in external_columns
        }

        if 'phaseId' in sorting_expression:
            item_cte = select([
                Item.issue_id,
                func.max(Item.id).label('max_item_id')
            ]) \
                .group_by(Item.issue_id) \
                .cte()

            query = query.join(Item, Item.issue_id == Issue.id)
            query = query.join(item_cte, item_cte.c.max_item_id == Item.id)
            query = cls._sort_by_key_value(
                query,
                column=Item.phase_id,
                descending=sorting_columns['phaseId']
            )

        if 'tagId' in sorting_expression:
            query = query.join(IssueTag, IssueTag.issue_id == Issue.id)
            query = cls._sort_by_key_value(
                query,
                column=IssueTag.tag_id,
                descending=sorting_columns['tagId']
            )

        return query

    @classmethod
    def __declare_last__(cls):
        observe(cls, ['modified_at', 'project_id'])

