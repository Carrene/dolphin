from nanohttp import json, context, int_or_notfound, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..models import TimeCard
from ..validators import timecard_create_validator
from ..exceptions import StatusEndDateMustBeGreaterThanStartDate


class TimeCardController(ModelRestController):
    __model__ = TimeCard

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @timecard_create_validator
    @commit
    def create(self):
        time_card = TimeCard()
        time_card.update_from_request()
        if time_card.start_date > time_card.end_date:
            raise StatusEndDateMustBeGreaterThanStartDate()

        DBSession.add(time_card)
        return time_card

