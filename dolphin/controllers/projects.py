
from nanohttp import HTTPStatus, RestController, validate, json, context, text
from restfulpy.controllers import RootController
from restfulpy.orm import DBSession, commit

import dolphin
from dolphin.models import Project
from dolphin.validators import project_validator


class ProjectController(RestController):
    title = None
    description = None
    due_date = None
    status = None

    @text
    def index(self):
        return dolphin.__version__

    @json
    @project_validator
    @Project.expose
    @commit
    def create(self):
        form_title = context.form.get('title')
        title_exist = DBSession.query(Project).filter_by(title=form_title).\
            one_or_none()

        if title_exist is not None:
            raise HTTPStatus('600 Repetitive title')

        new_project = Project()
        new_project.update_from_request()
        DBSession.add(new_project)

        return new_project

