from nanohttp import HTTPStatus, json, context, HTTPNotFound
from restfulpy.orm import DBSession, commit
from restfulpy.controllers import ModelRestController

from dolphin.models import Item, item_statuses
from dolphin.validators import update_item_validator


class ItemController(ModelRestController):
    __model__ = Item

    @json
    @update_item_validator
    @Item.expose
    @commit
    def update(self, id):
        status = context.form['status']

        # FIXME: This validation must be performed inside the validation
        # decorator
        try:
            id = int(id)
        except:
            raise HTTPNotFound()

        item = DBSession.query(Item) \
            .filter(Item.id == id) \
            .one_or_none()
        if not item:
            raise HTTPNotFound()

        # FIXME: as a validator
        if status not in item_statuses:
            raise HTTPStatus(
                f'705 Invalid status value, only ' \
                f'"{", ".join(item_statuses)}" will be accepted.'
            )

        item.status = status
        return item

