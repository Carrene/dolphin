from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..exceptions import HTTPEndDateMustBeGreaterThanStartDate
from ..models import Event
from ..validators import event_add_validator


class EventController(ModelRestController):
    __model__ = Event

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @event_add_validator
    @commit
    def add(self):
        event = Event()
        event.update_from_request()
        if event.start_date > event.end_date:
            raise HTTPEndDateMustBeGreaterThanStartDate()

        DBSession.add(event)
        return event

