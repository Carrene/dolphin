
from restfulpy.orm import Field, DeclarativeBase, relationship
from restfulpy.orm.mixins import TimestampMixin
from sqlalchemy import Integer, ForeignKey


class Item(TimestampMixin, DeclarativeBase):
    __tablename__ = 'item'

    phase_id = Field(Integer, ForeignKey('phase.id'), primary_key=True)
    issue_id = Field(Integer, ForeignKey('issue.id'), primary_key=True)
    member_id = Field(Integer, ForeignKey('member.id'), primary_key=True)

    issues = relationship(
        'Issue',
        foreign_keys=issue_id,
        back_populates='items'
    )
