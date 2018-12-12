from nanohttp import Controller, json
from restfulpy.controllers import RootController

import dolphin
from .issues import IssueController
from .items import ItemController
from .members import MemberController
from .oauth2 import OAUTHController
from .projects import ProjectController
from .releases import ReleaseController
from .tokens import TokenController
from .organization import OrganizationController, OrganizationMemberController
from .invitation import InvitationController


class Apiv1(Controller):

    releases = ReleaseController()
    projects = ProjectController()
    members = MemberController()
    issues = IssueController()
    items = ItemController()
    tokens = TokenController()
    oauth2 = OAUTHController()
    organizations = OrganizationController()
    organizationmembers = OrganizationMemberController()
    invitations = InvitationController()

    @json
    def version(self):
        return dict(version=dolphin.__version__)


class Root(RootController):
    apiv1 = Apiv1()

