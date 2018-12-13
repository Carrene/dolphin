import itsdangerous
from nanohttp import settings
from restfulpy.principal import BaseJwtPrincipal

from .exceptions import HTTPTokenExpired, HTTPMalformedToken


class OrganizationInvitationToken(BaseJwtPrincipal):

    @classmethod
    def load(cls, token):
        try:
            return super().load(token)

        except itsdangerous.SignatureExpired:
            raise HTTPTokenExpired()

        except itsdangerous.BadSignature:
            raise HTTPMalformedToken()

    @classmethod
    def get_config(cls):
        return settings.organization_invitation

    @property
    def email(self):
        return self.payload.get('email')

    @property
    def organization_id(self):
        return self.payload.get('organizationId')

    @property
    def by_member_reference_id(self):
        return self.payload.get('byMemberReferenceId')

    @property
    def role(self):
        return self.payload.get('role')
