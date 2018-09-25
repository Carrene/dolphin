from nanohttp import json, context, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession, commit
from restfulpy.controllers import ModelRestController
from sqlalchemy.exc import SQLAlchemyError

from dolphin.backends import CASClient, ChatClient
from dolphin.models import Manager, Project
from dolphin.validators import assign_manager_validator


class ManagerController(ModelRestController):
    __model__ = Manager

    @authorize
    @json
    @assign_manager_validator
    @Project.expose
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

        access_token =  CASClient() \
            .get_access_token(context.form.get('authorizationCode'))

        room = ChatClient().add_member(
            project.room_id,
            manager.reference_id,
            access_token[0]
        )

        project.manager = manager
        try:
            DBSession.commit()
        except SQLAlchemyError:
            ChatClient().remove_member(
                project.room_id,
                manager.reference_id,
                access_token[0]
            )
        return manager

    @authorize
    @json
    @Manager.expose
    def list(self):
        query = DBSession.query(Manager)
        return query

