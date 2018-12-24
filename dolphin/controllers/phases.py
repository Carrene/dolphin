from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from restfulpy.authorization import authorize
from nanohttp import json, HTTPNotFound

from ..models import Phase, Workflow, Item


class PhaseController(ModelRestController):
    __model__ = Phase

    def __init__(self, workflow=None, issue=None):
        self.workflow = workflow
        self.issue = issue

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
        phase = DBSession.query(Phase) \
            .filter(Phase.id == id) \
            .one_or_none()
        if phase is None:
            raise HTTPNotFound()

        phase.issues.append(self.issue)
        DBSession.add(phase)

        return phase
