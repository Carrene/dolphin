from nanohttp import json, HTTPNotFound, int_or_notfound
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

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Group.expose
    def get(self, id):
        id = int_or_notfound(id)
        group = DBSession.query(Group).get(id)

        if not group:
            raise HTTPNotFound()

        return group

