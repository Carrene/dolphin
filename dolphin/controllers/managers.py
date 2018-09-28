from nanohttp import json, context, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession, commit
from restfulpy.controllers import ModelRestController
from sqlalchemy.exc import SQLAlchemyError

from dolphin.backends import CASClient, ChatClient
from dolphin.models import Manager, Project


class ManagerController(ModelRestController):
    __model__ = Manager

    @authorize
    @json
    @Manager.expose
    def list(self):
        query = DBSession.query(Manager)
        return query

