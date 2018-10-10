from restfulpy.orm import Field, relationship, SoftDeleteMixin, \
    ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin
from sqlalchemy import Integer, ForeignKey, Enum, select, func
from sqlalchemy.orm import column_property

from .issue import Issue
from .subscribable import Subscribable


project_statuses = [
    'active',
    'on-hold',
    'queued',
    'done',
]


class Project(ModifiedMixin, OrderingMixin, FilteringMixin, PaginationMixin,
              SoftDeleteMixin, Subscribable):

    __tablename__ = 'project'
    __mapper_args__ = {'polymorphic_identity': __tablename__}

    _boarding = ['on-time', 'delayed', 'at-risk']

    id = Field(Integer, ForeignKey('subscribable.id'), primary_key=True)
    release_id = Field(Integer, ForeignKey('release.id'), nullable=True)
    manager_id = Field(Integer, ForeignKey('member.id'))
    group_id = Field(Integer, ForeignKey('group.id'), nullable=True)
    room_id = Field(Integer)

    status = Field(
        Enum(*project_statuses, name='project_status'),
        default='queued'
    )

    manager = relationship(
        'Manager',
        foreign_keys=[manager_id],
        back_populates='projects',
        protected=True
    )
    phases = relationship(
        'Phase',
        back_populates='project',
        protected=True
    )
    release = relationship(
        'Release',
        foreign_keys=[release_id],
        back_populates='projects',
        protected=True
    )
    issues = relationship(
        'Issue',
        primaryjoin=id == Issue.project_id,
        back_populates='project',
        protected=True
    )
    group = relationship(
        'Group',
        back_populates='projects',
        protected=True
    )

    due_date = column_property(
        select([func.max(Issue.due_date)]).\
            where(Issue.project_id == id).\
            correlate_except(Issue)
    )

    @property
    def boardings(self):
        if not self.issues:
            return None

        for issue in self.issues:
            if issue.due_date > self.release.due_date:
                return self._boarding[2]

            if issue.boardings == 'delayed':
                return self._boarding[1]

            if self.status != 'active':
                return None

        return self._boarding[0]

    def to_dict(self):
        project_dict = super().to_dict()
        project_dict['boarding'] = self.boardings
        project_dict['dueDate'] = self.due_date
        return project_dict

