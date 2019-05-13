from restfulpy.controllers import ModelRestController

from ..models import Dailyreport


class DailyreportController(ModelRestController):
    __model__ = Dailyreport

