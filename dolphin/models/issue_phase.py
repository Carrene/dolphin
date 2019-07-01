from restfulpy.orm import Field, DeclarativeBase, relationship
from sqlalchemy import Integer, ForeignKey, select, case
from sqlalchemy.orm import column_property
from sqlalchemy.sql.expression import any_, all_

from .item import Item


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
        protected=True,
    )
    issue = relationship(
        'Issue',
        foreign_keys=issue_id,
        back_populates='issue_phases',
        protected=True,
    )
    phase = relationship(
        'Phase',
        foreign_keys=phase_id,
        back_populates='issue_phases',
        protected=True,
    )
    status = column_property(
        case([
            (
                any_(
                    select([Item.status])
                    .where(
                        Item.issue_phase_id == id
                    ).correlate_except(Item)
                ) == 'in-progress',
                'in-progress'
            ),
            (
                all_(
                    select([Item.status])
                    .where(
                        Item.issue_phase_id == id
                    ).correlate_except(Item)
                ) == 'complete',
                'complete'
            ),

        ], else_='to-do').label('status'),
        deferred=True
    )

