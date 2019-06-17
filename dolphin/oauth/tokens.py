import itsdangerous
from nanohttp import settings, HTTPStatus
from restfulpy.principal import BaseJwtPrincipal

from ..exceptions import HTTPTokenExpired, HTTPMalformedAccessToken, \
    HTTPMalformedAuthorizationCode


class AuthorizationCode(BaseJwtPrincipal):

    @classmethod
    def load(cls, token):
        try:
            return super().load(token)

        except itsdangerous.SignatureExpired:
            raise HTTPTokenExpired()

        except itsdangerous.BadSignature:
            raise HTTPMalformedAuthorizationCode()

    @classmethod
    def get_config(cls):
        return settings.authorization_code

    @property
    def scopes(self):
        return self.payload.get('scopes')

    @property
    def member_id(self):
        return self.payload.get('memberId')

    @property
    def location(self):
        return self.payload.get('location')

    @property
    def application_id(self):
        return self.payload.get('applicationId')

    @property
    def email(self):
        return self.payload.get('email')


class AccessToken(BaseJwtPrincipal):

    @classmethod
    def load(cls, token):
        try:
            return super().load(token)

        except itsdangerous.SignatureExpired:
            raise HTTPTokenExpired()

        except itsdangerous.BadSignature:
            raise HTTPMalformedAccessToken()

    @classmethod
    def get_config(cls):
        return settings.access_token

    @property
    def application_id(self):
        return self.payload.get('applicationId')

    @property
    def member_id(self):
        return self.payload.get('memberId')

    @property
    def scopes(self):
        return self.payload.get('scopes')

    @property
    def id(self):
        return self.payload.get('memberId')

    @property
    def reference_id(self):
        return self.payload.get('memberId')

    @property
    def session_id(self):
        return self.payload.get('sessionId')

    def assert_roles(self):
        pass

