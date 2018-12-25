from nanohttp import json, context, HTTPNotFound, HTTPUnauthorized
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import commit, DBSession

from ..models import DraftIssue
from .tag import TagController


class DraftIssueController(ModelRestController):
    __model__ = DraftIssue

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1:

            if not context.identity:
                raise HTTPUnauthorized()

            try:
                id = int(remaining_paths[0])

            except (ValueError, TypeError):
                raise HTTPNotFound()

            draft_issue = DBSession.query(DraftIssue).get(id)
            if draft_issue is None:
                raise HTTPNotFound()

            if remaining_paths[1] == 'tags':
                return TagController(draft_issue=draft_issue) \
                    (*remaining_paths[2:])

        return super().__call__(*remaining_paths)

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @DraftIssue.expose
    @commit
    def define(self):
        draft_issue = DraftIssue()
        DBSession.add(draft_issue)
        return draft_issue

