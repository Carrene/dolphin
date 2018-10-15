from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Member


class MemberController(ModelRestController):
    __model__ = Member

    @authorize
    @json
    @Member.expose
    def list(self):
        query = DBSession.query(Member)
        return query

