<<<<<<< HEAD
from nanohttp import json, HTTPNotFound, int_or_notfound
=======
from nanohttp import json, HTTPNotFound, int_or_notfound, context
>>>>>>> Implemented the update method on the event controller, closes #724
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from sqlalchemy import exists

from ..exceptions import HTTPEndDateMustBeGreaterThanStartDate, \
    HTTPRepetitiveTitle
from ..models import Event
from ..validators import event_add_validator, event_update_validator


FORM_WHITELIST = [
    'title',
    'description',
    'startDate',
    'endDate',
    'eventTypeId',
]


FORM_WHITELISTS_STRING = ', '.join(FORM_WHITELIST)


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

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    def get(self, id):
        id = int_or_notfound(id)
        event = DBSession.query(Event).get(id)
        if event is None:
            raise HTTPNotFound()

        return event

    @Event.expose
    def list(self):
        return DBSession.query(Event)

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELISTS_STRING}'
        )
    )
    @event_update_validator
    @commit
    def update(self, id):
        id = int_or_notfound(id)
        event = DBSession.query(Event).get(id)
        if event is None:
            raise HTTPNotFound()

        if event.title != context.form.get('title'):
            is_title_already_exist = DBSession.query(
                exists().where(Event.title == context.form.get('title'))
            ).scalar()
            if is_title_already_exist:
                raise HTTPRepetitiveTitle()

        event.update_from_request()
        if event.start_date > event.end_date:
            raise HTTPEndDateMustBeGreaterThanStartDate()

        return event

