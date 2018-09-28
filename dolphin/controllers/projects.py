from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case

from ..backends import ChatClient, CASClient
from ..validators import project_validator, update_project_validator, \
    subscribe_validator
from ..exceptions import ChatServerNotFound, ChatServerNotAvailable, \
    ChatInternallError, ChatRoomNotFound, RoomMemberAlreadyExist, \
    RoomMemberNotFound


class ProjectController(ModelRestController):
    __model__ = Project

    def _ensure_room(self, title, token, access_token):
        create_room_error = 1
        room = None
        while create_room_error is not None:
            try:
                room = ChatClient().create_room(
                    title,
                    token,
                    access_token,
                    context.identity.payload['referenceId']
                )
                create_room_error = None
            except ChatRoomNotFound:
                # FIXME: Cover here
                create_room_error = 1

        return room

    def manager_replacement(self, manager_id, project, access_token):
        new_assignee_manager = DBSession.query(Manager) \
            .filter(Manager.id == manager_id) \
            .one_or_none()
        current_assignee_manager = project.manager
        project.manager = new_assignee_manager

        try:
            # Add new assignee manager to project chat room
            room = ChatClient().add_member(
                project.room_id,
                new_assignee_manager.reference_id,
                access_token
            )
        except RoomMemberAlreadyExist:
            pass

        try:
            # Remove current assignee manager from project chat room
            room = ChatClient().remove_member(
                project.room_id,
                current_assignee_manager.reference_id,
                access_token
            )
        except RoomMemberNotFound:
            pass

        return room

    @authorize
    @json
    @project_validator
    @Project.expose
    @commit
    def create(self):
        PENDING = -1
        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']

        project = Project()
        project.update_from_request()
        DBSession.add(project)
        project.room_id = PENDING
        DBSession.flush()

        manager = DBSession.query(Manager) \
            .filter(Manager.id == form['managerId']) \
            .one_or_none()

        access_token, ___ =  CASClient() \
            .get_access_token(context.form.get('authorizationCode'))

        room = self._ensure_room(form['title'], token, access_token)

        try:
            ChatClient().add_member(
                project.room_id,
                manager.reference_id,
                token,
                access_token
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
            ChatClient().delete_room(title, token, access_token)
            raise

        return project

    @authorize
    @json(prevent_empty_form='708 No Parameter Exists In The Form')
    @update_project_validator
    @Project.expose
    @commit
    def update(self, id):
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

        # FIXME: these lines should be removed and replaced by Project.validate
        # decorator
        json_columns = set(
            c.info.get('json', to_camel_case(c.key)) for c in
            Project.iter_json_columns(include_readonly_columns=False)
        )
        json_columns.add('authorizationCode')
        if set(form.keys()) - json_columns:
            raise HTTPStatus(
                f'707 Invalid field, only one of '
                f'"{", ".join(json_columns)}" is accepted'
            )

        if form['title'] and DBSession.query(Project).filter(
            Project.id != id,
            Project.title == form['title']
        ).one_or_none():
            raise HTTPStatus(
                f'600 Another project with title: ' \
                f'"{form["title"]}" is already exists.'
            )

        access_token, ___ =  CASClient() \
            .get_access_token(context.form.get('authorizationCode'))

        current_manager = project.manager
        project.update_from_request()

        if form['managerId'] and project.manager.id != form['managerId']:
            room = self.manager_replacement(
                form['managerId'],
                project,
                access_token
            )

        # The exception type is not specified because after consulting with
        # Mr.Mardani, the result got: there must be no specification on
        # exception type because nobody knows what exception may be raised
        try:
            DBSession.flush()
        except:
            room = self.manager_replacement(
                current_manager.id,
                project,
                access_token
            )
            raise

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
    @json
    @subscribe_validator
    @Project.expose
    @commit
    def subscribe(self, id):
        form = context.form
        payload = context.identity.payload

        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        if DBSession.query(Subscription).filter(
            Subscription.subscribable == id,
            Subscription.member == form['memberId']
        ).one_or_none():
            raise HTTPStatus('611 Already Subscribed')

        subscription = Subscription(
            subscribable=id,
            member=form['memberId']
        )
        DBSession.add(subscription)

        access_token, ___ =  CASClient() \
            .get_access_token(context.form.get('authorizationCode'))
        try:
            room = ChatClient().add_member(
                project.room_id,
                payload['reference_id'],
                access_token
            )
        except RoomMemberAlreadyExist:
            pass

        try:
            DBSession.flush()
        except:
            room = ChatClient().remove_member(
                project.room_id,
                payload['reference_id'],
                access_token
            )
            raise

        return project

    @authorize
    @json
    @subscribe_validator
    @Project.expose
    @commit
    def unsubscribe(self, id):
        form = context.form
        payload = context.identity.payload

        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == id) \
            .one_or_none()
        if not project:
            raise HTTPNotFound()

        subscription = DBSession.query(Subscription).filter(
            Subscription.subscribable == id,
            Subscription.member == form['memberId']
        ).one_or_none()
        if not subscription:
            raise HTTPStatus('612 Not Subscribed Yet')

        DBSession.delete(subscription)

        access_token, ___ =  CASClient() \
            .get_access_token(context.form.get('authorizationCode'))
        try:
            room = ChatClient().remove_member(
                project.room_id,
                payload['reference_id'],
                access_token
            )
        except RoomMemberNotFound:
            pass

        try:
            DBSession.flush()
        except:
            room = ChatClient().add_member(
                project.room_id,
                payload['reference_id'],
                access_token
            )
            raise

        return project

