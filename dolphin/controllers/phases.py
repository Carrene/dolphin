from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession
from nanohttp import json

from ..models import Phase


class PhaseController(ModelRestController):
    __model__ = Phase


    def __init__(self, workflow):
        self.workflow = workflow

    @json
    @Phase.expose
    def list(self):
        query = DBSession.query(Phase) \
            .filter(Phase.workflow_id == self.workflow.id)
        return query
