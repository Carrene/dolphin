from nanohttp import HTTPStatus, json, context
from restfulpy.orm import DBSession, commit
from restfulpy.controllers import ModelRestController

from dolphin.models import Project
from dolphin.validators import project_validator


class ProjectController(ModelRestController):
    __model__ = Project

    @json
    @project_validator
    @Project.expose
    @commit
    def create(self):
        title = context.form['title']
        project = DBSession.query(Project).filter_by(title=title) \
            .one_or_none()

        if project is not None:
            raise HTTPStatus(
                f'600 A project with title: {title} is already exists.'
            )

        project = Project()
        project.update_from_request()
        DBSession.add(project)
        return project

