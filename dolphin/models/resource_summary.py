from restfulpy.orm import Field, PaginationMixin, FilteringMixin, \
    OrderingMixin, BaseModel, MetadataField
from sqlalchemy import Integer, Unicode, select, join, DateTime, func, case
from sqlalchemy.orm import mapper

from . import Phase, Item, Resource, Dailyreport, SkillMember
from .issue_phase import IssuePhase


class AbstractResourceSummaryView(PaginationMixin, OrderingMixin,
                                  FilteringMixin, BaseModel):
    __abstract__ = True
    __table_args__ = {'autoload': True}
    __containig_fields__ = {
        'resource': ('id', 'title'),
        'item': ('start_date', 'end_date', 'estimated_hours', 'id', 'status'),
        'dailyreport': ('hours')
    }

    id = Field('id', Integer, primary_key=True)
    item_id = Field('item_id', Integer)
    title = Field('title', Unicode(100))
    load = Field('load', Unicode())
    start_date = Field('start_date', DateTime)
    end_date = Field('end_date', DateTime)
    estimated_hours = Field('estimated_hours', Integer)
    hours = Field('hours_worked', Integer)
    status = Field('status', Unicode(100))

    @classmethod
    def create_mapped_class(cls, issue_id, phase_id):
        item_cte = select([
            Item.id,
            Item.start_date,
            Item.end_date,
            Item.estimated_hours,
            Item.status,
            Item.member_id,
        ]) \
            .select_from(
                join(
                    Item,
                    IssuePhase,
                    IssuePhase.id == Item.issue_phase_id
                )
            ) \
            .where(IssuePhase.issue_id == issue_id) \
            .where(IssuePhase.phase_id == phase_id) \
            .cte()

        dailyreport_cte = select([
            func.sum(Dailyreport.hours).label('hours_worked'),
            Dailyreport.item_id
        ]).group_by(Dailyreport.item_id).cte()

        query = select([
            Resource.id,
            Resource.title,
            Resource.load.label('load'),
            item_cte.c.id.label('item_id'),
            item_cte.c.start_date,
            item_cte.c.end_date,
            item_cte.c.estimated_hours,
            item_cte.c.status,
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
                     hybrids=False):
        for c in Resource.iter_columns(
            relationships=relationships,
            synonyms=synonyms,
            composites=composites,
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
        ):
            if c.key not in cls.__containig_fields__['item']:
                continue

            column = getattr(cls, c.key, None)
            a = c.key
            if hasattr(c, 'info'):
                column.info.update(c.info)

            yield column

        for c in Dailyreport.iter_columns(
            relationships=relationships,
            synonyms=synonyms,
            composites=composites,
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
        yield MetadataField(
            name='startDate',
            key='start_date',
            label='Start',
            required=False,
            readonly=True,
            protected=False,
        )
        yield MetadataField(
            name='endDate',
            key='end_date',
            label='Target',
            required=False,
            readonly=True,
            protected=False,
        )
        yield MetadataField(
            name='title',
            key='title',
            label='Resource',
            required=False,
            readonly=True,
            protected=False,
        )
        yield MetadataField(
            name='status',
            key='status',
            label='status',
            required=False,
            readonly=True,
            protected=False,
        )

    def to_dict(self):
        # The `load` key is added manually because the `load` attribute is a
        # hybrid property on `Resource` model, so that it isn't included in
        # `Resource.iter_columns` method.
        phase_summary_dict = super().to_dict()
        phase_summary_dict['load'] = self.load
        return phase_summary_dict

