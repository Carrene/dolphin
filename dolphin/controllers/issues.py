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
        form = context.form
        title = form['title']

        # FIXME: as a validator
        if form['kind'] not in issue_kinds:
            raise HTTPStatus(
                f'717 Invalid kind, only one of ' \
                f'"{", ".join(issue_kinds)}" will be accepted'
            )

        # FIXME: as a validator
        if 'status' in form.keys() and form['status'] not in issue_kinds:
            raise HTTPStatus(
                f'705 Invalid status, only one of ' \
                f'"{", ".join(issue_statuses)}" will be accepted'
            )

        issue = Issue()
        issue.update_from_request()
        DBSession.add(issue)
        return issue


    @json
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

        # FIXME: as a validator
        if not len(form.keys()):
            raise HTTPStatus('708 No parameter exists in the form')

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

        # FIXME: as a validator
        if 'status' in form and form['status'] not in issue_statuses:
            raise HTTPStatus(
                f'705 Invalid status, only one of ' \
                f'"{", ".join(issue_statuses)}" will be accepted'
            )

        # FIXME: as a validator
        if 'kind' in form and form['kind'] not in issue_kinds:
            raise HTTPStatus(
                f'717 Invalid kind, only one of ' \
                f'"{", ".join(issue_kinds)}" will be accepted'
            )

        issue.update_from_request()
        return issue

    @json
    @Issue.expose
    def list(self):

        query = DBSession.query(Issue)
        return query

