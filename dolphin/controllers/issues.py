from nanohttp import HTTPStatus, json, context, HTTPNotFound, HTTPUnauthorized
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..backends import ChatClient
from ..exceptions import RoomMemberAlreadyExist, RoomMemberNotFound, \
    ChatRoomNotFound
from ..models import Issue, Subscription, Phase, Item, Member
from ..validators import issue_validator, update_issue_validator, \
    assign_issue_validator, issue_move_validator
from .phases import PhaseController
from .tag import TagController


class IssueController(ModelRestController):
    __model__ = Issue

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1:

            if not context.identity:
                raise HTTPUnauthorized()

            issue = self._get_issue(remaining_paths[0])

            if remaining_paths[1] == 'phases':
                return PhaseController(issue=issue)(*remaining_paths[2:])

            elif remaining_paths[1] == 'tags':
                return TagController(issue=issue)(*remaining_paths[2:])

        return super().__call__(*remaining_paths)

    def _get_issue(self, id):
        try:
            id = int(id)

        except (ValueError, TypeError):
            raise HTTPNotFound()

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()

        if issue is None:
            raise HTTPNotFound()

        return issue

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
        ['title', 'description', 'kind', 'days', 'status', 'projectId',
         'dueDate', 'phaseId', 'memberId', 'priority'],
        '707 Invalid field, only following fields are accepted: ' \
        'title, description, kind, days, status, projectId, dueDate, ' \
        'phaseId, memberId and priority'
    ))
    @issue_validator
    @Issue.expose
    @commit
    def define(self):
        PENDING = -1
        UNKNOWN_ASSIGNEE = -1
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

        if 'phaseId' in form:
            item = Item(
                phase_id=form['phaseId'],
                issue_id=issue.id,
                member_id=UNKNOWN_ASSIGNEE,
            )
        else:
            default_phase = DBSession.query(Phase) \
                .filter(Phase.title == 'backlog') \
                .one()
            item = Item(
                phase_id=default_phase.id,
                issue_id=issue.id,
                member_id=UNKNOWN_ASSIGNEE,
            )

        if 'memberId' in form:
            item.member_id=form['memberId']
        else:
            item.member_id=context.identity.id

        return issue

    @authorize
    @json(
        prevent_empty_form='708 No Parameter Exists In The Form',
        form_whitelist=(
            ['title', 'days', 'dueDate', 'kind', 'description', 'status', 'priority'],
            '707 Invalid field, only following fields are accepted: ' \
            'title, days, dueDate, kind, description, status, priority' \
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

        issue = DBSession.query(Issue).get(id)
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

        member = DBSession.query(Member) \
            .filter(Member.id == form['memberId']) \
            .one_or_none()

        phase = DBSession.query(Phase) \
            .filter(Phase.id == form['phaseId']) \
            .one_or_none()

        if DBSession.query(Item).filter(
            Item.phase_id == phase.id,
            Item.member_id == member.id,
            Item.issue_id == issue.id
        ).one_or_none():
            raise HTTPStatus('602 Already Assigned')

        item = Item(
            phase_id=phase.id,
            member_id=member.id,
            issue_id=issue.id
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

    @authorize
    @json(prevent_empty_form='708 No Parameter Exists In The Form')
    @issue_move_validator
    @commit
    def move(self, id):
        try:
            id = int(id)

        except (ValueError, TypeError):
            raise HTTPNotFound()

        issue = DBSession.query(Issue).get(id)
        if not issue:
            raise HTTPNotFound()

        issue.project_id = context.form.get('projectId')
        return issue

