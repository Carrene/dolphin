from nanohttp import json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from dolphin.models import Item
from dolphin.validators import update_item_validator


class ItemController(ModelRestController):
    __model__ = Item

    @authorize
    @json
    @update_item_validator
    @Item.expose
    @commit
    def update(self, id):
        id = int_or_notfound(id)

        item = DBSession.query(Item).get(id)
        if not item:
            raise HTTPNotFound()

        item.status = context.form['status']
        return item

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Item.expose
    def get(self, id):
        id = int_or_notfound(id)
        item = DBSession.query(Item).get(id)
        if not item:
            raise HTTPNotFound()

        return item

