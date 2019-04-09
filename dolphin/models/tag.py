from restfulpy.orm import Field, DeclarativeBase, relationship, OrderingMixin, \
    FilteringMixin, PaginationMixin
from sqlalchemy import Integer, ForeignKey, String, Unicode


class Tag(DeclarativeBase, OrderingMixin, FilteringMixin, PaginationMixin):

    __tablename__ = 'tag'

    id = Field(
        Integer,
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
        example=1,
        protected=False,
    )
    organization_id = Field(
        Integer,
        ForeignKey('organization.id'),
        readonly=True,
    )

    title = Field(
        String,
        max_length=50,
        min_length=1,
        label='Tag Name',
        watermark='Enter the title',
        example='lorem ipsum',
        nullable=False,
        not_none=True,
        required=True,
        python_type=str
    )

    description = Field(
        Unicode,
        min_length=1,
        max_length=8192,
        label='Description',
        watermark='Lorem Ipsum',
        not_none=False,
        nullable=True,
        required=False,
        python_type=str,
        example='Lorem Ipsum'
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

    def __repr__(self):
        return f'\tTitle: {self.title}\n'

