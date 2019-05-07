import re
from datetime import datetime

from auditor import context as AuditLogContext
from nanohttp import HTTPStatus, json, context, HTTPNotFound, \
    HTTPUnauthorized, int_or_notfound, settings, validate, HTTPNoContent, \
    action
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController, JsonPatchControllerMixin
from restfulpy.orm import DBSession, commit
from sqlalchemy import and_, exists, select, func, join

from ..backends import ChatClient
from ..exceptions import StatusRoomMemberAlreadyExist, \
    StatusRoomMemberNotFound, StatusChatRoomNotFound, StatusRelatedIssueNotFound, \
    StatusIssueBugMustHaveRelatedIssue, StatusIssueNotFound
from ..models import Issue, Subscription, Phase, Item, Member, Project, \
    RelatedIssue, Subscribable, IssueTag, Tag
from ..validators import update_issue_validator, assign_issue_validator, \
    issue_move_validator, unassign_issue_validator, issue_relate_validator, \
    issue_unrelate_validator
from .activity import ActivityController
from .files import FileController
from .phases import PhaseController
from .tag import TagController


PENDING = -1
UNKNOWN_ASSIGNEE = -1


TRIAGE_PHASE_ID_PATTERN = re.compile(r'[(,\s]0[,\)\s]|^0$')


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
            except StatusChatRoomNotFound:
                # FIXME: Cover here
                create_room_error = 1

        return room

    @authorize
    @json(
        prevent_empty_form='708 No Parameter Exists In The Form',
        form_whitelist=(
            ['title', 'days', 'dueDate', 'kind', 'description', 'status',
             'priority', 'projectId'],
            '707 Invalid field, only following fields are accepted: '
            'title, days, dueDate, kind, description, status, priority'
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
                        f'600 Another issue with title: '
                        f'"{form["title"]}" is already exists.'
                    )

        issue.update_from_request()

        subscriptions = DBSession.query(Subscription) \
            .filter(
                and_(
                    Subscription.member_id != context.identity.id,
                    Subscription.subscribable_id == issue.id,
                    Subscription.one_shot.is_(None),
                )
            )

        self._unsee_subscriptions(subscriptions)
        return issue

    @authorize
    @json
    @Issue.expose
    def list(self):
        query = DBSession.query(Issue)
        sorting_expression = context.query.get('sort', '').strip()
        is_issue_tag_joined = False
        is_issue_item_joined = False
        needed_cte = bool(
            'phaseId' in sorting_expression or \
            'phaseTitle' in sorting_expression or \
            'phaseId' in context.query or \
            'phaseTitle' in context.query
        )

        if needed_cte:
            item_cte = select([
                Item.issue_id.label('item_issue_id'),
                func.max(Item.id).label('max_item_id'),
            ]) \
                .select_from(
                    join(Issue, Item, Issue.id == Item.issue_id, isouter=True)
                ) \
                .group_by(Item.issue_id) \
                .cte()

        # FILTER
        if 'phaseId' in context.query:
            value = context.query['phaseId']
            query = query.join(Item, Item.issue_id == Issue.id)
            query = query.join(item_cte, item_cte.c.max_item_id == Item.id)
            query = Issue._filter_by_column_value(
                query,
                Item.phase_id,
                value
            )
            if TRIAGE_PHASE_ID_PATTERN.search(value):
                triage = DBSession.query(Issue) \
                    .outerjoin(Item, Item.issue_id == Issue.id) \
                    .filter(Item.id == None)
                query = query.union(triage)

            is_issue_item_joined = True

        if 'phaseTitle' in context.query:
            value = context.query['phaseTitle']
            if not is_issue_item_joined:
                query = query.join(
                    item_cte,
                    item_cte.c.item_issue_id == Issue.id,
                )
                query = query.join(
                    Item,
                    Item.id == item_cte.c.max_item_id,
                )
                is_issue_item_joined = True

            query = query.join(Phase, Phase.id == Item.phase_id)
            query = Issue._filter_by_column_value(query, Phase.title, value)

        if 'tagId' in context.query:
            query = query.join(IssueTag, IssueTag.issue_id == Issue.id)
            value = context.query['tagId']
            query = Issue._filter_by_column_value(
                query,
                IssueTag.tag_id,
                value
            )
            is_issue_tag_joined = True

        if 'tagTitle' in context.query:
            value = context.query['tagTitle']
            if is_issue_tag_joined:
                query = query.join(Tag, Tag.id == IssueTag.tag_id)

            else:
                query = query \
                    .join(IssueTag, IssueTag.issue_id == Issue.id) \
                    .join(Tag, Tag.id == IssueTag.tag_id)
                is_issue_tag_joined = True

            query = Issue._filter_by_column_value(query, Tag.title, value)

        # SORT
        external_columns = ('phaseId', 'tagId', 'tagTitle', 'phaseTitle')

        if sorting_expression:

            sorting_columns = {
                c[1:] if c.startswith('-') else c:
                    'desc' if c.startswith('-') else None
                for c in sorting_expression.split(',')
                    if c.replace('-', '') in external_columns
            }

            if 'phaseId' in sorting_expression:
                if not is_issue_item_joined:
                    query = query.join(
                        item_cte,
                        item_cte.c.item_issue_id == Issue.id,
                        isouter=True
                    )
                    query = query.join(
                        Item,
                        Item.id == item_cte.c.max_item_id,
                        isouter=True
                    )
                    is_issue_item_joined = True

                query = Issue._sort_by_key_value(
                    query,
                    column=Item.phase_id,
                    descending=sorting_columns['phaseId']
                )

            if 'phaseTitle' in sorting_expression:

                if not is_issue_item_joined:
                    query = query.join(
                        item_cte,
                        item_cte.c.item_issue_id == Issue.id,
                        isouter=True
                    )
                    query = query.join(
                        Item,
                        Item.id == item_cte.c.max_item_id,
                        isouter=True
                    )

                if not 'phaseTitle' in context.query:
                    query = query.join(
                        Phase,
                        Phase.id == Item.phase_id,
                        isouter=True
                    )

                # THE RESULT QUERY:
                # WITH anon_1 AS
                # (SELECT item.issue_id AS item_issue_id, max(item.id)
                # AS max_item_id
                # FROM subscribable JOIN issue ON subscribable.id = issue.id
                # LEFT OUTER JOIN item ON issue.id = item.issue_id
                # GROUP BY item.issue_id)
                # SELECT subscribable.created_at AS subscribable_created_at,
                # subscribable.type_ AS subscribable_type_,
                # issue.id AS issue_id, subscribable.id AS subscribable_id,
                # subscribable.title AS subscribable_title,
                # subscribable.description AS subscribable_description,
                # issue.modified_at AS issue_modified_at, issue."modifiedBy"
                # AS "issue_modifiedBy", issue.project_id AS issue_project_id,
                # issue.room_id AS issue_room_id,
                # issue.due_date AS issue_due_date, issue.kind AS issue_kind,
                # issue.days AS issue_days, issue.status AS issue_status,
                # issue.priority AS issue_priority
                # FROM subscribable JOIN issue ON subscribable.id = issue.id
                # LEFT OUTER JOIN anon_1 ON anon_1.item_issue_id = issue.id
                # LEFT OUTER JOIN item ON item.id = anon_1.max_item_id
                # LEFT OUTER JOIN phase ON phase.id = item.phase_id

                query = Issue._sort_by_key_value(
                    query,
                    column=Phase.title,
                    descending=sorting_columns['phaseTitle']
                )

            if 'tagId' in sorting_expression:
                if not is_issue_tag_joined:
                    query = query.join(
                        IssueTag,
                        IssueTag.issue_id == Issue.id,
                        isouter=True
                    )
                    is_issue_tag_joined = True

                query = Issue._sort_by_key_value(
                    query,
                    column=IssueTag.tag_id,
                    descending=sorting_columns['tagId']
                )

            if 'tagTitle' in sorting_expression:
                if not is_issue_tag_joined:
                    query = query.join(
                        IssueTag,
                        IssueTag.issue_id == Issue.id,
                        isouter=True
                    )
                    is_issue_tag_joined = True

                if 'tagTitle' not in context.query:
                    query = query.join(
                        Tag,
                        Tag.id == IssueTag.tag_id,
                        isouter=True
                    )

                query = Issue._sort_by_key_value(
                    query,
                    column=Tag.title,
                    descending=sorting_columns['tagTitle']
                )

        if 'unread' in context.query:
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

        id = int_or_notfound(id)
        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()
        if not issue:
            raise HTTPNotFound()

        subscription = DBSession.query(Subscription).filter(
            Subscription.subscribable_id == id,
            Subscription.member_id == member.id,
        ).one_or_none()
        if subscription is not None:
            if subscription.one_shot != True:
                raise HTTPStatus('611 Already Subscribed')

            if subscription.one_shot == True:
                subscription.one_shot = None
                subscription.seent_at = datetime.utcnow()

        else:
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

        except StatusRoomMemberAlreadyExist:
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
            Subscription.member_id == member.id,
            Subscription.one_shot.is_(None),
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
        except StatusRoomMemberNotFound:
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

        if DBSession.query(Item) \
                .filter(
                    Item.phase_id == phase.id,
                    Item.member_id == member.id,
                    Item.issue_id == issue.id
                ) \
                .one_or_none():
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
            attribute_key='phase',
            attribute_label='Phase',
            value=phase.title
        )
        AuditLogContext.append(
            user=context.identity.email,
            object_=issue,
            attribute_key='resource',
            attribute_label='Resource',
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
            attribute_key='phase',
            attribute_label='Phase',
            value=phase.title
        )
        AuditLogContext.remove(
            user=context.identity.email,
            object_=issue,
            attribute_key='resource',
            attribute_label='Resource',
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
            attribute_key='project',
            attribute_label='Project',
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

        subscriptions = DBSession.query(Subscription) \
            .filter(and_(
                Subscription.member_id == context.identity.id,
                Subscription.subscribable_id == issue.id,
            ))

        for subscription in subscriptions:
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

        subscriptions = DBSession.query(Subscription) \
            .filter(
                Subscription.subscribable_id == issue.id,
                Subscription.member_id == context.identity.id,
            )

        self._unsee_subscriptions(subscriptions)
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
            raise StatusRelatedIssueNotFound(target_id)

        is_related = DBSession.query(exists().where(
            and_(
                RelatedIssue.issue_id == issue.id,
                RelatedIssue.related_issue_id == target.id
            )
        )).scalar()
        if not is_related:
            raise HTTPStatus('646 Already Unrelated')

        if issue.kind == 'bug' and len(issue.relations) < 2:
            raise StatusIssueBugMustHaveRelatedIssue()

        issue.relations.remove(target)
        return issue

    @validate(
        roomId=dict(
            type_=int,
            required=True,
        ),
        memberReferenceId=dict(
            type_=int,
            required=True,
        )
    )
    @action
    @commit
    def sent(self):
        issue = DBSession.query(Issue) \
            .filter(Issue.room_id == context.query['roomId']) \
            .one_or_none()
        if issue is None:
            raise StatusIssueNotFound()

        member = DBSession.query(Member) \
            .filter(
                Member.reference_id == context.query['memberReferenceId']
            ) \
            .one_or_none()
        if member is None:
            raise StatusRoomMemberNotFound()

        subscriptions = DBSession.query(Subscription) \
            .filter(
                Subscription.subscribable_id == issue.id,
                Subscription.member_id != member.id
            )
        self._unsee_subscriptions(subscriptions)
        issue.modified_at = datetime.utcnow()
        context.identity = member.create_jwt_principal()
        raise HTTPNoContent()

    @validate(
        roomId=dict(
            type_=int,
            required=True,
        ),
        memberReferenceId=dict(
            type_=int,
            required=True,
        ),
    )
    @action
    @commit
    def mentioned(self):
        issue = DBSession.query(Issue) \
            .filter(Issue.room_id == context.query['roomId']) \
            .one_or_none()
        if issue is None:
            raise StatusIssueNotFound()

        member = DBSession.query(Member) \
            .filter(
                Member.reference_id == context.query['memberReferenceId']
            ) \
            .one_or_none()
        if member is None:
            raise HTTPStatus('610 Member Not Found')

        subscription = DBSession.query(Subscription) \
                .filter(
                    Subscription.member_id == member.id,
                    Subscription.subscribable_id == issue.id,
                ) \
                .one_or_none()
        if subscription is None:
            subscription = Subscription(
                member_id=member.id,
                subscribable_id=issue.id,
                one_shot=True,
            )
            DBSession.add(subscription)

        subscription.seen_at = None
        issue.modified_at = datetime.utcnow()
        context.identity = member.create_jwt_principal()
        raise HTTPNoContent()

    def _unsee_subscriptions(self, subscriptions):
        for subscription in subscriptions:
            subscription.seen_at = None

