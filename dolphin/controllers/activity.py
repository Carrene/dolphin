from restfulpy.controllers import ModelRestController

from ..models import Activity


class ActivityController(ModelRestController):
    __model__ = Activity