from restfulpy.orm import Field, DeclarativeBase, relationship, OrderingMixin, \
    FilteringMixin, PaginationMixin
from sqlalchemy import Integer, ForeignKey, String


class Tag(DeclarativeBase, OrderingMixin, FilteringMixin, PaginationMixin):

    __tablename__ = 'tag'

    id = Field(Integer, primary_key=True)

    organization_id = Field(Integer, ForeignKey('organization.id'))

    title = Field(
        String,
        max_length=50,
        min_length=1,
        label='Title',
        watermark='Enter the title',
        example='lorem ipsum',
        nullable=False,
        not_none=True,
        required=True,
        python_type=str
    )

    issues = relationship(
        'Issue',
        secondary='issue_tag',
        back_populates='tags'
    )

    draft_issues = relationship(
        'DraftIssue',
        secondary='draft_issue_tag',
        back_populates='tags'
    )

    organization = relationship(
        'Organization',
        back_populates='tags',
        protected=True
    )

