import re
from datetime import datetime
import json

from auditor import context as AuditLogContext
from nanohttp import HTTPStatus, json, context, HTTPNotFound, \
    HTTPUnauthorized, int_or_notfound, settings, validate, HTTPNoContent, \
    action
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController, JsonPatchControllerMixin
from restfulpy.orm import DBSession, commit
from restfulpy.mule import MuleTask, worker
from sqlalchemy import and_, exists, select, func, join, or_, Text, cast

from ..backends import ChatClient
from ..exceptions import StatusRoomMemberAlreadyExist, \
    StatusRoomMemberNotFound, StatusChatRoomNotFound, StatusRelatedIssueNotFound, \
    StatusIssueBugMustHaveRelatedIssue, StatusIssueNotFound, \
    StatusQueryParameterNotInFormOrQueryString
from ..models import Issue, Subscription, Phase, Item, Member, Project, \
    RelatedIssue, Subscribable, IssueTag, Tag, Resource, SkillMember, \
    AbstractResourceSummaryView, AbstractPhaseSummaryView, IssuePhase, \
    ReturnTotriageJob
from ..validators import update_issue_validator, assign_issue_validator, \
    issue_move_validator, unassign_issue_validator, issue_relate_validator, \
    issue_unrelate_validator, search_issue_validator
from .activity import ActivityController
from .files import FileController
from .phases import PhaseController
from .tag import TagController


# FIXME: Remove these two redundant lines
PENDING = -1
UNKNOWN_ASSIGNEE = -1


FORM_WHITELIST = [
    'stage',
    'isDone',
    'description',
    'phaseId',
    'memberId',
    'projectId',
    'title',
    'days',
    'priority',
    'kind',
]


FORM_WHITELIST_STRING = ', '.join(FORM_WHITELIST)


TRIAGE_PHASE_ID_PATTERN = re.compile(r'[(,\s]0[,\)\s]|^0$')


class IssueController(ModelRestController, JsonPatchControllerMixin):
    __model__ = Issue

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1:

            if not context.identity:
                raise HTTPUnauthorized()

            issue = self._get_issue(remaining_paths[0])

            if remaining_paths[1] == 'phases':
                return IssuePhaseController(issue=issue)(*remaining_paths[2:])

            elif remaining_paths[1] == 'tags':
                return TagController(issue=issue)(*remaining_paths[2:])

            elif remaining_paths[1] == 'files':
                return FileController(issue=issue)(*remaining_paths[2:])

            elif remaining_paths[1] == 'activities':
                return ActivityController(issue=issue)(*remaining_paths[2:])

            elif remaining_paths[1] == 'phasessummaries':
                return IssuePhaseSummaryController(issue=issue)(*remaining_paths[2:])

            elif remaining_paths[1] == 'jobs':
                return IssueJobController(issue=issue)(*remaining_paths[2:])

        return super().__call__(*remaining_paths)

    def __init__(self, project=None):
        self.project = project

    def _get_issue(self, id):
        id = int_or_notfound(id)

        issue = DBSession.query(Issue).filter(Issue.id == id).one_or_none()

        if issue is None:
            raise HTTPNotFound()

        return issue

    def _is_first_phase(self, phase):
        workflow = phase.workflow
        first_phase_order, = DBSession.query(func.min(Phase.order)) \
            .filter(Phase.workflow_id == workflow.id) \
            .one()

        return first_phase_order == phase.order

    @authorize
    @json(
        prevent_empty_form='708 No Parameter Exists In The Form',
        form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELIST_STRING}'
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
        is_issue_issue_phase_joined = False
        needed_cte = bool(
            'phaseId' in sorting_expression or \
            'phaseTitle' in sorting_expression or \
            'phaseId' in context.query or \
            'phaseTitle' in context.query
        )

        # FILTER
        if 'phaseId' in context.query:
            value = context.query['phaseId']

            query = Issue._filter_by_column_value(
                query,
                Issue.phase_id,
                value
            )
            if TRIAGE_PHASE_ID_PATTERN.search(value):
                triage = DBSession.query(Issue).filter(Issue.phase_id == None)
                query = query.union(triage)

            del context.query['phaseId']

        if 'phaseTitle' in context.query:
            value = context.query['phaseTitle']
            if not is_issue_issue_phase_joined:
                query = query.join(
                    Phase,
                    Phase.id == Issue.phase_id,
                )
                is_issue_issue_phase_joined = True

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
        external_columns = ('tagId', 'tagTitle', 'phaseTitle')

        if sorting_expression:

            sorting_columns = {
                c[1:] if c.startswith('-') else c:
                    'desc' if c.startswith('-') else None
                for c in sorting_expression.split(',')
                    if c.replace('-', '') in external_columns
            }

            if 'phaseTitle' in sorting_expression:

                if not 'phaseTitle' in context.query:
                    query = query.join(
                        Phase,
                        Phase.id == Issue.phase_id,
                        isouter=True
                    )

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
            DBSession.flush()

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
        DBSession.flush()

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

        return issue

    @authorize
    @json(form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELIST_STRING}'
        )
    )
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

        phase_issue = DBSession.query(IssuePhase). \
            filter(
                IssuePhase.issue_id == id,
                IssuePhase.phase_id == phase.id
            ).one_or_none()

        if phase_issue is None:
            phase_issue = IssuePhase(
                issue_id = id,
                phase_id = phase.id
            )
            DBSession.add(phase_issue)
            DBSession.flush()

        if DBSession.query(Item) \
                .filter(
                    Item.issue_phase_id == phase_issue.id,
                    Item.member_id == member.id,
                ) \
                .one_or_none():
            raise HTTPStatus('602 Already Assigned')

        item = Item(
            member_id=member.id,
            issue_phase_id=phase_issue.id
        )
        DBSession.add(item)

        if self._is_first_phase(phase):
            item.need_estimate_timestamp = datetime.now()

        subscription = DBSession.query(Subscription) \
            .filter(
                Subscription.subscribable_id == issue.id,
                Subscription.member_id == member.id
            ) \
            .one_or_none()
        if subscription is None:
            subscription = Subscription(
                subscribable_id=issue.id,
                member_id=member.id
            )
            DBSession.add(subscription)

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

        issue_phase = DBSession.query(IssuePhase) \
            .filter(
                IssuePhase.issue_id == id,
                IssuePhase.phase_id == context.form.get('phaseId')
            ) \
            .one_or_none()
        if issue_phase is None:
            raise HTTPStatus('636 Not Assigned Yet')

        item = DBSession.query(Item) \
            .filter(
                Item.issue_phase_id == issue_phase.id,
                Item.member_id == context.form.get('memberId'),
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

    @authorize
    @search_issue_validator
    @json
    @Issue.expose
    def search(self):
        query = context.form.get('query') or context.query.get('query')
        if query is None:
            raise StatusQueryParameterNotInFormOrQueryString()

        query = f'%{query}%'
        query = DBSession.query(Issue) \
            .filter(or_(
                Issue.title.ilike(query),
                Issue.description.ilike(query),
                cast(Issue.id, Text).ilike(query)
            ))

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


class IssuePhaseSummaryController(ModelRestController):
    __model__ = AbstractPhaseSummaryView

    def __init__(self, issue=None):
        self.issue = issue

    @authorize
    @json(prevent_form=True)
    @AbstractPhaseSummaryView.expose
    @commit
    def list(self):
        phase_summary_view = AbstractPhaseSummaryView \
            .create_mapped_class(self.issue.id)
        query = DBSession.query(phase_summary_view)
        return query


class IssuePhaseController(ModelRestController):
    __model__ = Phase

    def __init__(self, issue):
        self.issue = issue

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1:
            phase = self._get_phase(remaining_paths[0])
            if remaining_paths[1] == 'resourcessummaries':
                return IssuePhaseResourceSummaryController(
                    phase=phase, issue=self.issue
                )(*remaining_paths[2:])

        return super().__call__(*remaining_paths)

    def _get_phase(self, id):
        id = int_or_notfound(id)
        phase = DBSession.query(Phase).get(id)
        if phase is None:
            raise HTTPNotFound()

        return phase


class IssuePhaseResourceSummaryController(ModelRestController):
    __model__ = AbstractResourceSummaryView

    def __init__(self, phase, issue):
        self.phase = phase
        self.issue = issue

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @AbstractResourceSummaryView.expose
    def list(self):
        phase_summary_view = AbstractResourceSummaryView \
            .create_mapped_class(issue_id=self.issue.id, phase_id=self.phase.id)
        query = DBSession.query(phase_summary_view)
        return query


class IssueJobController(ModelRestController):
    __model__ = ReturnTotriageJob

    def __init__(self, issue):
        self.issue = issue

    @authorize
    @json
    @commit
    def schedule(self):
        if self.issue.returntotriagejobs:
            returntotriages = DBSession.query(ReturnTotriageJob) \
                .filter(ReturnTotriageJob.issue_id == self.issue.id)

            for returntotriage in returntotriages:
                returntotriage.status = 'expired'
                returntotriage.terminated_at = datetime.now()

        job = ReturnTotriageJob()
        job.update_from_request()
        job.issue_id = self.issue.id
        DBSession.add(job)
        return job

