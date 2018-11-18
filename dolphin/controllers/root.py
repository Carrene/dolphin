from nanohttp import Controller, json
from restfulpy.controllers import RootController

import dolphin
from .issues import IssueController
from .items import ItemController
from .members import MemberController
from .oauth2 import OAUTHController
from .projects import ContainerController
from .releases import ReleaseController
from .tokens import TokenController


class Apiv1(Controller):

    releases = ReleaseController()
    projects = ContainerController()
    members = MemberController()
    issues = IssueController()
    items = ItemController()
    tokens = TokenController()
    oauth2 = OAUTHController()

    @json
    def version(self):
        return dict(version=dolphin.__version__)


class Root(RootController):
    apiv1 = Apiv1()

