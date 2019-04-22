from nanohttp import json, context, HTTPNotFound, HTTPForbidden
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController, JsonPatchControllerMixin
from restfulpy.orm import DBSession, commit
from sqlalchemy import and_, exists

from ..exceptions import HTTPAlreadyTagAdded, HTTPAlreadyTagRemoved
from ..models import EventType
from ..validators import event_type_create_validator



class EventTypeController(ModelRestController):
    __model__ = EventType

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @event_type_create_validator
    @commit
    def create(self):
        event_type  = EventType(
            title=context.form.get('title'),
            description=context.form.get('description'),
        )
        DBSession.add(event_type)
        return event_type


