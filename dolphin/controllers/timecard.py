from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..exceptions import StatusEndDateMustBeGreaterThanStartDate
from ..models import Timecard
from ..validators import timecard_create_validator


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
    @json(prevent_form='709 Form Not Allowed')
    @Timecard.expose
    def list(self):
        return DBSession.query(Timecard)

