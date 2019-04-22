from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..models import EventType
from ..validators import event_type_create_validator


class EventTypeController(ModelRestController):
    __model__ = EventType

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @event_type_create_validator
    @commit
    def create(self):
        event_type = EventType(
            title=context.form.get('title'),
            description=context.form.get('description'),
        )
        DBSession.add(event_type)
        return event_type

