from nanohttp import HTTPStatus, json, context, HTTPNotFound, HTTPBadRequest
from restfulpy.orm import DBSession, commit
from restfulpy.controllers import ModelRestController

from dolphin.models import Manager, Project
from dolphin.validators import assign_manager_validator


class ManagerController(ModelRestController):
    __model__ = Manager

    @json
    @assign_manager_validator
    @Project.expose
    @commit
    def assign(self, id):
        form = context.form

        # FIXME: This validation must be performed inside the validation
        # decorator
        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        manager = DBSession.query(Manager) \
            .filter(Manager.id == id).one_or_none()
        if not manager:
            raise HTTPNotFound()

        project = DBSession.query(Project) \
            .filter(Project.id == form['projectId']).one_or_none()
        if not project:
            raise HTTPStatus(f'601 Project not found with id: '
                             f'{form["projectId"]}'
            )

        import pudb; pudb.set_trace()  # XXX BREAKPOINT

        project.manager = manager
        return manager

