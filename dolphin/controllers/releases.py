import re

from nanohttp import HTTPStatus, RestController, validate, json, context, text
from restfulpy.controllers import RootController
from restfulpy.orm import DBSession, commit

import dolphin
from dolphin.models import Release
from dolphin.validators import release_validator


class ReleaseController(RestController):
    title = None
    description = None
    due_date = None
    cutoff = None
    status = None

    @text
    def index(self):
        return dolphin.__version__

    @json
    @release_validator
    @Release.expose
    @commit
    def create(self):
        form_title = context.form.get('title')
        title_exist = DBSession.query(Release).filter_by(title=form_title).\
            one_or_none()

        if title_exist is not None:
            raise HTTPStatus('600 Repetitive title')

        new_release = Release()
        new_release.update_from_request()
        DBSession.add(new_release)

        return new_release

