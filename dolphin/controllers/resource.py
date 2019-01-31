from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Resource, Skill, Phase


class ResourceController(ModelRestController):
    __model__ = Resource

    def __init__(self, phase=None):
        self.phase = phase

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Resource.expose
    def list(self):
        query = DBSession.query(Resource) \
            .join(Skill, Resource.skill_id == Skill.id) \
            .join(Phase, Phase.skill_id == Skill.id) \
            .filter(Skill.id == self.phase.skill_id)
        return query

