from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession
from restfulpy.authorization import authorize
from nanohttp import json

from ..models import Phase


class PhaseController(ModelRestController):
    __model__ = Phase


    def __init__(self, workflow):
        self.workflow = workflow

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Phase.expose
    def list(self):
        query = DBSession.query(Phase) \
            .filter(Phase.workflow_id == self.workflow.id)
        return query

