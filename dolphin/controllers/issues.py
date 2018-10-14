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
    @json(prevent_empty_form='708 No Parameter Exists In The Form')
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
            chat_client.remove_member(
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
            chat_client.remove_member(
                issue.project.room_id,
                context.identity.reference_id,
                token,
                member.access_token
            )
        except RoomMemberNotFound:
            # Exception is passed because it means `remove_member()` is already
            # called and `member` successfully removed from room. So there is
            # no need to call `remove_member()` API again and re-add the member
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

