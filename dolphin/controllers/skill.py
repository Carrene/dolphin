from restfulpy.controllers import ModelRestController

from ..models.skill import Skill


class SkillController(ModelRestController):
    __model__ = Skill