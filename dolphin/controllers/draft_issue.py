from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import commit, DBSession

from ..models import DraftIssue


class DraftIssueController(ModelRestController):
    __model__ = DraftIssue

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @DraftIssue.expose
    @commit
    def define(self):
        draft_issue = DraftIssue()
        DBSession.add(draft_issue)
        return draft_issue

