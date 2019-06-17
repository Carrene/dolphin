from nanohttp import json, context, HTTPStatus, validate
from restfulpy.authorization import authorize
from restfulpy.controllers import RestController
from restfulpy.orm import DBSession

from .. import AuthorizationCode
from ...models import Application
from ..scopes import SCOPES
from ...exceptions import HTTPUnRecognizedApplication, HTTPInvalidScope


class AuthorizationCodeController(RestController):

    @json(prevent_form='707 Form Not Allowed')
    @authorize
    @validate(
        applicationId=dict(
            type_=(str, '605 We Don\'t Recognize This Application'),
            required='729 Application Id Not In Query',
        ),
        scopes=dict(required='606 Invalid Scope')
    )
    def create(self):
        state = context.query.get('state')
        scopes = context.query.get('scopes').split(',')

        for s in scopes:
            if s not in SCOPES:
                raise HTTPInvalidScope()

        application = DBSession.query(Application) \
            .filter(Application.id == context.query.get('applicationId')) \
            .one_or_none()
        if not application:
            raise HTTPUnRecognizedApplication()

        redirect_uri = context.query.get('redirectUri')\
            if context.query.get('redirectUri') else application.redirect_uri

        location = f'{redirect_uri}?application_id={application.id}'

        if state:
            location = f'{location}&state={state}'

        authorization_code_payload = dict(
            scopes=scopes,
            memberId=context.identity.id,
            memberTitle=context.identity.payload['name'],
            email=context.identity.email,
            applicationId=application.id,
            applicationTitle=application.title,
            location=location
        )
        authorization_code = AuthorizationCode(authorization_code_payload)
        return dict(authorizationCode=authorization_code.dump())

