from nanohttp import json, context, int_or_notfound, HTTPNotFound
from restfulpy.authorization import authorize
from restfulpy.controllers import RestController
from restfulpy.orm import DBSession, commit

from ..models import EventType
from ..validators import eventtype_create_validator, eventtype_update_validator
from ..exceptions import StatusRepetitiveTitle


class GithubController(RestController):

    @json
    def post(self):
        print(context.form)

