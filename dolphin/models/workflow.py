from restfulpy.orm import Field, relationship, SoftDeleteMixin, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin, \
    DeclarativeBase
from sqlalchemy import Integer, String, Unicode
from restfulpy.orm.metadata import MetadataField
from sqlalchemy import Integer, String


class Workflow(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
               SoftDeleteMixin, DeclarativeBase):

    __tablename__ = 'workflow'

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
        String,
        max_length=50,
        min_length=1,
        label='Workflow Name',
        watermark='Enter the name',
        pattern=r'^[^\s].+[^\s]$',
        pattern_description='Spaces at the first and end of title is not valid',
        example='Sample Title',
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

    phases = relationship(
        'Phase',
        back_populates='workflow',
        protected=True
    )

    projects = relationship(
        'Project',
        back_populates='workflow',
        protected=True
    )

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='phases',
            key='phases',
            label='Phases',
        )

    def __repr__(self):
        return f'\tTitle: {self.title}\n'

