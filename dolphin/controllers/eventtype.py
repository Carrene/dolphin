from nanohttp import json, context, int_or_notfound, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..models import EventType
from ..validators import eventtype_create_validator


class EventTypeController(ModelRestController):
    __model__ = EventType

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @eventtype_create_validator
    @commit
    def create(self):
        event_type = EventType(
            title=context.form.get('title'),
            description=context.form.get('description'),
        )
        DBSession.add(event_type)
        return event_type

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    def get(self, id):
        id = int_or_notfound(id)
        event_type = DBSession.query(EventType).get(id)
        if event_type is None:
            raise HTTPNotFound()

        return event_type

