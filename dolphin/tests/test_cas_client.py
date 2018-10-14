from bddrest.authoring import status, when, Remove, Update

from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestToken(LocalApplicationTestCase):

    def test_get_access_token(self):
        with oauth_mockup_server(), self.given(
                'Try to get an access token from CAS',
                '/apiv1/oauth2/tokens',
                'OBTAIN',
                form=dict(authorizationCode='authorization code')
            ):
                assert status == 200

                when(
                    'Trying to pass without the authorization code parameter',
                    form=Remove('authorizationCode')
                )
                assert status == 403

                when(
                    'Trying to pass with damage authorization code',
                    form=Update(authorizationCode='token is damage')
                )
                assert status == 403

