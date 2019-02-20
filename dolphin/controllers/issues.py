from datetime import datetime

from nanohttp import HTTPStatus, json, context, HTTPNotFound, \
    HTTPUnauthorized, int_or_notfound, settings
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController, JsonPatchControllerMixin
from restfulpy.orm import DBSession, commit
from sqlalchemy import and_, exists
from auditor import context as AuditLogContext

from ..backends import ChatClient
from ..exceptions import RoomMemberAlreadyExist, RoomMemberNotFound, \
    ChatRoomNotFound, HTTPNotSubscribedIssue, HTTPRelatedIssueNotFound
from ..models import Issue, Subscription, Phase, Item, Member, Project, \
    RelatedIssue, Subscribable
from ..validators import update_issue_validator, assign_issue_validator, \
    issue_move_validator, unassign_issue_validator, issue_relate_validator, \
    issue_unrelate_validator
from .files import FileController
from .phases import PhaseController
from .tag import TagController
from .files import FileController
from .activity import ActivityController


PENDING = -1
UNKNOWN_ASSIGNEE = -1


class IssueController(ModelRestController, JsonPatchControllerMixin):
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

            elif remaining_paths[1] == 'files':
                return FileController(issue=issue)(*remaining_paths[2:])

            elif remaining_paths[1] == 'activities':
                return ActivityController(issue=issue)(*remaining_paths[2:])

        return super().__call__(*remaining_paths)

    def __init__(self, project=None):
        self.project = project

    def _get_issue(self, id):
        id = int_or_notfound(id)

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
    @json(
        prevent_empty_form='708 No Parameter Exists In The Form',
        form_whitelist=(
            ['title', 'days', 'dueDate', 'kind', 'description', 'status',
             'priority', 'projectId'],
            '707 Invalid field, only following fields are accepted: ' \
            'title, days, dueDate, kind, description, status, priority' \
        )
    )
    @update_issue_validator
    @Issue.expose
    @commit
    def update(self, id):
        form = context.form
        id = int_or_notfound(id)

        issue = DBSession.query(Issue).get(id)
        if not issue:
            raise HTTPNotFound()

        if 'title' in form:
            project = issue.project

            if 'projectId' in form and form['projectId'] != issue.project.id:
                project = DBSession.query(Project).get(form['projectId'])

            for i in project.issues:
                if i.title == form['title'] and i.id != id:
                    raise HTTPStatus(
                        f'600 Another issue with title: ' \
                        f'"{form["title"]}" is already exists.'
                    )

        issue.update_from_request()

        subscriptions = DBSession.query(Subscription) \
            .filter(
                and_(
                    Subscription.member_id != context.identity.id,
                    Subscription.subscribable_id == issue.id,
                )
            ).all()

        for subscription in subscriptions:
            subscription.seen_at = None

        return issue

    @authorize
    @json
    @Issue.expose
    def list(self):
        query = DBSession.query(Issue)
        if 'seenAt' in context.query:
            query = query \
                .join(
                    Subscription,
                    and_(
                        Subscription.subscribable_id == Issue.id,
                        Subscription.seen_at.is_(None),
                    )
                ) \
                .filter(Subscription.member_id == context.identity.id)

        return query

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Issue.expose
    @commit
    def subscribe(self, id=None):
        token = context.environ['HTTP_AUTHORIZATION']
        member = Member.current()
        chat_client = ChatClient()

        if context.query:
            query = DBSession.query(Issue)
            requested_issues = Issue.filter_by_request(query).all()

            if len(requested_issues) >= settings.issue.subscription.max_length:
                raise HTTPStatus(
                    f'776 Maximum {settings.issue.subscription.max_length} '
                    f'Issues To Subscribe At A Time'
                )

            requested_issues_id = {i.id for i in requested_issues}

            subscribed_issues = DBSession.query(Subscription) \
                .filter(Subscription.member_id == member.id) \
                .join(
                    Subscribable,
                    Subscribable.id == Subscription.subscribable_id
                ) \
                .filter(Subscribable.type_ == 'issue') \
                .all()
            subscribed_issues_id = {i.subscribable_id for i in subscribed_issues}

            not_subscribed_issues_id = requested_issues_id - subscribed_issues_id

            flush_counter = 0
            for each_issue_id in not_subscribed_issues_id:
                flush_counter += 1
                subscription = Subscription(
                    subscribable_id=each_issue_id,
                    member_id=member.id
                )
                DBSession.add(subscription)
                if flush_counter % 10 == 0:
                    DBSession.flush()

            not_subscribed_issues = DBSession.query(Issue) \
                .filter(Issue.id.in_(not_subscribed_issues_id))

            requested_rooms_id = [i.room_id for i in requested_issues]
            if requested_issues_id:
                chat_client.subscribe_rooms(requested_rooms_id, member)

            return not_subscribed_issues

        id = int_or_notfound(id)
        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        if DBSession.query(Subscription).filter(
                Subscription.subscribable_id == id,
                Subscription.member_id == member.id
        ).one_or_none():
            raise HTTPStatus('611 Already Subscribed')

        subscription = Subscription(
            subscribable_id=issue.id,
            member_id=member.id,
            seen_at=datetime.utcnow()
        )
        DBSession.add(subscription)

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
        id = int_or_notfound(id)

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        member = Member.current()
        subscription = DBSession.query(Subscription).filter(
            Subscription.subscribable_id == id,
            Subscription.member_id == member.id
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
        id = int_or_notfound(id)

        issue = DBSession.query(Issue).get(id)
        if not issue:
            raise HTTPNotFound()

        member = DBSession.query(Member).get(form['memberId']) \
            if 'memberId' in form else Member.current()

        phase = DBSession.query(Phase).get(form['phaseId'])

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

        AuditLogContext.append(
            user=context.identity.email,
            object_=issue,
            attribute='Phase',
            value=phase.title
        )
        AuditLogContext.append(
            user=context.identity.email,
            object_=issue,
            attribute='Resource',
            value=member.title
        )
        return issue

    @authorize
    @json
    @unassign_issue_validator
    @Issue.expose
    @commit
    def unassign(self, id):
        id = int_or_notfound(id)
        issue = DBSession.query(Issue).get(id)
        if issue is None:
            raise HTTPNotFound()

        item = DBSession.query(Item) \
            .filter(
                Item.issue_id == id,
                Item.member_id == context.form.get('memberId'),
                Item.phase_id == context.form.get('phaseId'),
            ) \
            .one_or_none()
        if not item:
            raise HTTPStatus('636 Not Assigned Yet')

        DBSession.delete(item)

        member = DBSession.query(Member).get(context.form.get('memberId'))
        phase = DBSession.query(Phase).get(context.form.get('phaseId'))
        AuditLogContext.remove(
            user=context.identity.email,
            object_=issue,
            attribute='Phase',
            value=phase.title
        )
        AuditLogContext.remove(
            user=context.identity.email,
            object_=issue,
            attribute='Resource',
            value=member.title
        )
        return issue

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Issue.expose
    def get(self, id):
        id = int_or_notfound(id)

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        return issue

    @authorize
    @json(prevent_empty_form='708 No Parameter Exists In The Form')
    @issue_move_validator
    @commit
    def move(self, id):
        id = int_or_notfound(id)

        issue = DBSession.query(Issue).get(id)
        if not issue:
            raise HTTPNotFound()

        project = DBSession.query(Project).get(context.form.get('projectId'))
        AuditLogContext.append_change_attribute(
            user=context.identity.email,
            object_=issue,
            attribute='project',
            old_value=issue.project.title,
            new_value=project.title,
        )
        issue.project_id = context.form.get('projectId')
        return issue

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Issue.expose
    @commit
    def see(self, id):
        id = int_or_notfound(id)
        issue = DBSession.query(Issue).get(id)
        if issue is None:
            raise HTTPNotFound()

        subscription = DBSession.query(Subscription) \
            .filter(
                and_(
                    Subscription.member_id == context.identity.id,
                    Subscription.subscribable_id == issue.id
                )
        ).one_or_none()

        if subscription is None:
            raise HTTPNotSubscribedIssue()

        subscription.seen_at = datetime.utcnow()
        return issue

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Issue.expose
    @commit
    def unsee(self, id):
        id = int_or_notfound(id)
        issue = DBSession.query(Issue).get(id)
        if issue is None:
            raise HTTPNotFound()

        subscription = DBSession.query(Subscription) \
            .filter(
                and_(
                    Subscription.member_id == context.identity.id,
                    Subscription.subscribable_id == issue.id
                )
        ).one_or_none()

        if subscription is None:
            raise HTTPNotSubscribedIssue()

        subscription.seen_at = None
        return issue

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @issue_relate_validator
    @commit
    def relate(self, id):
        id = int_or_notfound(id)
        target_id = context.form.get('targetIssueId')

        issue = DBSession.query(Issue).get(id)
        if issue is None:
            raise HTTPNotFound()

        target = DBSession.query(Issue).get(target_id)
        if target is None:
            raise HTTPStatus('648 Target Issue Not Found')

        is_related = DBSession.query(exists().where(
            and_(
                RelatedIssue.issue_id == issue.id,
                RelatedIssue.related_issue_id == target.id
            )
        )).scalar()
        if is_related:
            raise HTTPStatus('645 Already Is Related')

        issue.relations.append(target)
        return issue

    @authorize
    @json(prevent_empty_form='708 Empty Form')
    @issue_unrelate_validator
    @commit
    def unrelate(self, id):
        id = int_or_notfound(id)
        target_id = context.form.get('targetIssueId')

        issue = DBSession.query(Issue).get(id)
        if issue is None:
            raise HTTPNotFound()

        target = DBSession.query(Issue).get(target_id)
        if target is None:
            raise HTTPRelatedIssueNotFound(target_id)

        is_related = DBSession.query(exists().where(
            and_(
                RelatedIssue.issue_id == issue.id,
                RelatedIssue.related_issue_id == target.id
            )
        )).scalar()
        if not is_related:
            raise HTTPStatus('646 Already Unrelated')

        issue.relations.remove(target)
        return issue

