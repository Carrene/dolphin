from restfulpy.orm import Field, DeclarativeBase, relationship
from sqlalchemy import Integer, ForeignKey, Enum


issue_phase_statuses = [
    'to-do',
    'in-progress',
    'complete',
]


class IssuePhase(DeclarativeBase):
    __tablename__ = 'issue_phase'

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
    status = Field(
        Enum(*issue_phase_statuses, name='issue_phase_status'),
        python_type=str,
        label='Status',
        protected=True,
        not_none=True,
        required=False,
        default='to-do',
        example='Lorem ipsum',
        message='Lorem ipsum',
        watermark='Lorem ipsum',
    )
    phase_id = Field(
        Integer,
        ForeignKey('phase.id'),
        python_type=int,
        nullable=False,
        watermark='Choose a phase',
        label='Phase',
        not_none=True,
        required=True,
        example='Lorem Ipsum',
    )
    issue_id = Field(
        Integer,
        ForeignKey('issue.id'),
        python_type=int,
        nullable=False,
        watermark='Choose an issue',
        label='Issue',
        not_none=True,
        required=True,
        example='Lorem Ipsum',
    )
    items = relationship(
        'Item',
        back_populates='issue_phase',
        protected=False,
    )
    issue = relationship(
        'Issue',
        foreign_keys=issue_id,
        back_populates='issue_phases',
        protected=False,
    )
    phase = relationship(
        'Phase',
        foreign_keys=phase_id,
        back_populates='issue_phases',
        protected=False,
    )

