from os.path import abspath, dirname, join

from nanohttp import json, Static
from restfulpy.controllers import RootController, RestController, \
    JsonPatchControllerMixin

import dolphin
from .issues import IssueController
from .items import ItemController
from .members import MemberController
from .oauth2 import OAUTHController
from .projects import ProjectController
from .releases import ReleaseController
from .tokens import TokenController
from .organization import OrganizationController
from .invitation import InvitationController
from .tag import TagController
from .workflows import WorkflowController
from .phases import PhaseController
from .draft_issue import DraftIssueController
from .files import FileController
from .resource import ResourceController
from .skill import SkillController
from .group import GroupController
from .activity import ActivityController
from .eventtype import EventTypeController
from .event import EventController
from .timecard import TimeCardController

here = abspath(dirname(__file__))
attachment_storage = abspath(join(here, '../..', 'data/assets'))


class Apiv1(RestController, JsonPatchControllerMixin):

    releases = ReleaseController()
    projects = ProjectController()
    members = MemberController()
    issues = IssueController()
    items = ItemController()
    tokens = TokenController()
    oauth2 = OAUTHController()
    organizations = OrganizationController()
    invitations = InvitationController()
    tags = TagController()
    workflows = WorkflowController()
    phases = PhaseController()
    draftissues = DraftIssueController()
    resources = ResourceController()
    files = FileController()
    skills = SkillController()
    groups = GroupController()
    activities = ActivityController()
    eventtypes = EventTypeController()
    events = EventController()
    timecards = TimeCardController()

    @json
    def version(self):
        return dict(version=dolphin.__version__)


class Root(RootController):
    apiv1 = Apiv1()
    assets = Static(attachment_storage)

