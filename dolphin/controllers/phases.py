from nanohttp import json, HTTPNotFound, HTTPUnauthorized, context, \
    int_or_notfound, HTTPStatus
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..validators  import phase_validator
from ..models import Phase, Member, Workflow, Skill
from .resource import ResourceController
from ..validators import phase_update_validator
from ..exceptions import StatusRepetitiveTitle, StatusSkillNotFound, \
    StatusRepetitiveOrder


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
    @Phase.expose
    def list(self):
        return DBSession.query(Phase)

