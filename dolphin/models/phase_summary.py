from datetime import datetime

from restfulpy.orm import Field, PaginationMixin, FilteringMixin, \
    OrderingMixin, BaseModel, MetadataField, DBSession
from sqlalchemy import Integer, Unicode, select, func, join, DateTime, and_
from sqlalchemy.orm import mapper

from . import Phase, Item, Dailyreport, Project, Issue
from .issue_phase import IssuePhase


class AbstractPhaseSummaryView(PaginationMixin, OrderingMixin, FilteringMixin,
                               BaseModel):
    __abstract__ = True
    __table_args__ = {'autoload': True}
    __containig_fields__ = {
        'phase': ('id', 'title'),
        'item': ('issue_id', 'start_date', 'end_date', 'estimated_hours'),
        'dailyreport': ('hours'),
    }

    id = Field('id', Integer, primary_key=True)
    title = Field('title', Unicode(100))
    start_date = Field('start_date', DateTime)
    end_date = Field('end_date', DateTime)
    issue_id = Field('issue_id', Integer)
    estimated_hours = Field('estimated_hours', Integer)
    hours = Field('hours_worked', Integer)

    @classmethod
    def create_mapped_class(cls, issue_id):
        item_cte = select([Item, IssuePhase.issue_id, IssuePhase.phase_id]) \
            .select_from(join(
                Item,
                IssuePhase,
                Item.issue_phase_id == IssuePhase.id
            )) \
            .where(IssuePhase.issue_id == issue_id) \
            .cte()
        workflow_id_subquery = DBSession.query(Project.workflow_id) \
            .join(Issue, Project.id == Issue.project_id) \
            .filter(Issue.id == issue_id) \
            .subquery()

        query = select([
            item_cte.c.issue_id.label('issue_id'),
            Phase.id,
            Phase.title,
            func.min(item_cte.c.start_date).label('start_date'),
            func.max(item_cte.c.end_date).label('end_date'),
            func.sum(item_cte.c.estimated_hours).label('estimated_hours'),
            func.sum(Dailyreport.hours).label('hours_worked'),
        ]) \
        .select_from(
                join(
                    Phase,
                    item_cte,
                    Phase.id == item_cte.c.phase_id,
                    isouter=True
                ).join(
                    Dailyreport,
                    Dailyreport.item_id == item_cte.c.id,
                    isouter=True
                )
        ) \
        .where(Phase.workflow_id.in_(workflow_id_subquery)) \
        .where(Phase.order > 0) \
        .group_by(item_cte.c.issue_id) \
        .group_by(Phase.id) \
        .group_by(Phase.title) \
        .order_by(Phase.order) \
        .cte()

        class PhaseSummaryView(cls):
            pass

        mapper(PhaseSummaryView, query.alias())
        return PhaseSummaryView

    @classmethod
    def iter_columns(cls, relationships=False, synonyms=False, composites=False,
                     use_inspection=False, hybrids=False):
        for c in Item.iter_columns(
            relationships=relationships,
            synonyms=synonyms,
            composites=composites,
            use_inspection=use_inspection
        ):
             if c.key not in cls.__containig_fields__['item']:
                 continue

             column = getattr(cls, c.key, None)
             if hasattr(c, 'info'):
                 column.info.update(c.info)

             yield column

        for c in IssuePhase.iter_columns(
            relationships=relationships,
            synonyms=synonyms,
            composites=composites,
            use_inspection=use_inspection
        ):
             if c.key not in cls.__containig_fields__['item']:
                 continue

             column = getattr(cls, c.key, None)
             if hasattr(c, 'info'):
                 column.info.update(c.info)

             yield column

        for c in Phase.iter_columns(
            relationships=relationships,
            synonyms=synonyms,
            composites=composites,
            use_inspection=use_inspection
        ):
             if c.key not in cls.__containig_fields__['phase']:
                 continue

             column = getattr(cls, c.key, None)
             if hasattr(c, 'info'):
                 column.info.update(c.info)

             yield column

        for c in Dailyreport.iter_columns(
            relationships=relationships,
            synonyms=synonyms,
            composites=composites,
            use_inspection=use_inspection
        ):
             if c.key not in cls.__containig_fields__['dailyreport']:
                 continue

             column = getattr(cls, c.key, None)
             if hasattr(c, 'info'):
                 column.info.update(c.info)

             yield column

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='hours',
            key='hours',
            label='Hours Worked',
            readonly=True,
            required=False,
        )
        yield MetadataField(
            name='startDate',
            key='start_date',
            label='Start',
            readonly=True,
            required=False,
        )
        yield MetadataField(
            name='endDate',
            key='end_date',
            label='Target',
            readonly=True,
            required=False,
        )
        yield MetadataField(
            name='title',
            key='title',
            label='Phase',
            readonly=True,
            required=False,
        )

