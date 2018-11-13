from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case

from ..backends import ChatClient
from ..exceptions import ChatRoomNotFound, RoomMemberAlreadyExist, \
    RoomMemberNotFound
from ..models import Container, Member, Subscription
from ..validators import container_validator, update_container_validator


class ContainerController(ModelRestController):
    __model__ = Container

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
    @container_validator
    @Container.expose
    @commit
    def create(self):
        PENDING = -1
        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']
        member = Member.current()

        container = Container()
        container.update_from_request()
        container.member_id = member.id
        DBSession.add(container)
        container.room_id = PENDING
        DBSession.flush()

        room = self._ensure_room(form['title'], token, member.access_token)

        chat_client = ChatClient()
        container.room_id = room['id']
        try:
            chat_client.add_member(
                container.room_id,
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
            container.room_id = room['id']
            DBSession.flush()
        except:
            chat_client.delete_room(
                container.room_id,
                token,
                member.access_token
            )
            raise

        return container

    @authorize
    @json(
        prevent_empty_form='708 No Parameter Exists In The Form',
        form_whitelist=(
            ['groupId', 'title', 'description', 'status'],
            '707 Invalid field, only following fields are accepted: ' \
            'groupId, title, description and status'
        )
    )
    @update_container_validator
    @Container.expose
    @commit
    def update(self, id):
        form = context.form
        token = context.environ['HTTP_AUTHORIZATION']

        try:
            id = int(id)
        except (ValueError, TypeError):
            raise HTTPNotFound()

        container = DBSession.query(Container) \
            .filter(Container.id == id) \
            .one_or_none()
        if not container:
            raise HTTPNotFound()

        if container.is_deleted:
            raise HTTPStatus('746 Hidden Container Is Not Editable')

        if 'title' in form and DBSession.query(Container).filter(
            Container.id != id,
            Container.title == form['title']
        ).one_or_none():
            raise HTTPStatus(
                f'600 Another container with title: ' \
                f'"{form["title"]}" is already exists.'
            )

        container.update_from_request()
        return container

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Container.expose
    @commit
    def hide(self, id):
        form = context.form

        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound()

        container = DBSession.query(Container) \
            .filter(Container.id == id) \
            .one_or_none()
        if not container:
            raise HTTPNotFound()

        container.soft_delete()
        return container

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Container.expose
    @commit
    def show(self, id):
        form = context.form

        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound()

        container = DBSession.query(Container) \
            .filter(Container.id == id) \
            .one_or_none()
        if not container:
            raise HTTPNotFound()

        container.soft_undelete()
        return container

    @authorize
    @json
    @Container.expose
    def list(self):

        query = DBSession.query(Container)
        return query

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Container.expose
    @commit
    def subscribe(self, id):
        token = context.environ['HTTP_AUTHORIZATION']
        identity = context.identity

        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound()

        container = DBSession.query(Container) \
            .filter(Container.id == id) \
            .one_or_none()
        if not container:
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
                container.room_id,
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
                container.room_id,
                identity.reference_id,
                token,
                member.access_token
            )
            raise

        return container

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Container.expose
    @commit
    def unsubscribe(self, id):
        token = context.environ['HTTP_AUTHORIZATION']
        identity = context.identity

        try:
            id = int(id)
        except ValueError:
            raise HTTPNotFound()

        container = DBSession.query(Container) \
            .filter(Container.id == id) \
            .one_or_none()
        if not container:
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
                container.room_id,
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
                container.room_id,
                identity.reference_id,
                token,
                access_token
            )
            raise

        return container

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Container.expose
    def get(self, id):

        try:
            id = int(id)
        except (ValueError, TypeError):
            raise HTTPNotFound()

        container = DBSession.query(Container) \
            .filter(Container.id == id) \
            .one_or_none()
        if not container:
            raise HTTPNotFound()

        return container

