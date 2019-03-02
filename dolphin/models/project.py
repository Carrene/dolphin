from nanohttp import context
from restfulpy.orm import Field, relationship, SoftDeleteMixin, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, ForeignKey, Enum, select, func, bindparam, \
    join, case
from sqlalchemy.orm import column_property
from sqlalchemy.ext.hybrid import hybrid_property

from .issue import Issue, Boarding
from .subscribable import Subscribable, Subscription
from .member import Member


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
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
        example=1,
        protected=False,
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
    manager_id = Field(
        Integer,
        ForeignKey('member.id'),
        python_type=int,
        watermark='Choose a member',
        label='Manager',
        nullable=False,
        not_none=True,
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

    manager = relationship(
        'Member',
        foreign_keys=[manager_id],
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

    boarding_value = column_property(
        select([func.max(Issue.boarding_value)]) \
        .where(Issue.project_id == id) \
        .where(status == 'active')
    )

    @hybrid_property
    def boarding(self):
        if self.boarding_value == 1:
            return Boarding.ontime[1]

        elif self.boarding_value == 2:
            return Boarding.delayed[1]

        return None

    @boarding.expression
    def boarding(cls):
        return case([
            (cls.boarding_value == 1, Boarding.ontime[1]),
            (cls.boarding_value == 2, Boarding.delayed[1])
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
            name='dueDate',
            key='due_date',
            label='Target',
            required=False,
            readonly=True,
            watermark='This will be calculated by its Nuggets automaticaly.',
        )
        yield MetadataField(
            name='isSubscribed',
            key='is_subscribed',
            label='is subscribed',
            required=False,
            readonly=True,
            watermark='Lorem Ipsum',
        )
        yield MetadataField(
            name='managerReferenceId',
            key='manager_reference_id',
            label='Lorem Ipsum',
            required=True,
            not_none=True,
            readonly=False,
            watermark='Lorem Ipsum',
            example='Lorem Ipsum',
            message='Lorem Ipsum',
        )
        yield MetadataField(
            name='boardingValue',
            key='boarding_value',
            label='boarding value',
            required=False,
            readonly=True
        )

    def to_dict(self):
        project_dict = super().to_dict()
        project_dict['boarding'] = self.boarding
        project_dict['isSubscribed'] = True if self.is_subscribed else False
        project_dict['dueDate'] = self.due_date.isoformat() \
            if self.due_date else None
        return project_dict

    def get_room_title(self):
        return f'{self.title.lower()}-{self.manager_id}-{self.workflow_id}_' \
            f'{self.release_id}-{self.group_id}'

