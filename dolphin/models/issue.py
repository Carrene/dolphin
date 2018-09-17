
from sqlalchemy import Integer, Time, ForeignKey, DateTime, Enum, String,\
    Column, Table
from restfulpy.orm import Field, DeclarativeBase, TimestampMixin, \
    relationship, ModifiedMixin, OrderingMixin, FilteringMixin,\
    PaginationMixin

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
    title = Field(String, max_length=40, unique=True, example='feature')

    issues = relationship(
        'Issue',
        secondary=association_table,
        back_populates='tags'
    )


class Issue(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
            Subscribable):

    __tablename__ = 'issue'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    project_id = Field(Integer, ForeignKey('project.id'))
    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)

    kind = Field(Enum(*issue_kinds, name='kind'))
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

