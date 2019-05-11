from nanohttp import json, context, HTTPNotFound, int_or_notfound, \
    HTTPStatus, HTTPUnauthorized
from restfulpy.controllers import ModelRestController
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession, commit

from ..models import Workflow, Phase, Skill, Member
from ..validators import workflow_create_validator, \
    workflow_update_validator,phase_update_validator, phase_validator
from ..exceptions import StatusRepetitiveTitle, StatusSkillNotFound, \
    StatusRepetitiveOrder


class WorkflowController(ModelRestController):
    __model__ = Workflow

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1 and remaining_paths[1] == 'phases':
            workflow = self._get_workflow(remaining_paths[0])
            return WorkflowPhaseController(workflow)(*remaining_paths[2:])

        return super().__call__(*remaining_paths)

    def _get_workflow(self, id):
        workflow = DBSession.query(Workflow) \
            .filter(Workflow.id == id) \
            .one_or_none()
        if workflow is None:
            raise HTTPNotFound()

        return workflow

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Workflow.expose
    def list(self):
        query = DBSession.query(Workflow)
        return query

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @workflow_create_validator
    @commit
    def create(self):
        workflow = Workflow(
            title=context.form.get('title'),
            description=context.form.get('description'),
        )
        DBSession.add(workflow)
        return workflow

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    def get(self, id):
        id = int_or_notfound(id)
        workflow = DBSession.query(Workflow).get(id)
        if workflow is None:
            raise HTTPNotFound()

        return workflow

    @authorize
    @json(
        prevent_empty_form='708 Empty Form',
        form_whitelist=(
            ['title', 'description'],
            f'707 Invalid field, only following fields are accepted: '
            f'title, description'
        )
    )
    @workflow_update_validator
    @commit
    def update(self, id):
        form = context.form
        id = int_or_notfound(id)

        workflow = DBSession.query(Workflow).get(id)
        if not workflow:
            raise HTTPNotFound()

        if 'title' in form and DBSession.query(Workflow).filter(
            Workflow.id != id,
            Workflow.title == form['title']
        ).one_or_none():
            raise HTTPStatus(f'600 Repetitive Title')

        workflow.update_from_request()
        return workflow


FORM_WHITELIST = [
    'title',
    'order',
    'skillId',
    'description',
]


FORM_WHITELISTS_STRING = ', '.join(FORM_WHITELIST)


class WorkflowPhaseController(ModelRestController):
    __model__ = Phase

    def __init__(self, workflow):
        self.workflow = workflow

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Phase.expose
    def list(self):
        return DBSession.query(Phase) \
            .filter(Phase.workflow_id == self.workflow.id)

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
    @json(form_whitelist=(
        FORM_WHITELIST,
        f'707 Invalid field, only following fields are accepted: '
        f'{FORM_WHITELISTS_STRING}'
    ))
    @phase_update_validator
    @commit
    def update(self, id):
        id = int_or_notfound(id)
        form = context.form
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
            raise StatusRepetitiveTitle()

        is_repetitive_order = DBSession.query(Phase) \
            .filter(
                Phase.order == context.form.get('order'),
                Phase.workflow_id == self.workflow.id
            ) \
            .one_or_none()
        if phase.order != context.form.get('order') \
                and is_repetitive_order is not None:
            raise StatusRepetitiveOrder()

        if 'skillId' in form and not DBSession.query(Skill) \
                .filter(Skill.id == form.get('skillId')) \
                .one_or_none():
            raise StatusSkillNotFound()

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

    @authorize
    @phase_validator
    @json
    @commit
    def create(self):
        form = context.form
        self._check_title_repetition(
            workflow=self.workflow,
            title=form['title']
        )
        self._check_order_repetition(
            workflow=self.workflow,
            order=form['order'],
        )
        phase = Phase()
        phase.update_from_request()
        phase.workflow = self.workflow
        phase.skill_id = form['skillId']
        DBSession.add(phase)
        return phase

    def _check_title_repetition(self, workflow, title):
        phase = DBSession.query(Phase) \
            .filter(Phase.title == title, Phase.workflow_id == workflow.id) \
            .one_or_none()
        if phase is not None:
            raise HTTPStatus('600 Repetitive Title')

    def _check_order_repetition(self, workflow, order):
        phase = DBSession.query(Phase) \
            .filter(Phase.order == order, Phase.workflow_id == workflow.id) \
            .one_or_none()
        if phase is not None:
            raise HTTPStatus('615 Repetitive Order')

