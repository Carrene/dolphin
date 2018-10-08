from nanohttp import Controller, json, text
from restfulpy.controllers import RootController
from restfulpy.authorization import authorize

import dolphin
from .releases import ReleaseController
from .projects import ProjectController
from .managers import ManagerController
from .issues import IssueController
from .items import ItemController
from .tokens import TokenController
from .oauth2 import OAUTHController
from .members import MemberController


class Apiv1(Controller):

    releases = ReleaseController()
    projects = ProjectController()
    managers = ManagerController()
    issues = IssueController()
    items = ItemController()
    tokens = TokenController()
    oauth2 = OAUTHController()
    members = MemberController()

    @json
    def version(self):
        return dict(version=dolphin.__version__)


class Root(RootController):
    apiv1 = Apiv1()

