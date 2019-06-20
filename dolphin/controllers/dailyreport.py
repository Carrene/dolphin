from restfulpy.controllers import ModelRestController

from ..models import Dailyreport


# The only reason to keep this class is to serve the METADATA verb.
class DailyreportController(ModelRestController):
    __model__ = Dailyreport

