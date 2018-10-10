from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from dolphin.models import Manager, Member


class ManagerController(ModelRestController):
    __model__ = Manager

    @authorize
    @json
    @Manager.expose
    def list(self):
        query = DBSession.query(Manager)
        return query

