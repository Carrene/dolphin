from contextlib import contextmanager

from bddrest.authoring import status, when, Remove, Update, response
from nanohttp import RestController, json, settings, context, HTTPForbidden
from restfulpy.mockup import mockup_http_server

from dolphin.tests.helpers import LocalApplicationTestCase, MockupApplication


class Token(RestController):
    @json
    def create(self):
        code = context.form.get('code')

        if not code.startswith('authorization code'):
            return dict(accessToken='token is damage', memberId=1)

        return dict(accessToken='access token', memberId=1)


class Profile(RestController):
    @json
    def get(self, id):
        access_token = context.environ['HTTP_AUTHORIZATION']

        if access_token.startswith('oauth2-accesstoken access token'):
            return dict(id=1, title='john', email='john@gmail.com')

        raise HTTPForbidden()


class Root(RestController):
    tokens = Token()
    profiles = Profile()


@contextmanager
def oauth_mockup_server(root_controller):
    app = MockupApplication('root', root_controller)
    with mockup_http_server(app) as (server, url):
        settings.merge(f'''
            tokenizer:
              url: {url}
        ''')
        yield app


class TestToken(LocalApplicationTestCase):

    def test_redirect_to_cas(self):
        settings.merge(f'''
            oauth:
              application_id: 1
        ''')

        with self.given(
            'Trying to redirect to CAS server',
            '/apiv1/oauth2/tokens',
            'REQUEST',
        ):
            assert status == 200
            assert len(response.json) == 2
            assert response.json['scopes'] == ['email', 'title']

            when('Trying to pass with the form patameter', form=dict(a='a'))
            assert status == '711 Form Not Allowed'

    def test_get_access_token(self):
        with oauth_mockup_server(Root()):
            settings.merge(f'''
                oauth:
                  secret: A1dFVpz4w/qyym+HeXKWYmm6Ocj4X5ZNv1JQ7kgHBEk=\n
                  application_id: 1
                  access_token:
                    url: {settings.tokenizer.url}/tokens
                    verb: create
                  member:
                    url: {settings.tokenizer.url}/profiles
                    verb: get
            ''')

            with self.given(
                'Try to get an access token from CAS',
                '/apiv1/oauth2/tokens',
                'OBTAIN',
                form=dict(authorizationCode='authorization code')
            ):
                assert status == 200
                assert 'token' in response.json
                assert 'X-New-Jwt-Token' in response.headers

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

