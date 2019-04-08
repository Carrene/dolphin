from nanohttp import json, HTTPNotFound, HTTPUnauthorized, context, \
    int_or_notfound, HTTPStatus
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..validators  import phase_validator
from ..models import Phase, Member
from .resource import ResourceController
from ..validators import phase_update_validator
from ..exceptions import HTTPRepetitiveTitle, HTTPSkillNotFound, \
    HTTPRepetitiveOrder


FORM_WHITELIST = [
    'title',
    'order',
    'skillId',
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

    def __init__(self, workflow=None, issue=None):
        self.workflow = workflow
        self.issue = issue

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
        query = DBSession.query(Phase) \
            .filter(Phase.workflow_id == self.workflow.id)
        return query

    @authorize
    @json
    @Phase.expose
    @commit
    def set(self, id):
        id = int_or_notfound(id)

        phase = DBSession.query(Phase).get(id)
        if phase is None:
            raise HTTPNotFound()

        phase.issues.append(self.issue)
        DBSession.add(phase)
        return phase

    @authorize
<<<<<<< HEAD
    @json(form_whitelist=(
        FORM_WHITELIST,
        f'707 Invalid field, only following fields are accepted: '
        f'{FORM_WHITELISTS_STRING}'
    ))
    @phase_update_validator
    @commit
    def update(self, id):
        id = int_or_notfound(id)
        phase = DBSession.query(Phase).get(id)
        if phase is None:
            raise HTTPNotFound()

        is_repetitive_title = DBSession.query(Phase) \
            .filter(
                Phase.title == context.form.get('title'),
                Phase.workflow_id == self.workflow.id
            ) \
            .one_or_none()
        if phase.title != context.form.get('title') \
                and is_repetitive_title is not None:
            raise HTTPRepetitiveTitle()

        is_repetitive_order = DBSession.query(Phase) \
            .filter(
                Phase.order == context.form.get('order'),
                Phase.workflow_id == self.workflow.id
            ) \
            .one_or_none()
        if phase.order != context.form.get('order') \
                and is_repetitive_order is not None:
            raise HTTPRepetitiveOrder()

        skill = DBSession.query(Skill).get(context.form.get('skillId'))
        if skill is None:
            raise HTTPSkillNotFound()

        phase.update_from_request()
        return phase

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    def get(self, id):
        id = int_or_notfound(id)
        phase = DBSession.query(Phase).get(id)
        if phase is None:
            raise HTTPNotFound()

        return phase

    @phase_validator
    @json
    @commit
    def create(self):
        form = context.form
        identity = context.identity
        member = DBSession.query(Member).get(identity.id)
        if member is None:
            raise HTTPSecondaryManagerNotFound()

        phase = Phase()
        phase.update_from_request()
        phase.workflow = self.workflow
        phase.skill_id = form['skill_id']
        DBSession.add(phase)
        return phase

