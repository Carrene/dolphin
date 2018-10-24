from datetime import datetime

from restfulpy.orm import Field, DeclarativeBase, relationship, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin
from sqlalchemy import Integer, ForeignKey, DateTime, Enum, String, Column, \
    Table

from .subscribable import Subscribable


association_table = Table('issue_tag', DeclarativeBase.metadata,
    Column('issue_id', Integer, ForeignKey('issue.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


issue_statuses = [
    'backlog',
    'triage',
    'in-progress',
    'on-hold',
    'delayed',
    'done',
]


issue_kinds = [
    'feature',
    'enhancement',
    'bug',
]


class Tag(DeclarativeBase):
    __tablename__ = 'tag'

    id = Field(Integer, primary_key=True)
    title = Field(
        String,
        max_length=50,
        min_length=1,
        label='Title',
        watermark='Enter the title',
        nullable=False,
        not_none=False,
        required=False,
        python_type=str
    )
    issues = relationship(
        'Issue',
        secondary=association_table,
        back_populates='tags'
    )


class Issue(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
            Subscribable):

    __tablename__ = 'issue'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    _boarding = ['on-time', 'delayed']

    project_id = Field(Integer, ForeignKey('project.id'))

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    due_date = Field(
        DateTime,
        label='Cutoff',
        pattern=r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])$',
        example='2018-02-02',
        watermark='Enter a due date',
        nullable=False,
        not_none=True,
        required=False,
    )
    kind = Field(
        Enum(*issue_kinds, name='kind'),
        label='Status',
        watermark='Choose a status',
        not_none=True,
        required=False,
        default='queued'
    )
    days = Field(Integer)
    status = Field(
        Enum(*issue_statuses, name='issues_status'),
        nullable=True,
        default='triage'
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

    items = relationship(
        'Item',
        back_populates='issue',
        protected=True
    )

    @property
    def boardings(self):
        if self.due_date < datetime.now():
            return self._boarding[1]

        return self._boarding[0]

    def to_dict(self):
        project_dict = super().to_dict()
        project_dict['boarding'] = self.boardings
        return project_dict

