from datetime import datetime

from nanohttp import json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from sqlalchemy import select, func, join

from ..models import Item, Dailyreport, Event, Member, Issue, Project, Phase
from ..validators import update_item_validator, dailyreport_update_validator, \
    estimate_item_validator, dailyreport_create_validator
from ..exceptions import StatusEndDateMustBeGreaterThanStartDate, \
    StatusInvalidDatePeriod


FORM_WHITLELIST_ITEM = [
    'startDate',
    'endDate',
    'estimatedHours',
]
FORM_WHITLELIST_DAILYREPORT = [
    'hours',
    'note',
    'date',
]
VALID_ZONES = [
    'newlyAssigned',
    'needEstimate',
    'upcomingNuggets',
    'inProgressNuggets'
]


FORM_WHITELIST_ITEM_STRING = ', '.join(FORM_WHITLELIST_ITEM)
FORM_WHITELIST_DAILYREPORT_STRING = ', '.join(FORM_WHITLELIST_DAILYREPORT)


class ItemController(ModelRestController):
    __model__ = Item

    def __call__(self, *remaining_path):
        if len(remaining_path) > 1 and remaining_path[1] == 'dailyreports':
            id = int_or_notfound(remaining_path[0])
            item = self._get_item(id)
            return ItemDailyreportController(item=item)(*remaining_path[2:])

        return super().__call__(*remaining_path)

    def _get_item(self, id):
        item = DBSession.query(Item).filter(Item.id == id).one_or_none()
        if item is None:
            raise HTTPNotFound()

        return item

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    def get(self, id):
        id = int_or_notfound(id)
        item = DBSession.query(Item).get(id)
        if not item:
            raise HTTPNotFound()

        return item

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Item.expose
    def list(self):
        member = Member.current()
        is_issue_joined = False
        is_project_joined = False

        lead_phase_subquery = select([Phase.id]) \
            .select_from(join(Item, Phase, Item.phase_id == Phase.id)) \
            .where(Item.estimated_hours.is_(None)) \
            .order_by(Phase.order) \
            .limit(1)

        if member.role == 'admin':
            query = DBSession.query(Item)

        else:
            query = DBSession.query(Item).filter(Item.member_id == member.id)

        if 'zone' in context.query:
            if context.query['zone'] not in VALID_ZONES:
                return []

            if context.query['zone'] == 'newlyAssigned':
                query = query \
                    .filter(Item.phase_id.notin_(lead_phase_subquery)) \
                    .filter(Item.estimated_hours.is_(None))

            if context.query['zone'] == 'needEstimate':
                query = query \
                    .filter(Item.phase_id.in_(lead_phase_subquery)) \
                    .filter(Item.estimated_hours.is_(None))

            elif context.query['zone'] == 'upcomingNuggets':
                query = query \
                    .filter(Item.estimated_hours.isnot(None)) \
                    .filter(Item.start_date > datetime.now())

            elif context.query['zone'] == 'inProgressNuggets':
                query = query \
                    .filter(Item.estimated_hours.isnot(None)) \
                    .filter(Item.start_date < datetime.now())

        # FILTER
        if 'issueBoarding' in context.query:
            value = context.query['issueBoarding']
            query = query.join(Issue, Item.issue_id == Issue.id)
            query = Item._filter_by_column_value(query, Issue.boarding, value)
            is_issue_joined = True

        if 'issueKind' in context.query:
            value = context.query['issueKind']
            if not is_issue_joined:
                query = query.join(Issue, Item.issue_id == Issue.id)
                is_issue_joined = True

            query = Item._filter_by_column_value(query, Issue.kind, value)

        if 'issueTitle' in context.query:
            value = context.query['issueTitle']
            if not is_issue_joined:
                query = query.join(Issue, Item.issue_id == Issue.id)
                is_issue_joined = True

            query = Item._filter_by_column_value(query, Issue.title, value)

        if 'projectTitle' in context.query:
            value = context.query['projectTitle']
            if not is_issue_joined:
                query = query.join(Issue, Item.issue_id == Issue.id)
                is_issue_joined = True

            query = query.join(Project, Project.id == Issue.project_id)
            query = Item._filter_by_column_value(query, Project.title, value)

        # SORT
        sorting_expression = context.query.get('sort', '').strip()
        external_columns = (
            'issueBoarding',
            'issueKind',
            'issueTitle',
            'projectTitle'
        )

        if sorting_expression:

            sorting_columns = {
                c[1:] if c.startswith('-') else c:
                    'desc' if c.startswith('-') else None
                for c in sorting_expression.split(',')
                    if c.replace('-', '') in external_columns
            }

            if 'issueBoarding' in sorting_expression:
                if not is_issue_joined:
                    query = query.join(Issue, Item.issue_id == Issue.id)
                    is_issue_joined = True

                query = Issue._sort_by_key_value(
                    query,
                    column=Issue.boarding,
                    descending=sorting_columns['issueBoarding']
                )

            if 'issueKind' in sorting_expression:
                if not is_issue_joined:
                    query = query.join(Issue, Item.issue_id == Issue.id)
                    is_issue_joined = True

                query = Issue._sort_by_key_value(
                    query,
                    column=Issue.kind,
                    descending=sorting_columns['issueKind']
                )

            if 'issueTitle' in sorting_expression:
                if not is_issue_joined:
                    query = query.join(Issue, Item.issue_id == Issue.id)
                    is_issue_joined = True

                query = Issue._sort_by_key_value(
                    query,
                    column=Issue.title,
                    descending=sorting_columns['issueTitle']
                )

            if 'projectTitle' in sorting_expression:
                if not is_issue_joined:
                    query = query.join(Issue, Item.issue_id == Issue.id)
                    is_issue_joined = True

                if not is_project_joined:
                    query = query.join(Project, Issue.project_id == Project.id)
                    is_project_joined = True

                query = Issue._sort_by_key_value(
                    query,
                    column=Project.title,
                    descending=sorting_columns['projectTitle']
                )

        return query

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            FORM_WHITLELIST_ITEM,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELIST_ITEM_STRING}'
        )
    )
    @estimate_item_validator
    @commit
    def estimate(self, id):
        id = int_or_notfound(id)

        item = DBSession.query(Item).get(id)
        if not item:
            raise HTTPNotFound()

        item.update_from_request()
        if item.start_date > item.end_date:
            raise StatusEndDateMustBeGreaterThanStartDate()

        return item


class ItemDailyreportController(ModelRestController):
    __model__ = Dailyreport

    def __init__(self, item):
        self.item = item

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @commit
    def get(self, id):
        id = int_or_notfound(id)
        dailyreport = DBSession.query(Dailyreport).get(id)
        if dailyreport is None:
            raise HTTPNotFound()

        return dailyreport

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            FORM_WHITLELIST_DAILYREPORT,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELIST_DAILYREPORT_STRING}'
        )
    )
    @dailyreport_update_validator
    @commit
    def update(self, id):
        id = int_or_notfound(id)
        dailyreport = DBSession.query(Dailyreport).get(id)
        if dailyreport is None:
            raise HTTPNotFound()

        dailyreport.update_from_request()
        return dailyreport

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Dailyreport.expose
    @commit
    def list(self):
        return DBSession.query(Dailyreport) \
            .filter(Dailyreport.item_id == self.item.id)

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            FORM_WHITLELIST_DAILYREPORT,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELIST_DAILYREPORT_STRING}'
        )
    )
    @dailyreport_create_validator
    @commit
    def create(self):
        date = context.form.get('date')
        if self.item.end_date < date or date < self.item.start_date:
            raise StatusInvalidDatePeriod()

        dailyreport = Dailyreport(
            note=context.form.get('note'),
            hours=context.form.get('hours'),
            item_id=self.item.id,
            date=date,
        )
        DBSession.add(dailyreport)
        return dailyreport

