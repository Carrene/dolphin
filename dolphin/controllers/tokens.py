from nanohttp import RestController, json, context, HTTPBadRequest, validate, \
    settings
from restfulpy.authorization import authorize
from restfulpy.orm import DBSession

from ..models import Manager
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

    @json
    def obtain(self):
        cas_client = CASClient()

        access_token, ___ = cas_client \
            .get_access_token(context.form.get('authorizationCode'))

        cas_member = cas_client.get_member(access_token)
        manager = DBSession.query(Manager) \
            .filter(Manager.email == cas_member['email']) \
            .one_or_none()

        if manager is None:
            manager = Manager(
                reference_id=cas_member['id'],
                email=cas_member['email'],
                title=cas_member['title'],
                access_token=access_token
            )
        else:
            manager.access_token = access_token

        DBSession.add(manager)
        DBSession.commit()
        principal = manager.create_jwt_principal()
        context.response_headers.add_header(
            'X-New-JWT-Token',
            principal.dump().decode('utf-8')
        )

        return dict(token=principal.dump().decode('utf-8'))

