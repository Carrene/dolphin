from restfulpy.orm import Field, DeclarativeBase, relationship, ModifiedMixin
from sqlalchemy import Integer, ForeignKey

from .issue import Issue


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


class DraftIssue(ModifiedMixin, DeclarativeBase):

    __tablename__ = 'draft_issue'

    id = Field(Integer, primary_key=True)

    issue_id = Field(
        Integer,
        ForeignKey('issue.id'),
        nullable=True,
        required=False,
        not_none=False
    )

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

    def to_dict(self):
        result = {}
        result['id'] = self.id
        result['issueId'] = self.issue_id
        return result

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield from Issue.iter_metadata_fields()

