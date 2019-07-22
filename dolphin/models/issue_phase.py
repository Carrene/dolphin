from restfulpy.orm import Field, DeclarativeBase, relationship
from sqlalchemy import Integer, ForeignKey, select, case, func, join
from sqlalchemy.orm import column_property
from sqlalchemy.sql.expression import any_, all_

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
    status = column_property(
        case([
            (
                any_(
                    select([Item.status])
                    .where(Item.issue_phase_id == id)
                    .correlate_except(Item)
                ) == 'in-progress',
                'in-progress'
            ),
            (
                all_(
                    select([Item.status])
                    .where(Item.issue_phase_id == id)
                    .correlate_except(Item)
                ) == 'complete',
                'complete'
            ),
        ], else_='to-do').label('status'),
        deferred=True
    )

    _maximum_end_date = select([func.max(Item.end_date)]) \
        .where(Item.issue_phase_id == id) \
        .as_scalar()

    _minimum_start_date = select([func.min(Item.start_date)]) \
        .where(Item.issue_phase_id == id) \
        .as_scalar()

    _total_estimated_hours = select([func.sum(Item.estimated_hours)]) \
        .where(Item.issue_phase_id == id) \
        .as_scalar()

    _total_estimated_hours = select([func.sum(Item.estimated_hours)]) \
        .where(Item.issue_phase_id == id) \
        .as_scalar()

    _total_hours_worked = select([func.sum(Dailyreport.hours)]) \
        .select_from(
            join(Item, Dailyreport, Item.id == Dailyreport.item_id, isouter=True)
        ) \
        .where(Item.issue_phase_id == id) \
        .as_scalar()

    mojo_remaining_hours = column_property(
        _total_estimated_hours - _total_hours_worked
    )

    mojo_progress = column_property(
        select([
            (func.sum(Dailyreport.hours) / func.sum(Item.estimated_hours)) * 100
        ]) \
        .select_from(
            join(Item, Dailyreport, Item.id == Dailyreport.item_id, isouter=True)
        ) \
        .where(Item.issue_phase_id == id) \
        .as_scalar()
    )

    _total_days_length = column_property(
        select([
            func.sum(
                func.date_part('days', Item.end_date - Item.start_date) + 1
            )
        ]) \
        .where(Item.issue_phase_id == id) \
        .as_scalar()
    )

    _days_left_to_estimate = column_property(
        select([func.sum(Item._days_left_to_estimate)]) \
        .where(Item.issue_phase_id == id) \
        .as_scalar()
    )

    mojo_boarding = column_property(
        case([
            (
                mojo_remaining_hours > _days_left_to_estimate * (
                    _total_hours_worked
                ),
                'at-risk'
            ),
            (
                mojo_remaining_hours > _days_left_to_estimate * (
                    _total_estimated_hours / _total_days_length
                ),
                'delayed'
            ),
        ], else_='on-time').label('mojo_boarding'),
        deferred=True
    )

