from itsdangerous import BadSignature
from cas import CASPrincipal
from nanohttp import HTTPStatus, context, HTTPUnauthorized, HTTPBadRequest
from restfulpy.authentication import StatefulAuthenticator
from restfulpy.orm import DBSession

from .models import Member


class Authenticator(StatefulAuthenticator):

    @staticmethod
    def safe_member_lookup(condition):
        member = DBSession.query(Member).filter(condition).one_or_none()
        if member is None:
            raise HTTPStatus('400 Incorrect Email Or Password')

        return member

    def create_principal(self, member_id=None, session_id=None):
        member = self.safe_member_lookup(Member.id == member_id)
        return member.create_jwt_principal()

    def create_refresh_principal(self, member_id=None):
        member = self.safe_member_lookup(Member.id == member_id)
        return member.create_refresh_principal()

    def validate_credentials(self, email):
        member = self.safe_member_lookup(Member.email == email)
        return member

    def verify_token(self, encoded_token):
        try:
            principal = CASPrincipal.load(encoded_token)
        except BadSignature:
            raise HTTPBadRequest()

        member = DBSession.query(Member) \
            .filter(Member.reference_id == principal.payload['referenceId']) \
            .one_or_none()
        if not member:
            raise HTTPUnauthorized()

        # TODO: Updating member when any scope attributes are changed

        return principal

