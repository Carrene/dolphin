from datetime import datetime

from nanohttp import json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from sqlalchemy import select, func

from ..models import Item, Dailyreport, Event, Member
from ..validators import update_item_validator, dailyreport_update_validator


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
        resource = Member.current()
        query = DBSession.query(Item).filter(Item.member_id == resource.id)
        active_item_cte = select([func.max(Item.id).label('max_item_id')]) \
            .group_by(Item.issue_id) \
            .cte()

        if 'zone' in context.query:
            if context.query['zone'] == 'needEstimate':
                query = query.filter(Item.id == active_item_cte.c.max_item_id) \
                    .filter(Item.estimated_hours.is_(None))

            elif context.query['zone'] == 'upcomingNuggets':
                query = query.filter(Item.id == active_item_cte.c.max_item_id) \
                    .filter(Item.start_date > datetime.now())

            elif context.query['zone'] == 'inProcessNuggets':
                query = query.filter(Item.id == active_item_cte.c.max_item_id) \
                    .filter(Item.start_date < datetime.now())

        return query


class ItemDailyreportController(ModelRestController):
    __model__ = Dailyreport

    def __init__(self, item):
        self.item = item

    def _create_dailyreport_if_needed(self):
        if Event.isworkingday(DBSession):
            is_dailyreport_exists = DBSession.query(Dailyreport) \
                .filter(
                    Dailyreport.date == datetime.now().date(),
                    Dailyreport.item_id == self.item.id
                ) \
                .one_or_none()

            if not is_dailyreport_exists:
                dailyreport = Dailyreport(
                    date=datetime.now().date(),
                    item_id=self.item.id,
                )
                DBSession.add(dailyreport)
                return dailyreport

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @commit
    def get(self, id):
        id = int_or_notfound(id)
        self._create_dailyreport_if_needed()
        dailyreport = DBSession.query(Dailyreport).get(id)
        if dailyreport is None:
            raise HTTPNotFound()

        return dailyreport

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            ['hours', 'note'],
            '707 Invalid field, only following fields are accepted: hours, note'
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
        self._create_dailyreport_if_needed()
        return DBSession.query(Dailyreport)

