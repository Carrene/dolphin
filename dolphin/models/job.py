from restfulpy.mule import MuleTask
from restfulpy.orm import Field, relationship, OrderingMixin, DeclarativeBase
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm.session import object_session
from sqlalchemy.sql import select, update

from .issue import Issue


class Job(MuleTask, OrderingMixin, DeclarativeBase):
    __tablename__ = 'job'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    id = Field(
        Integer,
        ForeignKey('mule_task.id'),
        primary_key=True,
        readonly=True,
        not_none=True,
        required=False,
        label='ID',
        minimum=1,
        example=1,
        protected=False,
    )
    issue_id = Field(
        Integer,
        ForeignKey('issue.id'),
        readonly=True,
        nullable=True,
    )

    def do_(self, context):
        pass
