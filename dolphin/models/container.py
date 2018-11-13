from nanohttp import context
from restfulpy.orm import Field, relationship, SoftDeleteMixin, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, ForeignKey, Enum, select, func, bindparam
from sqlalchemy.orm import column_property

from .issue import Issue
from .subscribable import Subscribable, Subscription


container_statuses = [
    'active',
    'on-hold',
    'queued',
    'done',
]


class Container(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
                SoftDeleteMixin, Subscribable):

    __tablename__ = 'container'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    _boarding = ['on-time', 'delayed', 'at-risk']

    release_id = Field(
        Integer,
        ForeignKey('release.id'),
        python_type=int,
        nullable=True,
        watermark='Choose a launch',
        label='Launch',
        not_none=False,
        required=False
    )
    member_id = Field(
        Integer,
        ForeignKey('member.id'),
        python_type=int,
        watermark='Choose a member',
        label='Member',
        nullable=False,
        not_none=False,
        required=True
    )
    room_id = Field(Integer)

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    status = Field(
        Enum(*container_statuses, name='container_status'),
        python_type=str,
        label='Status',
        watermark='Choose a status',
        not_none=True,
        required=False,
        default='queued',
        example='Lorem Ipsum',
        message='Lorem Ipsum'
    )

    member = relationship(
        'Member',
        foreign_keys=[member_id],
        back_populates='containers',
        protected=True
    )
    release = relationship(
        'Release',
        foreign_keys=[release_id],
        back_populates='containers',
        protected=True
    )
    issues = relationship(
        'Issue',
        primaryjoin=id == Issue.project_id,
        back_populates='project',
        protected=True
    )

    due_date = column_property(
        select([func.max(Issue.due_date)]) \
        .where(Issue.container_id == id) \
        .correlate_except(Issue)
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

    @property
    def boardings(self):
        release = self.release
        if not self.issues or self.status == 'queued':
            return None

        for issue in self.issues:
            if release is not None and issue.due_date > release.cutoff:
                return self._boarding[2]

            if issue.boardings == 'delayed':
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

    def to_dict(self):
        container_dict = super().to_dict()
        container_dict['boarding'] = self.boardings
        container_dict['dueDate'] = self.due_date.isoformat() if self.due_date else None
        container_dict['isSubscribed'] = True if self.is_subscribed else False
        return container_dict

