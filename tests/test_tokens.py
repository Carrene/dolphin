import time

import pytest
from nanohttp import settings, HTTPStatus

from dolphin.tokens import OrganizationInvitationToken
from .helpers import LocalApplicationTestCase


class TestTokens(LocalApplicationTestCase):

    def test_invitaion_token(self):

        # Create access token using dump and load methods
        payload = dict(a=1, b=2)
        invitation_token = OrganizationInvitationToken(payload)
        dump = invitation_token.dump()
        load = OrganizationInvitationToken.load(dump.decode())
        assert load.payload == payload

        # Trying to load token using bad signature token
        with pytest.raises(
            HTTPStatus('626 Malformed Token').__class__
        ):
            load = OrganizationInvitationToken.load('token')

        # Trying to load token when token is expired
        with pytest.raises(
            HTTPStatus('627 Token Expired').__class__
        ):
            settings.organization_invitation.max_age = 0.3
            invitation_token = OrganizationInvitationToken(payload)
            dump = invitation_token.dump()
            time.sleep(1)
            load = OrganizationInvitationToken.load(dump.decode())

