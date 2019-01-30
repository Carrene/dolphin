
from restfulpy.orm import Field, DeclarativeBase, relationship
from restfulpy.orm.mixins import TimestampMixin
from sqlalchemy import Integer, ForeignKey, UniqueConstraint


class Item(TimestampMixin, DeclarativeBase):
    __tablename__ = 'item'

    id = Field(Integer, primary_key=True)

    phase_id = Field(Integer, ForeignKey('phase.id'))
    issue_id = Field(Integer, ForeignKey('issue.id'))
    member_id = Field(Integer, ForeignKey('member.id'))

    issues = relationship(
        'Issue',
        foreign_keys=issue_id,
        back_populates='items'
    )

    UniqueConstraint(phase_id, issue_id, member_id)
