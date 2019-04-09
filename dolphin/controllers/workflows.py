from nanohttp import json, context, HTTPNotFound, int_or_notfound
from restfulpy.controllers import ModelRestController
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession, commit

from ..models import Workflow
from .phases import PhaseController
from ..validators import workflow_create_validator


class WorkflowController(ModelRestController):
    __model__ = Workflow

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1 and remaining_paths[1] == 'phases':
            workflow = self._get_workflow(remaining_paths[0])
            return PhaseController(workflow)(*remaining_paths[2:])

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

