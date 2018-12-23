from nanohttp import json, context
from restfulpy.authorization import authorize
from restfulpy.controllers import ModelRestController
from restfulpy.orm import DBSession

from ..models import Tag


class TagController(ModelRestController):
    __model__ = Tag

    @authorize
    @json(prevent_form='709 Form Not Allowed')
    @Tag.expose
    def list(self):
        return DBSession.query(Tag).filter(
            Tag.organization_id == context.identity.payload['organizationId']
        )

