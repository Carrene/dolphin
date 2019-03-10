from nanohttp import HTTPStatus, json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case

from .files import FileController
from .issues import IssueController
from ..backends import ChatClient
from ..exceptions import ChatRoomNotFound, RoomMemberAlreadyExist, \
    RoomMemberNotFound, HTTPManagerNotFound
from ..models import Project, Member, Subscription, Workflow, Group, Release
from ..validators import project_validator, update_project_validator


# FIXME: create room before creating project and remove PENDING
PENDING = -1


class ProjectController(ModelRestController):
    __model__ = Project

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1 and remaining_paths[1] == 'files':
            project = self._get_project(remaining_paths[0])
            return FileController(project=project)(*remaining_paths[2:])

        if len(remaining_paths) > 1 and remaining_paths[1] == 'issues':
            project = self._get_project(remaining_paths[0])
            return IssueController(project)(*remaining_paths[2:])

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
            except ChatRoomNotFound:
                # FIXME: Cover here
                create_room_error = 1

        return room

    @authorize
    @json(form_whitelist=(
        ['title', 'description', 'status', 'releaseId', 'workflowId', 'groupId',
         'managerReferenceId'],
        '707 Invalid field, only following fields are accepted: ' \
        'title, description, status, releaseId, workflowId and groupId' \
    ))
    @project_validator
    @Project.expose
    @commit
    def create(self):
        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']
        member = DBSession.query(Member) \
            .filter(Member.reference_id == form['managerReferenceId']) \
            .one_or_none()
        if member is None:
            raise HTTPManagerNotFound()

        project = Project()
        project.update_from_request()

        if 'groupId' in form:
            project.group_id = form['groupId']
        else:
            default_group = DBSession.query(Group)\
                .filter(Group.public == True)\
                .one()
            project.group = default_group

        if 'workflowId' in form:
            project.workflow_id = form['workflowId']
        else:
            default_workflow = DBSession.query(Workflow) \
                .filter(Workflow.title == 'Default') \
                .one()
            project.workflow_id = default_workflow.id

        project.manager_id = member.id
        DBSession.add(project)
        project.room_id = PENDING
        DBSession.flush()

        room = self._ensure_room(
            project.get_room_title(),
            token,
            member.access_token
        )

        chat_client = ChatClient()
        project.room_id = room['id']
        try:
            chat_client.add_member(
                project.room_id,
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
            project.room_id = room['id']
            DBSession.flush()
        except:
            chat_client.delete_room(
                project.room_id,
                token,
                member.access_token
            )
            raise

        return project

    @authorize
    @json(
        prevent_empty_form='708 No Parameter Exists In The Form',
        form_whitelist=(
            ['groupId', 'title', 'description', 'status', 'releaseId'],
            '707 Invalid field, only following fields are accepted: ' \
            'groupId, title, description, status and releaseId'
        )
    )
    @update_project_validator
    @Project.expose
    @commit
    def update(self, id):
        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']

        id = int_or_notfound(id)

        project = DBSession.query(Project).get(id)
        if not project:
            raise HTTPNotFound()

        if project.is_deleted:
            raise HTTPStatus('746 Hidden Project Is Not Editable')

        if 'title' in form:
            release = project.release

            if 'releaseId' in form and form['releaseId'] != release.id:
                release = DBSession.query(Release).get(form['releaseId'])

            for i in release.projects:
                if i.title == form['title'] and i.id != id:
                    raise HTTPStatus(
                        f'600 Another project with title: ' \
                        f'"{form["title"]}" is already exists.'
                    )

        project.update_from_request()
        return project

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Project.expose
    @commit
    def hide(self, id):
        form = context.form
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
        form = context.form
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
                project.room_id,
                identity.reference_id,
                token,
                access_token
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

