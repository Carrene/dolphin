from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.utils import to_camel_case
from restfulpy.orm import DBSession, commit
from restfulpy.controllers import ModelRestController

from dolphin.models import Issue, issue_kinds, issue_statuses
from dolphin.validators import issue_validator, update_issue_validator


class IssueController(ModelRestController):
    __model__ = Issue

    @json
    @issue_validator
    @Issue.expose
    @commit
    def define(self):
        issue = Issue()
        issue.update_from_request()
        DBSession.add(issue)
        return issue

    @json(prevent_empty_form='708 No parameter exists in the form')
    @update_issue_validator
    @Issue.expose
    @commit
    def update(self, id):
        form = context.form

        # FIXME: as a validator
        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        # FIXME: these lines should be removed and replaced by Project.validate
        # decorator
        json_columns = set(
            c.info.get('json', to_camel_case(c.key)) for c in
            Issue.iter_json_columns(include_readonly_columns=False)
        )
        if set(form.keys()) - json_columns:
            raise HTTPStatus(
                f'707 Invalid field, only one of '
                f'"{", ".join(json_columns)}" is accepted'
            )

        issue.update_from_request()
        return issue

