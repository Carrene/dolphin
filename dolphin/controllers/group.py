from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Group


class GroupController(ModelRestController):
    __model__ = Group

    @authorize
    @json
    @Group.expose
    def list(self):
        return DBSession.query(Group)