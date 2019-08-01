from os.path import abspath, dirname, join

from nanohttp import json, Static
from restfulpy.controllers import RootController, RestController, \
    JSONPatchControllerMixin

import dolphin
from .activity import ActivityController
from .batch import BatchController
from .dailyreport import DailyreportController
from .draft_issue import DraftIssueController
from .event import EventController
from .eventtype import EventTypeController
from .files import FileController
from .group import GroupController
from .invitation import InvitationController
from .issues import IssueController
from .items import ItemController
from .members import MemberController
from .oauth2 import OAUTHController
from .organization import OrganizationController
from .phase_summary import PhaseSummaryController
from .phases import PhaseController
from .projects import ProjectController
from .releases import ReleaseController
from .resource import ResourceController
from .resource_summary import ResourceSummaryController
from .skill import SkillController
from .specialty import SpecialtyController
from .tag import TagController
from .tokens import TokenController
from .workflows import WorkflowController


here = abspath(dirname(__file__))
attachment_storage = abspath(join(here, '../..', 'data/assets'))


class Apiv1(RestController, JSONPatchControllerMixin):

    releases = ReleaseController()
    projects = ProjectController()
    members = MemberController()
    issues = IssueController()
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
    specialties = SpecialtyController()
    groups = GroupController()
    activities = ActivityController()
    eventtypes = EventTypeController()
    events = EventController()
    dailyreports = DailyreportController()
    items = ItemController()
    phasessummaries = PhaseSummaryController()
    resourcessummaries = ResourceSummaryController()
    batches = BatchController()
    skills = SkillController()

    @json
    def version(self):
        return dict(version=dolphin.__version__)


class Root(RootController):
    apiv1 = Apiv1()
    assets = Static(attachment_storage)

