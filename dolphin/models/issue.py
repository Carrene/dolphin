
from sqlalchemy import Integer, Time, ForeignKey, DateTime, Enum, String,\
    Column, Table
from restfulpy.orm import Field, DeclarativeBase, TimestampMixin, relationship

from .subscribable import Subscribable


association_table = Table('issue_tag', DeclarativeBase.metadata,
    Column('issue_id', Integer, ForeignKey('issue.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class Tag(DeclarativeBase):
    __tablename__ = 'tag'

    id = Field(Integer, primary_key=True)
    name = Field(String, max_length=40, unique=True, example='feature')

    issues = relationship(
        'Issue',
        secondary=association_table,
        back_populates='tags'
    )


class Issue(Subscribable):
    __tablename__ = 'issue'
    __mapper_args__ = {'polymorphic_identity': __tablename__}


    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    project_id = Field(Integer, ForeignKey('project.id'))
    stage_id = Field(Integer, ForeignKey('stage.id'))
    kind = Field(
        Enum('feature', 'enhancement', 'bug', name='kind'),
    )
    duration = Field(DateTime)
    status = Field(
        Enum('in-progress', 'on-hold', 'delayed', 'complete', name='status'),
    )

    tags = relationship(
        'Tag',
        secondary=association_table,
        back_populates='issues',
        protected=True
    )
    stage = relationship(
        'Stage',
        back_populates='issues',
        foreign_keys=[stage_id],
        protected=True
    )

