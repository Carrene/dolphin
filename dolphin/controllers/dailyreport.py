from datetime import datetime

from nanohttp import json, int_or_notfound, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..exceptions import StatusEndDateMustBeGreaterThanStartDate
from ..models import Dailyreport
from ..validators import dailyreport_create_validator, \
    dailyreport_update_validator


class DailyreportController(ModelRestController):
    __model__ = Dailyreport

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            ['hours', 'note', 'itemId'],
            '707 Invalid field, only following fields are accepted: ' \
            'hours, note and itemId'
        )
    )
    @dailyreport_create_validator
    @commit
    def create(self):
        dailyreport = Dailyreport()
        dailyreport.update_from_request()
        dailyreport.date = datetime.now().date()
        DBSession.add(dailyreport)
        return dailyreport

    @authorize
    @json(prevent_form='709 Form Not Allowed')
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
    def list(self):
        return DBSession.query(Dailyreport)

