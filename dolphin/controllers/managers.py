from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.orm import DBSession, commit
from restfulpy.controllers import ModelRestController

from dolphin.models import Manager, Project


class ManagerController(ModelRestController):
    __model__ = Manager

    @json
    @Project.expose
    @commit
    def assign(self, id):
        form = context.form

        manager = DBSession.query(Manager) \
            .filter(Manager.id == id).one_or_none()

        if 'projectId' in form.keys() and DBSession.query(Project) \
                .filter(Project.id == form['projectId']).count() >= 1:
            raise HTTPStatus(
                f'600 Another project with title: "{form["projectId"]}" is '
                f'already assigned'
            )

        manager.projects.append(project)
        return manager
