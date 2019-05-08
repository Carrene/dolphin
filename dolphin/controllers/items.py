from nanohttp import json, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from dolphin.models import Item


class ItemController(ModelRestController):
    __model__ = Item

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Item.expose
    def get(self, id):
        id = int_or_notfound(id)
        item = DBSession.query(Item).get(id)
        if not item:
            raise HTTPNotFound()

        return item

