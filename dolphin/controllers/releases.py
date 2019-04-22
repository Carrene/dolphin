from nanohttp import json, context, HTTPNotFound, HTTPStatus, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from ..exceptions import HTTPManagerNotFound, \
    HTTPLaunchDateMustGreaterThanCutoffDate, ChatRoomNotFound, \
    RoomMemberAlreadyExist, RoomMemberNotFound
from ..models import Release, Subscription, Member
from ..validators import release_validator, update_release_validator
from ..backends import ChatClient


FORM_WHITELIST = [
    'title',
    'description',
    'status',
    'cutoff',
    'managerReferenceId',
    'launchDate',
]


FORM_WHITELISTS_STRING = ', '.join(FORM_WHITELIST)


class ReleaseController(ModelRestController):
    __model__ = Release

    @authorize
    @json(
        prevent_empty_form='708 No Parameter Exists In The Form',
        form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELISTS_STRING}'
        )
    )
    @release_validator
    @Release.expose
    @commit
    def create(self):
        token = context.environ['HTTP_AUTHORIZATION']
        member = DBSession.query(Member) \
            .filter(
                Member.reference_id == context.form['managerReferenceId']
            ) \
            .one_or_none()
        if member is None:
            raise HTTPManagerNotFound()

        release = Release()
        release.manager_id = member.id
        release.update_from_request()
        if release.launch_date < release.cutoff:
            raise HTTPLaunchDateMustGreaterThanCutoffDate()

        chat_client = ChatClient()
        room = chat_client.create_room(
            release.get_room_title(),
            token,
            member.access_token,
            context.identity.reference_id
        )
        release.room_id = room['id']
        try:
            chat_client.add_member(
                release.room_id,
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

        DBSession.add(release)
        return release

    @authorize
    @json(
        prevent_empty_form='708 No Parameter Exists In The Form',
        form_whitelist=(
            FORM_WHITELIST,
            f'707 Invalid field, only following fields are accepted: '
            f'{FORM_WHITELISTS_STRING}'
        )
    )
    @update_release_validator
    @Release.expose
    @commit
    def update(self, id):
        form = context.form
        id = int_or_notfound(id)

        release = DBSession.query(Release).get(id)
        if not release:
            raise HTTPNotFound()

        if 'title' in form and DBSession.query(Release).filter(
            Release.id != id,
            Release.title == form['title']
        ).one_or_none():
            raise HTTPStatus(
                f'600 Another release with title: '
                f'"{form["title"]}" is already exists.'
            )

        manager_reference_id = context.form.get('managerReferenceId')
        if manager_reference_id is not None:
            member = DBSession.query(Member) \
                .filter(Member.reference_id == manager_reference_id) \
                .one_or_none()
            if member is None:
                raise HTTPManagerNotFound()

            release.manager_id = member.id

        release.update_from_request()
        if release.launch_date < release.cutoff:
            raise HTTPLaunchDateMustGreaterThanCutoffDate()

        return release

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Release.expose
    @commit
    def abort(self, id):
        id = int_or_notfound(id)

        release = DBSession.query(Release).get(id)
        if not release:
            raise HTTPNotFound()

        DBSession.delete(release)
        release_dict = release.to_dict()

        # The returning value type is `dict` because the `to_dict` function
        # value after `@commit` is not accessible
        return release_dict

    @authorize
    @json
    @Release.expose
    def list(self):
        return DBSession.query(Release)

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Release.expose
    @commit
    def subscribe(self, id):
        id = int_or_notfound(id)
        release = DBSession.query(Release).get(id)
        if not release:
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

        return release

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Release.expose
    @commit
    def unsubscribe(self, id):
        id = int_or_notfound(id)
        release = DBSession.query(Release).get(id)
        if not release:
            raise HTTPNotFound()

        member = Member.current()
        subscription = DBSession.query(Subscription).filter(
            Subscription.subscribable_id == id,
            Subscription.member_id == member.id
        ).one_or_none()

        if not subscription:
            raise HTTPStatus('612 Not Subscribed Yet')

        DBSession.delete(subscription)
        return release

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Release.expose
    def get(self, id):
        id = int_or_notfound(id)

        release = DBSession.query(Release).get(id)
        if not release:
            raise HTTPNotFound()

        return release

