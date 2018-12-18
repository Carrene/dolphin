from nanohttp import json, context, HTTPNotFound
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Workflow
from .phases import PhaseController


class WorkflowController(ModelRestController):
    __model__ = Workflow

    def __call__(self, *remaining_paths):
        from pudb import set_trace; set_trace()
        if len(remaining_paths) > 1 and remaining_paths[1] == 'phases':
            workflow = self._get_workflow(remaining_paths[0])
            return PhaseController(workflow)(remaining_paths[1])


    def _get_workflow(self, id):
        workflow = DBSession.query(Workflow) \
            .filter(Workflow.id == id) \
            .one_or_none()
        if workflow is None:
            raise HTTPNotFound()

        return workflow

