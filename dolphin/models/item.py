from datetime import datetime

from restfulpy.orm import Field, DeclarativeBase
from restfulpy.orm.mixins import TimestampMixin
from sqlalchemy import DateTime, Integer, ForeignKey


class Item(TimestampMixin, DeclarativeBase):
    __tablename__ = 'item'

    phase_id = Field(Integer, ForeignKey('phase.id'), primary_key=True)
    issue_id = Field(Integer, ForeignKey('issue.id'), primary_key=True)
    member_id = Field(Integer, ForeignKey('member.id'), nullable=True)

    id = Field(Integer, primary_key=True)

