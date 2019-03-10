from nanohttp import json, context, HTTPNotFound, HTTPStatus, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case

from ..backends import ChatClient
from ..exceptions import RoomMemberAlreadyExist, RoomMemberNotFound, \
    HTTPManagerNotFound
from ..models import Release, release_statuses, Subscription, Member
from ..validators import release_validator, update_release_validator


FORM_WHITELIST = [
    'title',
    'description',
    'status',
    'cutoff',
    'managerReferenceId',
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
        member = DBSession.query(Member) \
            .filter(Member.reference_id == context.form['managerReferenceId']) \
            .one_or_none()
        if member is None:
            raise HTTPManagerNotFound()

        release = Release()
        release.manager = member
        release.update_from_request()
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
                f'600 Another release with title: ' \
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
        return release

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
        token = context.environ['HTTP_AUTHORIZATION']
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
        token = context.environ['HTTP_AUTHORIZATION']
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

