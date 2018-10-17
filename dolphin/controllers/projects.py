from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case

from ..backends import ChatClient
from ..exceptions import ChatRoomNotFound, RoomMemberAlreadyExist, \
    RoomMemberNotFound
from ..models import Project, Member, Subscription
from ..validators import project_validator, update_project_validator, \
    subscribe_validator


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
                    context.identity.reference_id
                )
                create_room_error = None
            except ChatRoomNotFound:
                # FIXME: Cover here
                create_room_error = 1

        return room

    def _replace_member(self, member_id, project, token, access_token):
        new_assignee_member = DBSession.query(Member) \
            .filter(Member.id == member_id) \
            .one()

        current_assignee_member = project.member
        project.member = new_assignee_member

        room_members_modified = True

        try:
            # Add new assignee member to project chat room
            ChatClient().add_member(
                project.room_id,
                new_assignee_member.reference_id,
                token,
                access_token
            )
        except RoomMemberAlreadyExist:
            room_members_modified = False
            pass

        try:
            # Remove current assignee member from project chat room
            ChatClient().remove_member(
                project.room_id,
                current_assignee_member.reference_id,
                token,
                access_token
            )
        except RoomMemberNotFound:
            room_members_modified = False
            pass

        return room_members_modified

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

        member = DBSession.query(Member) \
            .filter(Member.id == form['memberId']) \
            .one()

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
    @json(prevent_empty_form='708 No Parameter Exists In The Form')
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

        if 'title' in form and DBSession.query(Project).filter(
            Project.id != id,
            Project.title == form['title']
        ).one_or_none():
            raise HTTPStatus(
                f'600 Another project with title: ' \
                f'"{form["title"]}" is already exists.'
            )

        member = Member.current()
        current_member = project.member
        project.update_from_request()

        if 'memberId' in form and project.member.id != form['memberId']:
            member = DBSession.query(Member) \
                .filter(Member.id == form['memberId']) \
                .one_or_none()
            self._replace_member(
                form['memberId'],
                project,
                token,
                member.access_token
            )

        # The exception type is not specified because after consulting with
        # Mr.Mardani, the result got: there must be no specification on
        # exception type because nobody knows what exception may be raised
        try:
            DBSession.flush()
        except:
            self.replace_member(
                current_member.id,
                project,
                token,
                member.access_token
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
        token = context.environ['HTTP_AUTHORIZATION']

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

        member = Member.current()
        chat_client = ChatClient()
        try:
            chat_client.add_member(
                project.room_id,
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
                project.room_id,
                context.identity.reference_id,
                token,
                member.access_token
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
        token = context.environ['HTTP_AUTHORIZATION']

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

        member = Member.current()
        chat_client = ChatClient()
        try:
            chat_client.remove_member(
                project.room_id,
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
                project.room_id,
                context.identity.reference_id,
                token,
                access_token
            )
            raise

        return project

