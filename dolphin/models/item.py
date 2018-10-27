from restfulpy.orm import Field, DeclarativeBase, relationship
from restfulpy.orm.mixins import TimestampMixin
from sqlalchemy import DateTime, Integer, ForeignKey, Enum


item_statuses = [
    'in-progress',
    'on-hold',
    'delayed',
    'complete',
]


class Item(TimestampMixin, DeclarativeBase):
    __tablename__ = 'item'

    phase_id = Field(Integer, ForeignKey('phase.id'))
    issue_id = Field(Integer, ForeignKey('issue.id'))
    resource_id = Field(Integer, ForeignKey('member.id'))
    id = Field(Integer, primary_key=True)
    status = Field(
        Enum(*item_statuses, name='item_status'),
        label='Status',
        watermark='Choose a status',
        nullable=True,
        required=False,
    )
    end = Field(
        DateTime,
        label='End',
        pattern=r'^(\d{4})-(0[1-9]|1[012]|[1-9])-(0[1-9]|[12]\d{1}|3[01]|[1-9])$',
        example='2018-02-02',
        watermark='Enter a end time',
        nullable=True,
        required=False,
    )

    resource = relationship('Resource', back_populates='items', protected=True)
    phase = relationship(
        'Phase',
        foreign_keys=[phase_id],
        back_populates='items',
        protected=True
    )
    issue = relationship(
        'Issue',
        foreign_keys=[issue_id],
        back_populates='items',
        protected=True
    )

