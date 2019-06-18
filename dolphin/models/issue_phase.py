from restfulpy.orm import Field, DeclarativeBase, relationship
from sqlalchemy import Integer, ForeignKey, Enum, join, select, func, case, \
    text
from sqlalchemy.orm import column_property
from sqlalchemy.sql.expression import any_, all_, and_
from sqlalchemy.ext.hybrid import hybrid_property

from .item import Item
from .dailyreport import Dailyreport


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

    @hybrid_property
    def status(self):
        complete_count = 0
        for item in self.items:
            if item.status == 'in-progress':
                return 'in-progress'

            if item.status == 'complete':
                complete_count = complete_count + 1

        if len(self.items) == complete_count:
            return 'complete'

        return 'to-do'

    @status.expression
    def status(cls):
        return case([
            (
                func.count(
                    Item.__table__.select(Item.id)
                    .where(and_(
                        Item.status == 'to-do',
                        Item.issue_phase_id == cls.id
                    ))
                ) == \
                func.count(
                    Item.__table__.select(Item.id)
                    .where(Item.issue_phase_id == cls.id)
                ),
                'to-do'
            ),
            (
                func.count(
                    Item.__table__.select(Item.id)
                    .where(and_(
                        Item.status == 'complete',
                        Item.issue_phase_id == cls.id
                    ))
                ) == \
                func.count(
                    Item.__table__.select(Item.id)
                    .where(Item.issue_phase_id == cls.id)
                ),
                'complete'
            ),
        ], else_='in-progress')

