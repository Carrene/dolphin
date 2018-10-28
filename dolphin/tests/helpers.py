from contextlib import contextmanager
from os import path

from nanohttp import RegexRouteController, json, settings, context, HTTPStatus
from restfulpy.application import Application
from restfulpy.mockup import mockup_http_server
from restfulpy.testing import ApplicableTestCase
from restfulpy.orm.metadata import FieldInfo

from dolphin import Dolphin
from dolphin.authentication import Authenticator
from dolphin.models import Member, Project, Release, Issue, Item


HERE = path.abspath(path.dirname(__file__))
DATA_DIRECTORY = path.abspath(path.join(HERE, '../../data'))


_chat_server_status = 'idle'


member_id = FieldInfo(type_=int, not_none=True, required=True).to_json()
workflow_id = FieldInfo(type_=int, not_none=True, required=True).to_json()
resource_id = FieldInfo(type_=int, not_none=True, required=True).to_json()
phase_id = FieldInfo(type_=int, not_none=True, required=True).to_json()
project_id = FieldInfo(type_=int, not_none=True, required=True).to_json()

release_fields = Release.json_metadata()['fields']
project_fields = Project.json_metadata()['fields']
issue_fields = Issue.json_metadata()['fields']

issue_fields.update({
    'resourceId': resource_id,
    'phaseId': phase_id,
    'projectId': project_id,
    'memberId': member_id
})
project_fields.update({'memberId': member_id, 'workflowId': workflow_id})
release_fields.update({'memberId': member_id})


class LocalApplicationTestCase(ApplicableTestCase):
    __application_factory__ = Dolphin
    __story_directory__ = path.join(DATA_DIRECTORY, 'stories')
    __api_documentation_directory__ = path.join(DATA_DIRECTORY, 'markdown')
    __metadata__ = {
        r'^/apiv1/releases.*': release_fields,
        r'^/apiv1/projects.*': project_fields,
        r'^/apiv1/issues.*': issue_fields,
        r'^/apiv1/items.*': Item.json_metadata()['fields'],
        r'^/apiv1/members.*': Member.json_metadata()['fields'],
    }

    def login(self, email):
        session = self.create_session()
        member = session.query(Member).filter(Member.email == email).one()
        token = member.create_jwt_principal().dump()
        self._authentication_token = token.decode('utf-8')


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
                ('/apiv1/accesstokens', self.create),
                ('/apiv1/members/me', self.get),
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

            if 'access token' in access_token:
                return dict(id=1, title='member1', email='member1@example.com')

            raise HTTPForbidden()

    app = MockupApplication('root', Root())
    with mockup_http_server(app) as (server, url):
        settings.merge(f'''
            tokenizer:
              url: {url}
            oauth:
              secret: oauth2-secret
              application_id: 1
              url: {url}
        ''')
        yield app


@contextmanager
def chat_mockup_server():
    class Root(RegexRouteController):
        def __init__(self):
            super().__init__([
                ('/apiv1/rooms', self.create),
                ('/apiv1/targets', self.list_)
            ])

        @json(verbs=['create', 'delete', 'add', 'kick', 'list'])
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

            if _chat_server_status != 'idle':
                raise HTTPStatus(_chat_server_status)

            return dict(id=1, title='First chat room')

        @json
        def list_(self):
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

        @json(verbs=['add', 'kick'])
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

