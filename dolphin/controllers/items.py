from datetime import datetime

from nanohttp import json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from sqlalchemy import select, func

from ..models import Item, Dailyreport, Event, Member
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

        if member.role == 'admin':
            query = DBSession.query(Item)

        else:
            query = DBSession.query(Item).filter(Item.member_id == member.id)

        if 'zone' in context.query:
            if context.query['zone'] not in VALID_ZONES:
                return []

            if context.query['zone'] == 'newlyAssigned':
                query = query.filter(Item.status != 'in-progress')

            if context.query['zone'] == 'needEstimate':
                query = query.filter(Item.status == 'in-progress') \
                    .filter(Item.estimated_hours.is_(None))

            elif context.query['zone'] == 'upcomingNuggets':
                query = query.filter(Item.status == 'in-progress') \
                    .filter(Item.start_date > datetime.now())

            elif context.query['zone'] == 'inProgressNuggets':
                query = query.filter(Item.status == 'in-progress') \
                    .filter(Item.start_date < datetime.now())

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
        date = datetime.strptime(
            context.form.get('date'),
            '%Y-%m-%dT%H:%M:%S.%f'
        )
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

