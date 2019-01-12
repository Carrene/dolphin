from restfulpy.orm import Field, relationship, SoftDeleteMixin, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin, \
    DeclarativeBase
from sqlalchemy import Integer, String


class Workflow(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
               SoftDeleteMixin, DeclarativeBase):

    __tablename__ = 'workflow'

    id = Field(Integer, primary_key=True)
    title = Field(
        String,
        max_length=50,
        min_length=1,
        label='Name',
        watermark='Enter the name',
        pattern=r'^[^\s].+[^\s]$',
        pattern_description='Spaces at the first and end of title is not valid',
        example='Sample Title',
        nullable=False,
        not_none=True,
        required=True,
        python_type=str
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

