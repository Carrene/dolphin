from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..backends import ChatClient
from ..exceptions import RoomMemberAlreadyExist, RoomMemberNotFound, \
    ChatRoomNotFound
from ..models import Issue, Subscription, Resource, Phase, Item, Member
from ..validators import issue_validator, update_issue_validator, \
    assign_issue_validator


class IssueController(ModelRestController):
    __model__ = Issue

    def _ensure_room(self, title, token, access_token):
        create_room_error = 1
        room = None
        while create_room_error is not None:
            try:
                room = ChatClient().create_room(
                    title,
                    token,
                    access_token,
                    context.identity.reference_id
                )
                create_room_error = None
            except ChatRoomNotFound:
                # FIXME: Cover here
                create_room_error = 1

        return room

    @authorize
    @json(form_whitelist=(
        ['title', 'description', 'kind', 'days', 'status', 'projectId', 'dueDate'],
        '707 Invalid field, only following fields are accepted: ' \
        'title, description, kind, days, status, projectId and dueDate'
    ))
    @issue_validator
    @Issue.expose
    @commit
    def define(self):
        PENDING = -1
        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']

        issue = Issue()
        issue.update_from_request()
        DBSession.add(issue)
        issue.room_id = PENDING
        DBSession.flush()

        member = Member.current()
        room = self._ensure_room(form['title'], token, member.access_token)

        chat_client = ChatClient()
        issue.room_id = room['id']
        try:
            chat_client.add_member(
                issue.room_id,
                member.reference_id,
                token,
                member.access_token
            )
        except RoomMemberAlreadyExist:
            # Exception is passed because it means `add_member()` is already
            # called and `member` successfully added to room. So there is
            # no need to call `add_member()` API again and re-add the member to
            # room.
            pass

        # The exception type is not specified because after consulting with
        # Mr.Mardani, the result got: there must be no specification on
        # exception type because nobody knows what exception may be raised
        try:
            issue.room_id = room['id']
            DBSession.flush()
        except:
            chat_client.delete_room(
                issue.room_id,
                token,
                member.access_token
            )
            raise

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

        project = issue.project
        if 'title' in form:
            for i in project.issues:
                if i.title == form['title'] and i.id != id:
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
    @json(prevent_form='709 Form Not Allowed')
    @Issue.expose
    @commit
    def subscribe(self, id):
        token = context.environ['HTTP_AUTHORIZATION']

        try:
            id = int(id)
        except (TypeError, ValueError):
            raise HTTPNotFound()

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        member = Member.current()
        if DBSession.query(Subscription).filter(
            Subscription.subscribable == id,
            Subscription.member == member.id
        ).one_or_none():
            raise HTTPStatus('611 Already Subscribed')

        subscription = Subscription(
            subscribable=issue.id,
            member=member.id
        )
        DBSession.add(subscription)

        chat_client = ChatClient()
        try:
            chat_client.add_member(
                issue.room_id,
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
                issue.room_id,
                context.identity.reference_id,
                token,
                member.access_token
            )
            raise

        return issue

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Issue.expose
    @commit
    def unsubscribe(self, id):
        token = context.environ['HTTP_AUTHORIZATION']

        try:
            id = int(id)
        except (TypeError, ValueError):
            raise HTTPNotFound()

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        member = Member.current()
        subscription = DBSession.query(Subscription).filter(
            Subscription.subscribable == id,
            Subscription.member == member.id
        ).one_or_none()

        if not subscription:
            raise HTTPStatus('612 Not Subscribed Yet')

        DBSession.delete(subscription)

        chat_client = ChatClient()
        try:
            chat_client.kick_member(
                issue.room_id,
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
                issue.room_id,
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

