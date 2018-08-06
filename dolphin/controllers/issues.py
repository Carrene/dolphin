from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.utils import to_camel_case
from restfulpy.orm import DBSession, commit
from restfulpy.controllers import ModelRestController

from dolphin.models import Issue, issue_kinds, issue_statuses
from dolphin.validators import issue_validator


class IssueController(ModelRestController):
    __model__ = Issue

    @json
    @issue_validator
    @Issue.expose
    @commit
    def define(self):
        form = context.form
        title = form['title']

        if form['kind'] not in issue_kinds:
            raise HTTPStatus(f'717 Invalid kind, only one of ' \
                             f'"{", ".join(issue_kinds)}" will be accepted'
            )

        if 'status' in form.keys() and form['status'] not in issue_kinds:
            raise HTTPStatus(f'705 Invalid status, only one of ' \
                             f'"{", ".join(issue_statuses)}" will be accepted'
            )

        if DBSession.query(Issue) \
                .filter(Issue.title == title).one_or_none():
            raise HTTPStatus(
                f'600 Another project with title: "{title}" is already exists.'
            )

        issue = Issue()
        issue.update_from_request()
        DBSession.add(issue)
        return issue

