from restfulpy.controllers import ModelRestController

from ..models import Group


class GroupController(ModelRestController):
    __model__ = Group