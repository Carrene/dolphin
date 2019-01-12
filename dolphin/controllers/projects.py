from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case

from .files import FileController
from ..backends import ChatClient
from ..exceptions import ChatRoomNotFound, RoomMemberAlreadyExist, \
    RoomMemberNotFound
from ..models import Project, Member, Subscription, Workflow, Group
from ..validators import project_validator, update_project_validator


class ProjectController(ModelRestController):
    __model__ = Project

    def __call__(self, *remaining_paths):
        if len(remaining_paths) > 1 and remaining_paths[1] == 'files':
            project = self._get_project(remaining_paths[0])
            return FileController(project)(*remaining_paths[2:])

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
        ['title', 'description', 'status', 'releaseId', 'workflowId', 'groupId'],
        '707 Invalid field, only following fields are accepted: ' \
        'title, description, status, releaseId, workflowId and groupId' \
    ))
    @project_validator
    @Project.expose
    @commit
    def create(self):
        PENDING = -1
        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']
        member = Member.current()

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
                .filter(Workflow.title == 'default') \
                .one()
            project.workflow_id = default_workflow.id

        project.member_id = member.id
        DBSession.add(project)
        project.room_id = PENDING
        DBSession.flush()

        room = self._ensure_room(form['title'], token, member.access_token)

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
            ['groupId', 'title', 'description', 'status'],
            '707 Invalid field, only following fields are accepted: ' \
            'groupId, title, description and status'
        )
    )
    @update_project_validator
    @Project.expose
    @commit
    def update(self, id):
        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']

        try:
            id = int(id)
        except (ValueError, TypeError):
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        if project.is_deleted:
            raise HTTPStatus('746 Hidden Project Is Not Editable')

        if 'title' in form and DBSession.query(Project).filter(
            Project.id != id,
            Project.title == form['title']
        ).one_or_none():
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

        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        project.soft_delete()
        return project

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Project.expose
    @commit
    def show(self, id):
        form = context.form

        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        project.soft_undelete()
        return project

    @authorize
    @json
    @Project.expose
    def list(self):

        query = DBSession.query(Project)
        return query

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Project.expose
    @commit
    def subscribe(self, id):
        token = context.environ['HTTP_AUTHORIZATION']
        identity = context.identity

        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        member = Member.current()
        if DBSession.query(Subscription).filter(
            Subscription.subscribable == id,
            Subscription.member == member.id
        ).one_or_none():
            raise HTTPStatus('611 Already Subscribed')

        subscription = Subscription(
            subscribable=id,
            member=member.id
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

        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
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

        try:
            id = int(id)
        except (ValueError, TypeError):
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        return project

