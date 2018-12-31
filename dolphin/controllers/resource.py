from nanohttp import json
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Item, Member


class ResourceController(ModelRestController):
    __table__ = Member

    def __init__(self, phase=None):
        self.phase = phase

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Member.expose
    def list(self):
        resources = DBSession.query(Member) \
            .join(Item, Item.member_id == Member.id) \
            .filter(Item.phase_id == self.phase.id)
        return resources
