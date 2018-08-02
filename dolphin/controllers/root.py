from nanohttp import Controller, json, text
from restfulpy.controllers import RootController

import dolphin
from .releases import ReleaseController
from .projects import ProjectController
from .managers import ManagerController

class Apiv1(Controller):

    releases = ReleaseController()
    projects = ProjectController()
    managers = ManagerController()

    @json
    def version(self):
        return dict(version=dolphin.__version__)


class Root(RootController):
    apiv1 = Apiv1()

