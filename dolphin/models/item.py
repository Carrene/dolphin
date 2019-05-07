from restfulpy.orm import Field, DeclarativeBase, relationship
from restfulpy.orm.mixins import TimestampMixin, OrderingMixin, \
    FilteringMixin, PaginationMixin
from sqlalchemy import Integer, ForeignKey, UniqueConstraint


class Item(TimestampMixin, OrderingMixin, FilteringMixin, PaginationMixin,
           DeclarativeBase):
    __tablename__ = 'item'

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

    phase_id = Field(Integer, ForeignKey('phase.id'))
    issue_id = Field(Integer, ForeignKey('issue.id'))
    member_id = Field(Integer, ForeignKey('member.id'))

    issues = relationship(
        'Issue',
        foreign_keys=issue_id,
        back_populates='items'
    )

    UniqueConstraint(phase_id, issue_id, member_id)
