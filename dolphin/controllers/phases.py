from restfulpy.controllers import ModelRestController
from nanohttp import json

from ..models import Phase


class PhaseController(ModelRestController):
    __model__ = Phase


    def __init__(self, workflow):
        self.workflow = workflow

    @json
    def list(self):
        from pudb import set_trace; set_trace()
        return 1
