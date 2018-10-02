from nanohttp import json, context, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession, commit
from restfulpy.controllers import ModelRestController

from dolphin.models import Item, item_statuses
from dolphin.validators import update_item_validator


class ItemController(ModelRestController):
    __model__ = Item

    @authorize
    @json
    @update_item_validator
    @Item.expose
    @commit
    def update(self, id):
        status = context.form['status']

        try:
            id = int(id)
        except (TypeError, ValueError):
            raise HTTPNotFound()

        item = DBSession.query(Item) \
            .filter(Item.id == id) \
            .one_or_none()
        if not item:
            raise HTTPNotFound()

        item.status = status
        return item

