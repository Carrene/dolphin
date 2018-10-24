from nanohttp import json, HTTPNotFound
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

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Member.expose
    def get(self, id):

        try:
            id = int(id)
        except (ValueError, TypeError):
            raise HTTPNotFound()

        member = DBSession.query(Member).filter(Member.id == id).one_or_none()
        if not member:
            raise HTTPNotFound()

        return member

