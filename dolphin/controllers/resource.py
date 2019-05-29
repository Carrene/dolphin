from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Resource, Phase, SkillMember


class ResourceController(ModelRestController):
    __model__ = Resource

    def __init__(self, phase=None):
        self.phase = phase

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Resource.expose
    def list(self):
        query = DBSession.query(Resource) \
            .join(SkillMember, SkillMember.member_id == Resource.id) \
            .join(Phase, Phase.skill_id == SkillMember.skill_id) \
            .filter(Phase.id == self.phase.id)
        return query

