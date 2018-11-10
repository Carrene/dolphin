from bddrest.authoring import status, when, Remove, Update

from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, oauth_server_status


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

                with oauth_server_status('404 Not Found'):
                    when('Chat server is not found')
                    assert status == '619 CAS Server Not Found'

                with oauth_server_status('503 Service Unavailable'):
                    when('Chat server is not available')
                    assert status == '802 CAS Server Not Available'

                with oauth_server_status(
                    '605 We Don\'t Recognize This Application'
                ):
                    when('Application ID in configuration is invalid')
                    assert status == '620 Invalid Application ID'

                with oauth_server_status('608 Malformed Secret'):
                    when('Application Secret is manipulated')
                    assert status == '621 Invalid Secret'

                with oauth_server_status('609 Token Expired'):
                    when('Token is expired')
                    assert status == 401

                with oauth_server_status('610 Malformed Access Token'):
                    when('Access token is manipulated')
                    assert status == 401

