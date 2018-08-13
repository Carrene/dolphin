
from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.utils import to_camel_case
from restfulpy.orm import DBSession, commit
from restfulpy.controllers import ModelRestController

from dolphin.models import Issue, issue_kinds, issue_statuses, Subscription
from dolphin.validators import issue_validator, update_issue_validator, \
    subscribe_issue_validator, assign_issue_validator


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

    @json
    @Issue.expose
    def list(self):

        query = DBSession.query(Issue)
        return query

    @json
    @subscribe_issue_validator
    @Issue.expose
    @commit
    def subscribe(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        if DBSession.query(Subscription).filter(
            Subscription.subscribable == id,
            Subscription.member == form['memberId']
        ).one_or_none():
            raise HTTPStatus('611 Already subscribed')

        subscription = Subscription(
            subscribable=issue.id,
            member=form['memberId']
        )
        DBSession.add(subscription)

        return issue

    @json
    @subscribe_issue_validator
    @Issue.expose
    @commit
    def unsubscribe(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        subscription = DBSession.query(Subscription).filter(
            Subscription.subscribable == id,
            Subscription.member == form['memberId']
        ).one_or_none()

        if not subscription:
            raise HTTPStatus('612 Not Subscribed Yet')

        DBSession.delete(subscription)

        return issue

    @json
    @assign_issue_validator
    @Issue.expose
    @commit
    def assign(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        resource = DBSession.query(Resource) \
            .filter(Resource.id == form['resourceId']) \
            .one_or_none()

        resource.issue = resource
        return issue

