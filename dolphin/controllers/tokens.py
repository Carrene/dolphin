from nanohttp import RestController, json, context, HTTPBadRequest, validate, \
    settings
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession

from ..models import Member
from ..backends import CASClient


class TokenController(RestController):

    @validate(
        email=dict(
            required='400 Invalid email or password'
        ),
    )
    @json
    def create(self):
        email = context.form.get('email')
        principal = context.application.__authenticator__.login(email)
        if principal is None:
            raise HTTPBadRequest('Invalid email or password')
        return dict(token=principal.dump())

    @authorize
    @json
    def invalidate(self):
        context.application.__authenticator__.logout()
        return {}

    @json(prevent_form='711 Form Not Allowed')
    def request(self):
        return dict(
            scopes=['email', 'title'],
            applicationId=settings.oauth['application_id'],
        )

