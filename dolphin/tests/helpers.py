from contextlib import contextmanager
from os import path

from cas import CASPrincipal
from nanohttp import RegexRouteController, json, settings, context, \
    HTTPStatus, HTTPUnauthorized
from restfulpy.application import Application
from restfulpy.mockup import mockup_http_server
from restfulpy.testing import ApplicableTestCase

from dolphin import Dolphin
from dolphin.authentication import Authenticator
from dolphin.models import Member


HERE = path.abspath(path.dirname(__file__))
DATA_DIRECTORY = path.abspath(path.join(HERE, '../../data'))


_chat_server_status = 'idle'


class LocalApplicationTestCase(ApplicableTestCase):
    __application_factory__ = Dolphin
    __story_directory__ = path.join(DATA_DIRECTORY, 'stories')
    __api_documentation_directory__ = path.join(DATA_DIRECTORY, 'markdown')

    def login(self, email, url='/apiv1/tokens', verb='CREATE'):
        session = self.create_session()
        member = session.query(Member).filter(Member.email == email).one_or_none()
        if member is None:
            raise HTTPUnauthorized()

        token = CASPrincipal({
            'id':member.id,
            'referenceId':member.reference_id,
            'email':member.email,
            'roles':['member'],
            'name':member.title
        })
        self._authentication_token = token.dump().decode('utf-8')


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
                ('/apiv1/tokens', self.create),
                ('/apiv1/profiles/me', self.get),
            ])

        @json
        def create(self):
            code = context.form.get('code')
            if not code.startswith('authorization code'):
                return dict(accessToken='token is damage', memberId=1)

            return dict(accessToken='access token', memberId=1)

        @json
        def get(self):
            access_token = context.environ['HTTP_AUTHORIZATION']

            if 'access token 1' in access_token:
                return dict(id=1, title='manager1', email='manager1@example.com')

            if 'access token 2' in access_token:
                return dict(id=2, title='manager2', email='manager2@example.com')

            if 'access token 3' in access_token:
                return dict(id=3, title='manager3', email='manager3@example.com')

            if 'access token 4' in access_token:
                return dict(id=4, title='manager4', email='manager4@example.com')

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
                url: {url}/apiv1/tokens
                verb: create
              member:
                url: {url}/apiv1/profiles
                verb: get
        ''')
        yield app


@contextmanager
def chat_mockup_server():
    class Root(RegexRouteController):
        def __init__(self):
            super().__init__([
                ('/apiv1/rooms', self.create),
            ])

        @json(verbs=['create', 'delete', 'add', 'remove', 'list'])
        def create(self):
            if _chat_server_status == '615 Room Already Exists' and \
                    context.method == 'list':
                return [dict(id=1, title='First chat room')]

            if _chat_server_status == '604 Already Added To Target' and \
                    context.method in ('create', 'add'):
                return dict(id=10, title='New Room')

            if _chat_server_status == '615 Room Already Exists' and \
                    context.method == 'add':
                return dict(id=10, title='New Room')

            if _chat_server_status == '615 Room Already Exists' and \
                    context.method == 'list':
                return [dict(id=1, title='First chat room')]

            if _chat_server_status != 'idle':
                raise HTTPStatus(_chat_server_status)

            return dict(id=1, title='First chat room')

    app = MockupApplication('chat-server', Root())
    with mockup_http_server(app) as (server, url):
        settings.merge(f'''
            chat:
              room:
                url: {url}
        ''')
        yield app


@contextmanager
def room_mockup_server():
    class Root(RegexRouteController):
        _status = '604 Already Added To Target'

        def __init__(self):
            super().__init__([
                ('/apiv1/rooms', self.add),
            ])

        @json(verbs=['add', 'remove'])
        def add(self):
            temp_status = self._status
            self._status = '611 User Not Found'
            raise HTTPStatus(temp_status)


    app = MockupApplication('chat-server', Root())
    with mockup_http_server(app) as (server, url):
        settings.merge(f'''
            chat:
              room:
                url: {url}
        ''')
        yield app


@contextmanager
def chat_server_status(status):
    global _chat_server_status
    _chat_server_status = status
    yield
    _chat_server_status = 'idle'

