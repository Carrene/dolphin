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

    @authorize
    @json
    @Member.expose
    @commit
    def make(self, id):

        try:
            id = int(id)
        except (TypeError, ValueError):
            raise HTTPNotFound()


        member = DBSession.query(Member).filter(Member.id == id).one_or_none()
        if member is None:
            raise HTTPNotFound()

        member.role = 'manager'
        return member

