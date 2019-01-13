from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Resource, Skill


class ResourceController(ModelRestController):
    __model__ = Resource

    def __init__(self, phase=None):
        self.phase = phase

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Resource.expose
    def list(self):
        return DBSession.query(Resource) \
            .join(Skill, Resource.id == Skill.resource_id) \
            .filter(Skill.phase_id == self.phase.id)

