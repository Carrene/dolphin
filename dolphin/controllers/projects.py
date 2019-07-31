from auditor import context as AuditLogContext
from nanohttp import HTTPStatus, json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController, RestController
from restfulpy.orm import DBSession, commit

from ..backends import ChatClient
from ..exceptions import StatusChatRoomNotFound, \
    StatusRoomMemberAlreadyExist, StatusRoomMemberNotFound, \
    StatusManagerNotFound, StatusSecondaryManagerNotFound, \
    StatusIssueIdIsNull, StatusInvalidIssueIdType, \
    StatusIssueIdNotInForm, StatusIssueNotFound
from ..models import Project, Member, Subscription, Workflow, Group, Release, \
    GroupMember, Issue, ReturnToTriageJob
from ..validators import project_validator, update_project_validator, \
    batch_append_validator
from .files import FileController
from .issues import IssueController


FORM_WHITELIST = [
    'title',
    'description',
    'status',
    'releaseId',
    'workflowId',
    'groupId',
    'managerId',
    'secondaryManagerId'
]


FORM_WHITELISTS_STRING = ', '.join(FORM_WHITELIST)


class ProjectController(ModelRestController):
    __model__ = Project

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1 and remaining_paths[1] == 'files':
            project = self._get_project(remaining_paths[0])
            return FileController(project=project)(*remaining_paths[2:])

        if len(remaining_paths) > 1 and remaining_paths[1] == 'issues':
            project = self._get_project(remaining_paths[0])
            return IssueController(project)(*remaining_paths[2:])

        if len(remaining_paths) > 1 and remaining_paths[1] == 'batches':
            project = self._get_project(remaining_paths[0])
            return ProjectBatchController(project)(*remaining_paths[2:])

        return super().__call__(*remaining_paths)

    def _get_project(self, id):
        project = DBSession.query(Project).filter(Project.id == id) \
            .one_or_none()

        if project is None:
            raise HTTPNotFound()

        return project

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

    def _create_auditlog(self, project):
        workflow_id = context.form.get('workflowId')
        group_id = context.form.get('groupId')
        release_id = context.form.get('releaseId')
        manager_id = context.form.get('managerId')
        secondary_manager_id = context.form.get('secondaryManagerId')
        if workflow_id is not None and workflow_id != project.workflow_id:
            workflow = DBSession.query(Workflow).get(workflow_id)
            AuditLogContext.append_change_attribute(
                user=context.identity.email,
                object_=project,
                attribute_key='workflow',
                attribute_label='Workflow',
                old_value=project.workflow.title,
                new_value=workflow.title,
            )

        if group_id is not None and group_id != project.group_id:
            group = DBSession.query(Group).get(group_id)
            AuditLogContext.append_change_attribute(
                user=context.identity.email,
                object_=project,
                attribute_key='group',
                attribute_label='Group',
                old_value=project.group.title,
                new_value=group.title,
            )

        if release_id is not None and release_id != project.release_id:
            release = DBSession.query(Release).get(release_id)
            AuditLogContext.append_change_attribute(
                user=context.identity.email,
                object_=project,
                attribute_key='release',
                attribute_label='Release',
                old_value=project.release.title,
                new_value=release.title,
            )

        if manager_id is not None and manager_id != project.manager_id:
            manager = DBSession.query(Member).get(manager_id)
            AuditLogContext.append_change_attribute(
                user=context.identity.email,
                object_=project,
                attribute_key='manager',
                attribute_label='Manager',
                old_value=project.manager.title,
                new_value=manager.title,
            )

        if secondary_manager_id != project.secondary_manager_id:
            new_value = None if secondary_manager_id is None \
                else DBSession.query(Member).get(secondary_manager_id).title

            old_value = None if project.secondary_manager_id is None \
                else project.secondary_manager.title

            AuditLogContext.append_change_attribute(
                user=context.identity.email,
                object_=project,
                attribute_key='secondaryManager',
                attribute_label='Secondary Manager',
                old_value=old_value,
                new_value=new_value,
            )

    @authorize
    @json(form_whitelist=(
        FORM_WHITELIST,
        f'707 Invalid field, only following fields are accepted: '
        f'{FORM_WHITELISTS_STRING}'
    ))
    @project_validator
    @Project.expose
    @commit
    def create(self):
        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']
        manager = DBSession.query(Member).get(form['managerId'])
        creator = Member.current()
        if manager is None:
            raise StatusManagerNotFound()

        project = Project()
        project.update_from_request()
        project.manager_id = manager.id

        if form.get('secondaryManagerId') is not None:
            secondary_manager = DBSession.query(Member).get(
                form.get('secondaryManagerId')
            )
            if secondary_manager is None:
                raise StatusSecondaryManagerNotFound()

            project.secondary_manager_id = secondary_manager.id

        if 'groupId' in form:
            project.group_id = form['groupId']

        else:
            default_group = DBSession.query(Group) \
                .filter(Group.public.is_(True)) \
                .one()
            project.group_id = default_group.id

        if 'workflowId' in form:
            project.workflow_id = form['workflowId']

        else:
            default_workflow = DBSession.query(Workflow) \
                .filter(Workflow.title == 'Default') \
                .one()
            project.workflow_id = default_workflow.id

        room = self._ensure_room(
            project.get_room_title(),
            token,
            creator.access_token
        )

        chat_client = ChatClient()
        project.room_id = room['id']
        try:
            chat_client.add_member(
                project.room_id,
                manager.reference_id,
                token,
                creator.access_token
            )

        except StatusRoomMemberAlreadyExist:
            # Exception is passed because it means `add_member()` is already
            # called and `manager` successfully added to room. So there is
            # no need to call `add_member()` API again and re-add the manager to
            # room.
            pass

        # The exception type is not specified because after consulting with
        # Mr.Mardani, the result got: there must be no specification on
        # exception type because nobody knows what exception may be raised
        try:
            project.room_id = room['id']
            DBSession.flush()

        except:
            chat_client.delete_room(
                project.room_id,
                token,
                creator.access_token
            )
            raise

        DBSession.add(project)
        return project

    @authorize
    @json(
        prevent_empty_form='708 No Parameter Exists In The Form',
        form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELISTS_STRING}'
        )
    )
    @update_project_validator
    @Project.expose
    @commit
    def update(self, id):
        form = context.form
        id = int_or_notfound(id)

        project = DBSession.query(Project).get(id)
        if not project:
            raise HTTPNotFound()

        if project.is_deleted:
            raise HTTPStatus('746 Hidden Project Is Not Editable')

        manager_id = form.get('managerId')
        if manager_id is not None:
            manager = DBSession.query(Member).get(form.get('managerId'))
            if manager is None:
                raise StatusManagerNotFound()

        if form.get('secondaryManagerId') is not None:
            secondary_manager = DBSession.query(Member).get(
                form.get('secondaryManagerId')
            )
            if secondary_manager is None:
                raise StatusSecondaryManagerNotFound()

        if 'title' in form:
            release = project.release

            if 'releaseId' in form and form['releaseId'] != release.id:
                release = DBSession.query(Release).get(form['releaseId'])

            for i in release.projects:
                if i.title == form['title'] and i.id != id:
                    raise HTTPStatus(
                        f'600 Another project with title: '
                        f'"{form["title"]}" is already exists.'
                    )

        self._create_auditlog(project)
        project.update_from_request()
        return project

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Project.expose
    @commit
    def hide(self, id):
        id = int_or_notfound(id)
        project = DBSession.query(Project).get(id)
        if not project:
            raise HTTPNotFound()

        if project.removed_at is not None:
            raise HTTPStatus('638 Project Already Hidden')

        project.soft_delete()
        return project

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Project.expose
    @commit
    def show(self, id):
        id = int_or_notfound(id)
        project = DBSession.query(Project).get(id)
        if not project:
            raise HTTPNotFound()

        if project.removed_at is None:
            raise HTTPStatus('639 Project Already Shown')

        project.soft_undelete()
        return project

    @authorize
    @json
    @Project.expose
    def list(self):
        query = DBSession.query(Project)
        sorting_expression = context.query.get('sort', '').strip()

        # SORT
        external_columns = ('releaseTitle', 'managerTitle')

        if not sorting_expression:
            return query

        sorting_columns = {
            c[1:] if c.startswith('-') else c:
            'desc' if c.startswith('-') else None
            for c in sorting_expression.split(',')
            if c.replace('-', '') in external_columns
        }

        if 'releaseTitle' in sorting_expression:
            query = query.join(
                Release,
                Release.id == Project.release_id
            )
            query = Project._sort_by_key_value(
                query,
                column=Release.title,
                descending=sorting_columns['releaseTitle']
            )

        if 'managerTitle' in sorting_expression:
            query = query.join(
                Member,
                Member.id == Project.manager_id
            )
            query = Project._sort_by_key_value(
                query,
                column=Member.title,
                descending=sorting_columns['managerTitle']
            )

        return query

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Project.expose
    @commit
    def subscribe(self, id):
        token = context.environ['HTTP_AUTHORIZATION']
        identity = context.identity
        id = int_or_notfound(id)

        project = DBSession.query(Project).get(id)
        if not project:
            raise HTTPNotFound()

        member = Member.current()
        if DBSession.query(Subscription).filter(
                Subscription.subscribable_id == id,
                Subscription.member_id == member.id
        ).one_or_none():
            raise HTTPStatus('611 Already Subscribed')

        subscription = Subscription(
            subscribable_id=id,
            member_id=member.id
        )
        DBSession.add(subscription)

        chat_client = ChatClient()
        try:
            chat_client.add_member(
                project.room_id,
                identity.reference_id,
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
                project.room_id,
                identity.reference_id,
                token,
                member.access_token
            )
            raise

        return project

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Project.expose
    @commit
    def unsubscribe(self, id):
        token = context.environ['HTTP_AUTHORIZATION']
        identity = context.identity
        id = int_or_notfound(id)

        project = DBSession.query(Project).get(id)
        if not project:
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
                project.room_id,
                identity.reference_id,
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
                project.room_id,
                identity.reference_id,
                token,
                member.access_token
            )
            raise

        return project

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Project.expose
    def get(self, id):
        id = int_or_notfound(id)

        project = DBSession.query(Project).get(id)
        if not project:
            raise HTTPNotFound()

        return project


class ProjectBatchController(RestController):
    def __init__(self, project):
        self.project = project

    @authorize
    @json
    @batch_append_validator
    @commit
    def append(self, id):
        id = int_or_notfound(id)
        issue_id = context.form['issueIds']
        issue = DBSession.query(Issue) \
            .filter(Issue.id == issue_id) \
            .one_or_none()
        if issue is None:
            raise StatusIssueNotFound(issue_id)

        available_batch = DBSession.query(Issue) \
            .filter(Issue.batch == id) \
            .one_or_none()

        if available_batch is None:
            issue.batch = id

        else:
            issue.batch = id
            issue.stage = available_batch.stage
            if issue.stage == 'backlog' and available_batch.returntotriagejobs:
                returntotriage = ReturnToTriageJob(
                    at=available_batch.returntotriagejobs[0].at,
                    issue_id=issue.id,
                )
                issue.returntotriagejobs.append(returntotriage)

        DBSession.flush()
        issue_ids = DBSession.query(Issue.id) \
            .filter(Issue.batch == id)

        batch = dict(
            id=int(id),
            projectId=self.project.id,
            issueIds=[i[0] for i in issue_ids],
        )
        return batch

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    def list(self):
        issues = DBSession.query(Issue) \
            .filter(Issue.project_id == self.project.id)

        batches = {}
        for issue in issues:
            if issue.batch in batches.keys():
                batches[issue.batch]['issueIds'].append(issue.id)

            else:
                batches[issue.batch] = dict(
                    id=issue.batch,
                    projectId=self.project.id,
                    issueIds=[issue.id],
                )

        return list(batches.values())

