from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case

from ..backends import ChatClient
from ..exceptions import RoomMemberAlreadyExist, RoomMemberNotFound
from ..models import Issue, Subscription, Resource, Phase, Item, Member
from ..validators import issue_validator, update_issue_validator, \
    subscribe_validator, assign_issue_validator


class IssueController(ModelRestController):
    __model__ = Issue

    @authorize
    @json
    @issue_validator
    @Issue.expose
    @commit
    def define(self):
        issue = Issue()
        issue.update_from_request()
        DBSession.add(issue)
        return issue

    @authorize
    @json(
        prevent_empty_form='708 No Parameter Exists In The Form',
        form_whitelist=(
            ['title', 'days', 'dueDate', 'kind', 'description', 'status'],
            '707 Invalid field, only following fields are accepted: ' \
            'title, days, dueDate, kind, description, status' \
        )
    )
    @update_issue_validator
    @Issue.expose
    @commit
    def update(self, id):
        form = context.form

        try:
            id = int(id)
        except (TypeError, ValueError):
            raise HTTPNotFound()

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        if 'title' in form and DBSession.query(Issue).filter(
            Issue.id != id,
            Issue.title == form['title']
        ).one_or_none():
            raise HTTPStatus(
                f'600 Another issue with title: ' \
                f'"{form["title"]}" is already exists.'
            )

        issue.update_from_request()
        return issue

    @authorize
    @json
    @Issue.expose
    def list(self):

        query = DBSession.query(Issue)
        return query

    @authorize
    @json
    @subscribe_validator
    @Issue.expose
    @commit
    def subscribe(self, id):
        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']

        try:
            id = int(id)
        except (TypeError, ValueError):
            raise HTTPNotFound()

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        if DBSession.query(Subscription).filter(
            Subscription.subscribable == id,
            Subscription.member == form['memberId']
        ).one_or_none():
            raise HTTPStatus('611 Already Subscribed')

        subscription = Subscription(
            subscribable=issue.id,
            member=form['memberId']
        )
        DBSession.add(subscription)

        member = Member.current()

        chat_client = ChatClient()
        try:
            chat_client.add_member(
                issue.project.room_id,
                context.identity.reference_id,
                token,
                member.access_token
            )

        except RoomMemberAlreadyExist:
            # Exception is passed because it means `add_member()` is already
            # called and `member` successfully added to room. So there is
            # no need to call `add_member()` API again and re-add the member to
            # room.
            pass

        try:
            DBSession.flush()
        except:
            chat_client.kick_member(
                issue.project.room_id,
                context.identity.reference_id,
                token,
                member.access_token
            )
            raise

        return issue

    @authorize
    @json
    @subscribe_validator
    @Issue.expose
    @commit
    def unsubscribe(self, id):
        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']

        try:
            id = int(id)
        except (TypeError, ValueError):
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

        member = Member.current()
        chat_client = ChatClient()
        try:
            chat_client.kick_member(
                issue.project.room_id,
                context.identity.reference_id,
                token,
                member.access_token
            )
        except RoomMemberNotFound:
            # Exception is passed because it means `kick_member()` is already
            # called and `member` successfully removed from room. So there is
            # no need to call `kick_member()` API again and re-add the member
            # to room.
            pass

        try:
            DBSession.flush()
        except:
            chat_client.add_member(
                issue.project.room_id,
                context.identity.reference_id,
                token,
                member.access_token
            )
            raise

        return issue

    @authorize
    @json
    @assign_issue_validator
    @Issue.expose
    @commit
    def assign(self, id):
        form = context.form

        try:
            id = int(id)
        except (TypeError, ValueError):
            raise HTTPNotFound()

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        resource = DBSession.query(Resource) \
            .filter(Resource.id == form['resourceId']) \
            .one_or_none()

        phase = DBSession.query(Phase) \
            .filter(Phase.id == form['phaseId']) \
            .one_or_none()

        if DBSession.query(Item).filter(
            Item.phase == phase,
            Item.resource == resource,
            Item.issue == issue
        ).one_or_none():
            raise HTTPStatus('602 Already Assigned')

        item = Item(
            phase=phase,
            resource=resource,
            issue=issue
        )

        DBSession.add(item)
        return issue

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Issue.expose
    def get(self, id):

        try:
            id = int(id)
        except (ValueError, TypeError):
            raise HTTPNotFound()

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        return issue

