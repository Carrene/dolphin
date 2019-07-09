from restfulpy.orm import Field, DeclarativeBase, relationship, \
    OrderingMixin, FilteringMixin, PaginationMixin
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, ForeignKey, String, Unicode, UniqueConstraint


class Batch(DeclarativeBase, OrderingMixin, FilteringMixin, PaginationMixin):

    __tablename__ = 'batch'

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
    title = Field(
        Unicode(50),
        min_length=2,
        label='Batch title',
        watermark='Lorem Ipsum',
        not_none=True,
        required=True,
        python_type=str,
        protected=False,
        example='Lorem Ipsum'
    )
    project_id = Field(
        Integer,
        ForeignKey('project.id'),
        not_none=True,
        readonly=True
    )
    issues = relationship(
        'Issue',
        back_populates='batches',
        protected=True
    )
    projects = relationship(
        'Project',
        back_populates='batches',
        protected=True
    )

    __table_args__ = (
        UniqueConstraint(
            title,
            project_id,
            name='uix_title_project_id'
        ),
    )

    def to_dict(self):
        batch_dict = super().to_dict()
        batch_dict['issueIds'] = [i.id for i in self.issues]
        return batch_dict

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='issue_ids',
            key='issueIds',
            label='Issues IDs',
            required=False,
            readonly=True
        )

