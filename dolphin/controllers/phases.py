from nanohttp import json, HTTPNotFound, HTTPUnauthorized, context, \
    int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Phase
from .resource import ResourceController


FORM_WHITELIST = [
    'title',
    'order',
    'specialtyId',
    'description',
]


FORM_WHITELISTS_STRING = ', '.join(FORM_WHITELIST)


class PhaseController(ModelRestController):
    __model__ = Phase

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1:
            if not context.identity:
                raise HTTPUnauthorized()

            phase = self._get_phase(remaining_paths[0])
            if remaining_paths[1] == 'resources':
                return ResourceController(phase=phase)(*remaining_paths[2:])

        return super().__call__(*remaining_paths)

    def _get_phase(self, id):
        id = int_or_notfound(id)

        phase = DBSession.query(Phase).get(id)
        if phase is None:
            raise HTTPNotFound()

        return phase

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    def get(self, id):
        id = int_or_notfound(id)
        phase = DBSession.query(Phase).get(id)
        if phase is None:
            raise HTTPNotFound()

        return phase

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Phase.expose
    def list(self):
        return DBSession.query(Phase)

