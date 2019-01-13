from restfulpy.controllers import ModelRestController

from ..models import Skill


class SkillController(ModelRestController):
    __model__ = Skill