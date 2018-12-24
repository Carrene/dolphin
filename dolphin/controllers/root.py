from os.path import abspath, dirname, join

from nanohttp import Controller, json, Static
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
from .tag import TagController
from .files import FileController
from .workflows import WorkflowController


here = abspath(dirname(__file__))
attachment_storage = abspath(join(here, '../..', 'data/assets'))


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
    tags = TagController()
    workflows = WorkflowController()

    @json
    def version(self):
        return dict(version=dolphin.__version__)


class Root(RootController):
    apiv1 = Apiv1()
    assets = Static(attachment_storage)

