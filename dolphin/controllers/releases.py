import re

from nanohttp import json, context, HTTPNotFound, HTTPStatus
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case

from ..models import Release, release_statuses, Subscription
from ..validators import release_validator, update_release_validator, \
    subscribe_validator


class ReleaseController(ModelRestController):
    __model__ = Release

    @authorize
    @json
    @release_validator
    @Release.expose
    @commit
    def create(self):
        title = context.form.get('title')
        release = DBSession.query(Release) \
            .filter(Release.title == title) \
            .one_or_none()

        new_release = Release()
        new_release.update_from_request()
        DBSession.add(new_release)
        return new_release

    @authorize
    @json(prevent_empty_form='708 No Parameter Exists In The Form')
    @update_release_validator
    @Release.expose
    @commit
    def update(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        release = DBSession.query(Release) \
            .filter(Release.id == id) \
            .one_or_none()
        if not release:
            raise HTTPNotFound()

        # FIXME: these lines should be removed and replaced by Release.validate
        # decorator
        json_columns = set(
            c.info.get('json', to_camel_case(c.key)) for c in
            Release.iter_json_columns(include_readonly_columns=False)
        )
        if set(form.keys()) - json_columns:
            raise HTTPStatus(
                f'707 Invalid field, only one of '
                f'{", ".join(release_statuses)} will be accepted'
            )

        release = DBSession.query(Release) \
            .filter(Release.id == id) \
            .one_or_none()
        release.update_from_request()
        return release

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Release.expose
    @commit
    def abort(self, id):

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        release = DBSession.query(Release) \
            .filter(Release.id == id) \
            .one_or_none()
        if not release:
            raise HTTPNotFound()

        DBSession.delete(release)
        return release

    @authorize
    @json
    @Release.expose
    def list(self):

        query = DBSession.query(Release)
        return query

    @authorize
    @json
    @subscribe_validator
    @Release.expose
    @commit
    def subscribe(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        release = DBSession.query(Release) \
            .filter(Release.id == id) \
            .one_or_none()
        if not release:
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

        return release

    @authorize
    @json
    @subscribe_validator
    @Release.expose
    @commit
    def unsubscribe(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        release = DBSession.query(Release) \
            .filter(Release.id == id) \
            .one_or_none()
        if not release:
            raise HTTPNotFound()

        subscription = DBSession.query(Subscription).filter(
            Subscription.subscribable == id,
            Subscription.member == form['memberId']
        ).one_or_none()

        if not subscription:
            raise HTTPStatus('612 Not Subscribed Yet')

        DBSession.delete(subscription)

        return release

