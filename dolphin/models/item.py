
from sqlalchemy import DateTime, Integer, ForeignKey
from restfulpy.orm import Field, DeclarativeBase
from restfulpy.orm.mixins import TimestampMixin


class Item(TimestampMixin, DeclarativeBase):
    __tablename__ = 'item'

    stage_id = Field(Integer, ForeignKey('stage.id'))
    task_id = Field(Integer, ForeignKey('task.id'))
    resource_id = Field(Integer, ForeignKey('resource.id'))
    id = Field(Integer, primary_key=True)
    end = Field(DateTime)

