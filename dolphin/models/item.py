
from sqlalchemy import DateTime, Integer, ForeignKey
from restfulpy.orm import Field, DeclarativeBase, relationship
from restfulpy.orm.mixins import TimestampMixin


class Item(TimestampMixin, DeclarativeBase):
    __tablename__ = 'item'

    stage_id = Field(Integer, ForeignKey('stage.id'))
    issue_id = Field(Integer, ForeignKey('issue.id'))
    resource_id = Field(Integer, ForeignKey('resource.id'))
    id = Field(Integer, primary_key=True)
    end = Field(DateTime)

    resource = relationship('Resource', back_populates='items', protected=True)
    stage = relationship('Stage', back_populates='items', protected=True)

