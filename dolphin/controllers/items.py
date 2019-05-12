from nanohttp import json, context, HTTPNotFound, int_or_notfound
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession, commit

from dolphin.models import Item
from dolphin.validators import update_item_validator
from dolphin.controllers import DailyreportController


class ItemController(ModelRestController):
    __model__ = Item

    def __call__(self, *remaining_path):
        if len(remaining_path) > 1 and remaining_path[1] == 'dailyreports':
            id = int_or_notfound(remaining_path[0])
            item = self._get_item(id)
            return DailyreportController(item=item)(*remaining_path[2:])

    def _get_item(self, id):
        item = DBSession.query(Item).filter(Item.id == id).one_or_none()
        if item is None:
            raise HTTPNotFound()

        return item

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

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Item.expose
    def list(self):
        return DBSession.query(Item)

