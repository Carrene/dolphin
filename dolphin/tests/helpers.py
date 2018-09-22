from contextlib import contextmanager
from os import path

from nanohttp import RegexRouteController, json, settings, context
from restfulpy.application import Application
from restfulpy.testing import ApplicableTestCase
from restfulpy.mockup import mockup_http_server

from dolphin import Dolphin
from dolphin.authentication import Authenticator


HERE = path.abspath(path.dirname(__file__))
DATA_DIRECTORY = path.abspath(path.join(HERE, '../../data'))


class LocalApplicationTestCase(ApplicableTestCase):
    __application_factory__ = Dolphin
    __story_directory__ = path.join(DATA_DIRECTORY, 'stories')
    __api_documentation_directory__ = path.join(DATA_DIRECTORY, 'markdown')

    def login(self, email, url='/apiv1/tokens', verb='CREATE'):
        super().login(dict(email=email), url=url, verb=verb)


class MockupApplication(Application):

    def __init__(self, application_name, root):
        super().__init__(
            application_name,
            root=root
        )
        self.__authenticator__ = Authorization()


class Authorization(Authenticator):

    def validate_credentials(self, credentials):
        pass

    def create_refresh_principal(self, member_id=None):
        pass

    def create_principal(self, member_id=None, session_id=None, **kwargs):
        pass

    def authenticate_request(self):
        pass


@contextmanager
def oauth_mockup_server():
    class Root(RegexRouteController):
        def __init__(self):
            super().__init__([
                ('/tokens', self.create),
                ('/profiles', self.get),
            ])

        @json
        def create(self):
            code = context.form.get('code')
            if not code.startswith('authorization code'):
                return dict(accessToken='token is damage', memberId=1)

            return dict(accessToken='access token', memberId=1)

        @json
        def get(self, id):
            access_token = context.environ['HTTP_AUTHORIZATION']

            if access_token.startswith('oauth2-accesstoken access token'):
                return dict(title='john', email='john@gmail.com')

            raise HTTPForbidden()

    app = MockupApplication('root', Root())
    with mockup_http_server(app) as (server, url):
        settings.merge(f'''
            tokenizer:
              url: {url}
            oauth:
              secret: A1dFVpz4w/qyym+HeXKWYmm6Ocj4X5ZNv1JQ7kgHBEk=\n
              application_id: 1
              access_token:
                url: {url}/tokens
                verb: create
              member:
                url: {url}/profiles
                verb: get
        ''')
        yield app


@contextmanager
def chat_mockup_server():
    class Root(RegexRouteController):
        def __init__(self):
            super().__init__([
                ('/rooms', self.create),
            ])

        @json(verbs=['create', 'delete'])
        def create(self):
            return dict(id=1, title='First chat room')

    app = MockupApplication('jaguar-server', Root())
    with mockup_http_server(app) as (server, url):
        settings.merge(f'''
            chat:
              room:
                url: {url}
        ''')
        yield app

