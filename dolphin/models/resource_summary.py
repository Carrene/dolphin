from restfulpy.orm import Field, PaginationMixin, FilteringMixin, \
    OrderingMixin, BaseModel, MetadataField
from sqlalchemy import Integer, Unicode, select, join, DateTime, func
from sqlalchemy.orm import mapper

from . import Phase, Item, Resource, Dailyreport, SkillMember


class AbstractResourceSummaryView(PaginationMixin, OrderingMixin,
                                  FilteringMixin, BaseModel):
    __abstract__ = True
    __table_args__ = {'autoload': True}
    __containig_fields__ = {
        'resource': ('id', 'title'),
        'item': ('start_date', 'end_date', 'estimated_hours'),
    }

    id = Field('id', Integer, primary_key=True)
    title = Field('title', Unicode(100))
    load = Field('load', Unicode())
    start_date = Field('start_date', DateTime)
    end_date = Field('end_date', DateTime)
    estimated_hours = Field('estimated_hours', Integer)
    hours = Field('hours_worked', Integer)

    @classmethod
    def create_mapped_class(cls, issue_id, phase_id):
        item_cte = select([Item]) \
            .where(Item.issue_id == issue_id) \
            .where(Item.phase_id == phase_id) \
            .cte()

        dailyreport_cte = select([
            func.max(Dailyreport.hours).label('hours_worked'),
            Dailyreport.item_id
        ]).group_by(Dailyreport.item_id).cte()

        query = select([
            Resource.id,
            Resource.title,
            Resource.load,
            item_cte.c.start_date,
            item_cte.c.end_date,
            item_cte.c.estimated_hours,
            dailyreport_cte.c.hours_worked,
        ]) \
        .select_from(
            join(
                Resource,
                SkillMember,
                SkillMember.member_id == Resource.id,
                isouter=True
            ).join(
                Phase,
                Phase.skill_id == SkillMember.skill_id
            ).join(
                item_cte,
                item_cte.c.member_id == Resource.id,
                isouter=True
            ).join(
                dailyreport_cte,
                dailyreport_cte.c.item_id == item_cte.c.id,
                isouter=True
            )
        ) \
        .where(Phase.id == phase_id) \
        .cte()

        class ResourceSummaryView(cls):
            pass

        mapper(ResourceSummaryView, query.alias())
        return ResourceSummaryView

    @classmethod
    def iter_columns(cls, relationships=False, synonyms=False, composites=False,
                     use_inspection=False, hybrids=False):
        for c in Resource.iter_columns(
            relationships=relationships,
            synonyms=synonyms,
            composites=composites,
            use_inspection=use_inspection
        ):
             if c.key not in cls.__containig_fields__['resource']:
                 continue

             column = getattr(cls, c.key, None)
             if hasattr(c, 'info'):
                 column.info.update(c.info)

             yield column

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

    @classmethod
    def iter_metadata_fields(cls):
        yield from super().iter_metadata_fields()
        yield MetadataField(
            name='hoursWorked',
            key='hours_worked',
            label='Hours Worked',
            readonly=True,
            required=False,
            protected=False,
        )
        yield MetadataField(
            name='load',
            key='load',
            label='Load',
            required=False,
            readonly=True,
            protected=False,
        )

    def to_dict(self):
        a = super().to_dict()
        return a

