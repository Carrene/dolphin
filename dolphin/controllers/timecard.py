from nanohttp import json, context, int_or_notfound, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..exceptions import StatusEndDateMustBeGreaterThanStartDate
from ..models import Timecard
from ..validators import timecard_create_validator, timecard_update_validator


class TimecardController(ModelRestController):
    __model__ = Timecard

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @timecard_create_validator
    @commit
    def create(self):
        time_card = Timecard()
        time_card.update_from_request()
        if time_card.start_date > time_card.end_date:
            raise StatusEndDateMustBeGreaterThanStartDate()

        DBSession.add(time_card)
        return time_card

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @timecard_update_validator
    @commit
    def update(self, id):
        id = int_or_notfound(id)
        timecard = DBSession.query(Timecard).get(id)
        if timecard is None:
            raise HTTPNotFound()

        timecard.update_from_request()
        if timecard.start_date > timecard.end_date:
            raise StatusEndDateMustBeGreaterThanStartDate()

        return timecard

