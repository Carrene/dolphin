from nanohttp import json, context, int_or_notfound, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..models import EventType
from ..validators import eventtype_create_validator, eventtype_update_validator
from ..exceptions import HTTPRepetitiveTitle


FORM_WHITELIST = [
    'title',
    'description',
]
FORM_WHITELISTS_STRING = ', '.join(FORM_WHITELIST)


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
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELISTS_STRING}'
        )
    )
    @eventtype_update_validator
    @commit
    def update(self, id):
        id = int_or_notfound(id)
        title = context.form.get('title')
        event_type = DBSession.query(EventType).get(id)
        if event_type is None:
            raise HTTPNotFound()

        is_exist_event_type = DBSession.query(EventType) \
            .filter(
                EventType.title == title,
                EventType.id != id
            ) \
            .one_or_none()
        if is_exist_event_type:
            raise HTTPRepetitiveTitle()

        event_type.update_from_request()
        return event_type

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @EventType.expose
    def list(self):
        return DBSession.query(EventType)

