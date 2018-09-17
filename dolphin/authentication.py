from nanohttp import HTTPStatus, context
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
        if not encoded_token.startswith('oauth2-accesstoken'):
            return super().verify_token(encoded_token)

        return AccessToken.load(encoded_token.split(' ')[1])

