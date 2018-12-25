from datetime import datetime

from nanohttp import context
from restfulpy.orm import Field, DeclarativeBase, relationship, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy.orm import column_property
from sqlalchemy import Integer, ForeignKey, Enum, select, func, bindparam, \
    DateTime, String, Column, Table

from .subscribable import Subscribable, Subscription


class DraftIssueTag(DeclarativeBase):
    __tablename__ = 'draft_issue_tag'

    tag_id = Field(
        Integer,
        ForeignKey('tag.id'),
        primary_key=True
    )
    draft_issue_id = Field(
        Integer,
        ForeignKey('draft_issue.id'),
        primary_key=True
    )


class DraftIssue(DeclarativeBase):

    __tablename__ = 'draft_issue'

    id = Field(Integer, primary_key=True)

    issue_id = Field(Integer, ForeignKey('issue.id'), nullable=True)

    tags = relationship(
        'Tag',
        secondary='draft_issue_tag',
        back_populates='draft_issues',
        protected=True
    )

    issue = relationship(
        'Issue',
        back_populates='draft_issues',
        protected=True
    )

