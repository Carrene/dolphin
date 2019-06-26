from restfulpy.orm import Field, DeclarativeBase, relationship
from sqlalchemy import Integer, Foreignkey, String, Unicode


class Batch(DeclarativeBase):

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
        Foreignkey('project.id'),
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

