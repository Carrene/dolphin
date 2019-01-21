from nanohttp import context
from restfulpy.orm import Field, relationship, SoftDeleteMixin, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, ForeignKey, Enum, select, func, bindparam
from sqlalchemy.orm import column_property

from .issue import Issue
from .subscribable import Subscribable, Subscription
from .attachment import Attachment


project_statuses = [
    'active',
    'on-hold',
    'queued',
    'done',
]


class Project(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
              SoftDeleteMixin, Subscribable):

    __tablename__ = 'project'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    _boarding = ['on-time', 'delayed', 'at-risk']

    id = Field(
        Integer,
        ForeignKey('subscribable.id'),
        primary_key=True,
        readonly=True,
    )

    workflow_id = Field(
        Integer,
        ForeignKey('workflow.id'),
        python_type=int,
        nullable=False,
        watermark='Choose a workflow',
        label='Workflow',
        not_none=True,
        required=False,
        example='Lorem Ipsum'
    )

    release_id = Field(
        Integer,
        ForeignKey('release.id'),
        python_type=int,
        nullable=False,
        watermark='Choose a launch',
        label='Launch',
        not_none=True,
        required=True,
        example='Lorem Ipsum'
    )
    member_id = Field(
        Integer,
        ForeignKey('member.id'),
        python_type=int,
        watermark='Choose a member',
        label='Member',
        nullable=False,
        not_none=False,
        readonly=True,
        required=True
    )
    group_id = Field(
        Integer,
        ForeignKey('group.id'),
        python_type=int,
        watermark='Choose a group',
        label='Group',
        nullable=False,
        not_none=True,
        required=False,
        message='Lorem Ipsum'
    )

    room_id = Field(Integer, readonly=True)

    status = Field(
        Enum(*project_statuses, name='project_status'),
        python_type=str,
        label='Status',
        watermark='Choose a status',
        not_none=True,
        required=False,
        default='queued',
        example='Lorem Ipsum'
    )

    workflow = relationship(
        'Workflow',
        back_populates='projects',
        protected=True
    )

    member = relationship(
        'Member',
        foreign_keys=[member_id],
        back_populates='projects',
        protected=True
    )
    release = relationship(
        'Release',
        foreign_keys=[release_id],
        back_populates='projects',
        protected=True
    )
    issues = relationship(
        'Issue',
        primaryjoin=id == Issue.project_id,
        back_populates='project',
        protected=True
    )
    attachments = relationship('Attachment', lazy='selectin')
    group = relationship(
        'Group',
        uselist=False,
        back_populates='projects',
        protected=True,
    )

    due_date = column_property(
        select([func.max(Issue.due_date)]) \
        .where(Issue.project_id == id) \
        .correlate_except(Issue)
    )

    is_subscribed = column_property(
        select([func.count(Subscription.member_id)]) \
        .where(Subscription.subscribable_id == id) \
        .where(Subscription.member_id == bindparam(
                'member_id',
                callable_=lambda: context.identity.id
            )
               ) \
        .correlate_except(Subscription),
        deferred=True
    )

    @property
    def boardings(self):
        if not self.issues or self.status == 'queued':
            return None

        for issue in self.issues:
            if issue.boarding == 'at-risk':
                return self._boarding[2]

            if issue.boarding == 'delayed':
                return self._boarding[1]

            if self.status != 'active':
                return None

        return self._boarding[0]

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
            'dueDate',
            'due date',
            label='Target',
            required=False,
            readonly=True,
            watermark='This will be calculated by its Nuggets automaticaly.',
        )
        yield MetadataField(
            'isSubscribed',
            'is subscribed',
            label='is subscribed',
            required=False,
            readonly=True,
            watermark='Lorem Ipsum',
        )

    def to_dict(self):
        project_dict = super().to_dict()
        project_dict['boarding'] = self.boardings
        project_dict['isSubscribed'] = True if self.is_subscribed else False
        project_dict['dueDate'] = self.due_date.isoformat() \
            if self.due_date else None
        return project_dict

