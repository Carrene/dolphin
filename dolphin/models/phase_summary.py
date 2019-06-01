from datetime import datetime

from restfulpy.orm import Field, PaginationMixin, FilteringMixin, \
    OrderingMixin, BaseModel, MetadataField
from sqlalchemy import Integer, Unicode, select, func, join, DateTime, and_
from sqlalchemy.orm import mapper

from . import Phase, Item, Dailyreport


class AbstractPhaseSummaryView(PaginationMixin, OrderingMixin, FilteringMixin,
                               BaseModel):
    __abstract__ = True
    __table_args__ = {'autoload': True}
    __containig_fields__ = (
        'id',
        'title',
        'issue_id',
        'workflow_id',
        'start_date',
        'end_date',
#        'hours',
    )

    id = Field('id', Integer, primary_key=True)
    title = Field('title', Unicode(100))
    start_date = Field('start_date', DateTime)
    end_date = Field('end_date', DateTime)
    issue_id = Field('issue_id', Integer)
    workflow_id = Field('workflow_id', Integer)
#    hours = Field('hours', Integer)

    @classmethod
    def create_mapped_class(cls):
        query = select([
            Item.issue_id,
            Phase.id,
            Phase.title,
            Phase.workflow_id,
            func.min(Item.start_date).label('start_date'),
            func.max(Item.end_date).label('end_date'),
            func.max(Dailyreport.hours).label('hours')
        ]) \
        .select_from(
                join(Phase, Item, Phase.id == Item.phase_id, isouter=True),
        ) \
        .group_by(Item.issue_id) \
        .group_by(Phase.id) \
        .group_by(Phase.title) \
        .group_by(Phase.workflow_id) \
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
             if c.key not in cls.__containig_fields__:
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
             if c.key not in cls.__containig_fields__:
                 continue

             column = getattr(cls, c.key, None)
             if hasattr(c, 'info'):
                 column.info.update(c.info)

             yield column

#        for c in Dailyreport.iter_columns(
#            relationships=relationships,
#            synonyms=synonyms,
#            composites=composites,
#            use_inspection=use_inspection
#        ):
#             if c.key not in cls.__containig_fields__:
#                 continue

             column = getattr(cls, c.key, None)
             if hasattr(c, 'info'):
                 column.info.update(c.info)

             yield column


PhaseSummaryView = AbstractPhaseSummaryView.create_mapped_class()

