
from sqlalchemy import DateTime, Integer, ForeignKey, Enum
from restfulpy.orm import Field, DeclarativeBase, relationship
from restfulpy.orm.mixins import TimestampMixin


item_statuses = [
    'in-progress',
    'on-hold',
    'delayed',
    'complete',
]


class Item(TimestampMixin, DeclarativeBase):
    __tablename__ = 'item'

    stage_id = Field(Integer, ForeignKey('stage.id'))
    issue_id = Field(Integer, ForeignKey('issue.id'))
    resource_id = Field(Integer, ForeignKey('resource.id'))
    id = Field(Integer, primary_key=True)
    status = Field(
        Enum(*item_statuses, name='item_status'),
        nullable=True
    )
    end = Field(DateTime)

    resource = relationship('Resource', back_populates='items', protected=True)
    stage = relationship(
        'Stage',
        foreign_keys=[stage_id],
        back_populates='items',
        protected=True
    )
    issue = relationship(
        'Issue',
        foreign_keys=[issue_id],
        back_populates='items',
        protected=True
    )

