from nanohttp import json, context, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession, commit
from restfulpy.controllers import ModelRestController

from dolphin.models import Manager, Project
from dolphin.validators import assign_manager_validator


class ManagerController(ModelRestController):
    __model__ = Manager

    @authorize
    @json
    @assign_manager_validator
    @Project.expose
    @commit
    def assign(self, id):
        form = context.form

        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        manager = DBSession.query(Manager) \
            .filter(Manager.id == id) \
            .one_or_none()
        if not manager:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == form['projectId']) \
            .one_or_none()

        project.manager = manager
        return manager

    @authorize
    @json
    @Manager.expose
    def list(self):
        query = DBSession.query(Manager)
        return query

