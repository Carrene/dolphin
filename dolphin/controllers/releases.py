import re

from nanohttp import json, context, HTTPNotFound
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit
from restfulpy.utils import to_camel_case

from dolphin.models import Release, release_statuses
from dolphin.validators import release_validator, update_release_validator


class ReleaseController(ModelRestController):
    __model__ = Release

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

    @json(prevent_empty_form='708 No parameter exists in the form')
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

    @json
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

