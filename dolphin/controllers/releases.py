import re

from nanohttp import HTTPStatus, RestController, validate, json, context, \
    text, HTTPNotFound, HTTPBadRequest
from restfulpy.controllers import RootController
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case
from sqlalchemy import func

import dolphin
from dolphin.models import Release, release_statuses
from dolphin.validators import release_validator, update_release_validator
from dolphin.exceptions import empty_form_http_exception


class ReleaseController(RestController):
    @json
    @release_validator
    @Release.expose
    @commit
    def create(self):
        form_title = context.form.get('title')
        title_exist = DBSession.\
            query(Release).\
            filter_by(title=form_title).\
            one_or_none()

        if title_exist is not None:
            raise HTTPStatus('600 Repetitive title')

        new_release = Release()
        new_release.update_from_request()
        DBSession.add(new_release)

        return new_release

    @json
    @update_release_validator
    @Release.expose
    @commit
    def update(self, id):
        form = context.form

        # FIXME: This validation must be performed inside the validation
        # decorator
        try:
            id = int(id)
        except:
            raise HTTPNotFound()
        release = DBSession.query(Release).filter(Release.id==id).one_or_none()
        if not release:
            raise HTTPNotFound()

        # FIXME: This validation must be performed inside the validation
        # decorator.
        if not len(form.keys()):
            raise HTTPStatus(f'708 No parameter exists in the form')

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

        if 'status' in form and form['status'] not in release_statuses:
            raise HTTPStatus(
                f'705 Invalid status, only one of '
                f'"{", ".join(release_statuses)}" will be accepted'
            )

        if 'title' in form and DBSession.query(Release) \
                .filter(func.lower(Release.title) == form['title'].lower()) \
                .count() >= 1:
            raise HTTPStatus(
                f'600 Another release with title: "{form["title"]}" is already '
                f'exists'
            )

        release = DBSession.query(Release) \
            .filter(Release.id == id) \
            .one_or_none()

        release.update_from_request()
        return release

    @json
    @Release.expose
    @commit
    def abort(self, id):

        # FIXME: This validation must be performed inside the validation
        # decorator
        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        release = DBSession.query(Release).filter(Release.id==id).one_or_none()
        if not release:
            raise HTTPNotFound()

        DBSession.delete(release)
        return release

