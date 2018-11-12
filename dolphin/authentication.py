from cas import CASPrincipal
from nanohttp import HTTPStatus, HTTPUnauthorized
from restfulpy.authentication import StatefulAuthenticator
from restfulpy.orm import DBSession

from .backends import CASClient
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
        principal = CASPrincipal.load(encoded_token)

        member = DBSession.query(Member) \
            .filter(Member.reference_id == principal.reference_id) \
            .one_or_none()
        if not member:
            raise HTTPUnauthorized()

        cas_member = CASClient().get_member(member.access_token)

        # FIXME: If any item added to scopes, the additional scopes item must
        # be considered here
        if member.title != cas_member['title']:
            member.title = cas_member['title']

        if member.avatar != cas_member['avatar']:
            member.avatar = cas_member['avatar']

        DBSession.commit()
        return principal

