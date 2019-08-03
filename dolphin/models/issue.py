from datetime import datetime, timedelta

from auditor import observe
from nanohttp import context
from restfulpy.orm import Field, DeclarativeBase, relationship, \
    OrderingMixin, FilteringMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, ForeignKey, Enum, select, func, bindparam, \
    case, join, and_, exists, DateTime, Boolean, null
from sqlalchemy.event import listens_for
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import column_property

from ..constants import ISSUE_RESPONSE_TIME
from ..mixins import ModifiedByMixin, CreatedByMixin
from .issue_phase import IssuePhase
from .item import Item
from .member import Member
from .phase import Phase
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


issue_stages = [
    'triage',
    'backlog',
    'working',
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


issue_origins = [
    'new',
    'backlog',
]


class Priority:
    low =      (1, 'low')
    normal =   (2, 'normal')
    high =     (3, 'high')


class Issue(OrderingMixin, FilteringMixin, PaginationMixin, ModifiedByMixin,
            CreatedByMixin, Subscribable):

    __tablename__ = 'issue'
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
    origin = Field(
        Enum(*issue_origins, name='issues_origin'),
        python_type=str,
        label='Origin',
        default='new',
        not_none=True,
        required=False,
        protected=False,
        readonly=True,
        watermark='Lorem ipsum',
        message='Lorem ipsum',
        example='Lorem ipsum',
    )
    stage = Field(
        Enum(*issue_stages, name='issues_stage'),
        python_type=str,
        label='Phase',
        default='triage',
        required=False,
        not_none=True,
        protected=False,
        readonly=False,
        watermark='lorem ipsum',
        message='lorem ipsum',
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
    last_moving_time = Field(
        DateTime,
        python_type=datetime,
        default=datetime.now(),
        label='Last Moving Time',
        nullable=True,
        protected=True,
        required=False,
        not_none=False,
        readonly=True,
    )
    batch = Field(
        Integer,
        python_type=int,
        label='Batch',
        minimum=1,
        maximum=1000,
        nullable=True,
        not_none=False,
        required=False,
        readonly=False,
        watermark='lorem ipsum',
        example='lorem ipsum',
        message='lorem ipsum',
    )
    is_batch_leader = Field(
        Boolean,
        python_type=bool,
        label='Batch Leader',
        default=None,
        nullable=True,
        not_none=False,
        required=False,
        readonly=True,
        watermark='lorem ipsum',
        example='lorem ipsum',
        message='lorem ipsum',
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
        back_populates='issues',
        foreign_keys=[project_id],
        protected=False,
    )
    returntotriagejobs = relationship(
        'ReturnToTriageJob',
        back_populates='issue',
        protected=False,
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
    issue_phases = relationship(
        'IssuePhase',
        back_populates='issue',
        protected=True,
    )
    relations = relationship(
        'Issue',
        secondary='related_issue',
        primaryjoin=id == RelatedIssue.issue_id,
        secondaryjoin=id == RelatedIssue.related_issue_id,
        lazy='selectin',
    )
    due_date = column_property(
        select([func.max(Item.end_date)]) \
        .select_from(
            join(IssuePhase, Item, IssuePhase.id == Item.issue_phase_id)
        ) \
        .where(IssuePhase.issue_id == id) \
        .correlate_except(Item)
    )

    is_done = column_property(
        select([func.bool_and(Item.is_done)]) \
        .select_from(
            join(IssuePhase, Item, IssuePhase.id == Item.issue_phase_id)
        ) \
        .where(IssuePhase.issue_id == id) \
        .correlate_except(Item)
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

    _not_estimated_phases = select([Item.issue_phase_id]) \
        .where(Item.estimated_hours.is_(None)) \
        .group_by(Item.issue_phase_id)

    phase_id = column_property(
        select([IssuePhase.phase_id])
        .select_from(join(IssuePhase, Phase, IssuePhase.phase_id == Phase.id))
        .where(IssuePhase.id.notin_(_not_estimated_phases))
        .where(IssuePhase.issue_id == id)
        .order_by(Phase.order.desc())
        .limit(1)
    )

    _need_estimated_phase_id = column_property(
        select([IssuePhase.phase_id]) \
            .select_from(
                join(IssuePhase, Phase, IssuePhase.phase_id == Phase.id)
                .join(Item, IssuePhase.id == Item.issue_phase_id)
            ) \
            .where(IssuePhase.issue_id == id) \
            .where(Item.estimated_hours.is_(None)) \
            .order_by(Phase.order) \
            .limit(1) \
            .as_scalar()
    )

    status = column_property(
        case([
            (
                is_done,
                'done'
            ),
            (
                exists(
                    select([IssuePhase.status])
                    .where(and_(
                        IssuePhase.issue_id == id,
                        IssuePhase.phase_id == phase_id
                    ))
                ),
                select([IssuePhase.status])
                .where(and_(
                    IssuePhase.issue_id == id,
                    IssuePhase.phase_id == phase_id
                )).as_scalar()
            )
        ], else_='to-do').label('status'),
        deferred=True
    )

    boarding = column_property(
        case([
            (
                stage == 'on-hold',
                'frozen'
            ),
            (
                due_date == null(),
                'on-time'
            ),
            (
                due_date < func.now(),
                'delayed'
            ),
        ], else_='on-time').label('boarding'),
    )

    @hybrid_property
    def response_time(self):
        if self.last_moving_time:
            return self.last_moving_time - \
                datetime.now() + \
                timedelta(hours=ISSUE_RESPONSE_TIME)

        return None

    @response_time.expression
    def response_time(cls):
        # The constant `ISSUE_RESPONSE_TIME` used in query below is derived from
        # constants.py instead of `nanohttp.settings`. Because before setting
        # up the models, `Issue` model is loaded; So the response_time
        # expression is loaded at this time also. Thus, settings is not
        # initialized yet.
        return case([
            (
                cls.last_moving_time != None,
                (
                    func.date_part(
                        'day',
                        cls.last_moving_time - func.now()
                    ) * 24
                ) + \
                (
                    func.date_part(
                        'hour',
                        cls.last_moving_time - func.now()
                    )
                ) + \
                ISSUE_RESPONSE_TIME
            )
        ])

    boarding = column_property(
        case([
            (
                stage == 'on-hold',
                'frozen'
            ),
            (
                due_date == null(),
                'on-time'
            ),
            (
                due_date < func.now(),
                'delayed'
            ),
        ], else_='on-time').label('boarding'),
    )

    @hybrid_property
    def priority_value(self):
        return getattr(Priority, self.priority)[0]

    @priority_value.expression
    def priority_value(cls):
        return case([
            (cls.priority == 'low', Priority.low[0]),
            (cls.priority == 'normal', Priority.normal[0]),
            (cls.priority == 'high', Priority.high[0])
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
        yield MetadataField(
            name='priorityValue',
            key='priority_value',
            label='Priority Value',
            required=False,
            readonly=True,
        )
        yield MetadataField(
            name='dueDate',
            key='due_date',
            label='Target',
            required=False,
            readonly=True
        )
        yield MetadataField(
            name='status',
            key='status',
            label='Status',
            required=False,
            not_none=False,
            readonly=True,
            watermark='Lorem Ipsum',
            example='Lorem Ipsum',
            message='Lorem Ipsum',
        )
        yield MetadataField(
            name='items',
            key='items',
            label='Items',
            required=False,
            not_none=False,
            readonly=True,
            watermark='Lorem Ipsum',
            example='Lorem Ipsum',
            message='Lorem Ipsum',
        )
        yield MetadataField(
            name='isDone',
            key='is_done',
            label='Lorem Ipsum',
            required=False,
            readonly=True,
        )
        yield MetadataField(
            name='project',
            key='project',
            label='Project',
            required=False,
            readonly=True,
        )
        yield MetadataField(
            name='returnToTriage',
            key='returntotriagejobs',
            label='Return to triage',
            required=False,
            readonly=True,
        )
        yield MetadataField(
            name='responseTime',
            key='response_time',
            label='Response Time',
            required=False,
            readonly=True,
            not_none=True,
            protected=False,
        )
        yield MetadataField(
            name='returnToTriage',
            key='returntotriagejobs',
            label='Return to triage',
            required=False,
            readonly=True,
        )
        yield MetadataField(
            name='NeedEstimatedPhaseId',
            key='_need_estimated_phase_id',
            label='need estimated phase id',
            required=False,
            readonly=True
        )

    def to_dict(self, include_relations=True):
        # The `issue` relationship on Item model is `protected=False`, So the
        # `items` relationship on Issue model must be `protected=True`, So that
        # this causes recursively getting the instances of `issue` and `item`
        # model. But there is some field from Item model that is needed in Issue
        # which are appended to Issue.to_dict return value manually.
        items_list = []
        for issue_phase in self.issue_phases:
            for item in issue_phase.items:
                items_list.append(dict(
                    memberId=item.member_id,
                    createdAt=item.created_at,
                    phaseId=issue_phase.phase_id,
                ))

        issue_dict = super().to_dict()
        issue_dict['responseTime'] = \
            self._get_hours(self.response_time) \
            if self.response_time else None
        issue_dict['status'] = self.status
        issue_dict['boarding'] = self.boarding
        issue_dict['isSubscribed'] = True if self.is_subscribed else False
        issue_dict['seenAt'] = \
            self.seen_at.isoformat() if self.seen_at else None
        issue_dict['items'] = items_list
        issue_dict['dueDate'] = \
            self.due_date.isoformat() if self.due_date else None
        issue_dict['isDone'] = self.is_done
        if include_relations:
            issue_dict['relations'] = []
            for x in self.relations:
                issue_dict['relations'].append(
                    x.to_dict(include_relations=False)
                )
        issue_dict['stage'] = self.stage

        return issue_dict

    @classmethod
    def __declare_last__(cls):
        super().__declare_last__()
        observe(
            cls,
            ['modified_at', 'project_id', 'modified_by', 'returntotriagejobs']
        )

    def get_room_title(self):
        return f'{self.title.lower()}-{self.project_id}'

    @staticmethod
    def _get_hours(timedelta):
        return timedelta.total_seconds() // 3600


@listens_for(Issue.stage, 'set')
def handle_change_stage(target, value, oldvalue, initiator):
    if value == 'triage':
        target.last_moving_time = datetime.now()

    elif value == 'backlog':
        target.origin = 'backlog'
        target.last_moving_time = None

