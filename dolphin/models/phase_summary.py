from datetime import datetime

from restfulpy.orm import Field, PaginationMixin, FilteringMixin, \
    OrderingMixin, BaseModel, MetadataField
from sqlalchemy import Integer, Unicode, select, func, join, DateTime
from sqlalchemy.orm import mapper

from . import Phase, Item


class AbstractPhaseSummaryView(PaginationMixin, OrderingMixin, FilteringMixin,
                               BaseModel):
    __abstract__ = True
    __table_args__ = {'autoload': True}
    __containig_fields__ = ('id')# 'start_date', 'end_date', 'issue_id')

    id = Field(Integer, primary_key=True)
    title = Field(Unicode(100))
    start_date = Field(DateTime, key='start_date')
    end_date = Field(DateTime, key='end_date')
    issue_id = Field(Integer, key='issue_id')

    @classmethod
    def create_mapped_class(cls):
        query = select([
            Phase.id,
            Phase.title,
            func.min(Item.start_date),
            func.max(Item.end_date),
        ]) \
        .select_from(
            join(Phase, Item, Phase.id == Item.phase_id, isouter=True)
        ) \
        .group_by(Item.issue_id) \
        .group_by(Phase.id) \
        .group_by(Phase.title) \
        .cte()

        class PhaseSummaryView(cls):
            pass

        mapper(PhaseSummaryView, query.alias())
        return PhaseSummaryView

    @classmethod
    def iter_columns(cls, relationships=True, synonyms=True, composites=True,
                     use_inspection=False, hybrids=True):
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


PhaseSummaryView = AbstractPhaseSummaryView.create_mapped_class()

