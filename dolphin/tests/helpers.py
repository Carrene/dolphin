from contextlib import contextmanager
from os import path

from auditor import MiddleWare
from nanohttp import RegexRouteController, json, settings, context, HTTPStatus
from restfulpy.application import Application
from restfulpy.orm.metadata import FieldInfo
from restfulpy.testing import ApplicableTestCase, db

from .mockup import mockup_http_server
from dolphin import Dolphin
from dolphin.authentication import Authenticator
from dolphin.models import Member, Project, Release, Issue, Item, \
    Organization, Invitation, Group, Workflow


HERE = path.abspath(path.dirname(__file__))
DATA_DIRECTORY = path.abspath(path.join(HERE, '../../data'))


_chat_server_status = 'idle'
_oauth_server_status = 'idle'


member_id = FieldInfo(type_=int, not_none=True, required=True).to_json()
workflow_id = FieldInfo(type_=int, not_none=True, required=True).to_json()
phase_id = FieldInfo(type_=int, not_none=True, required=True).to_json()
project_id = FieldInfo(type_=int, not_none=True, required=True).to_json()
email=FieldInfo(type_=str, required=True, not_none=True).to_json()
title=FieldInfo(type_=str, required=True, not_none=True).to_json()
role=FieldInfo(type_=str, required=True, not_none=True).to_json()

release_fields = Release.json_metadata()['fields']
project_fields = Project.json_metadata()['fields']
issue_fields = Issue.json_metadata()['fields']
invitation_fields = Invitation.json_metadata()['fields']

issue_fields.update({
    'phaseId': phase_id,
    'projectId': project_id,
    'memberId': member_id
})
project_fields.update({'memberId': member_id, 'workflowId': workflow_id})
release_fields.update({'memberId': member_id})
organization_fields = Organization.json_metadata()['fields']
organization_fields.update(dict(
    email=email,
    role=role,
    title=title,
))


def callback(audit_logs):
    pass


class LocalApplicationTestCase(ApplicableTestCase):
    __application__ = MiddleWare(Dolphin(), callback)
    __story_directory__ = path.join(DATA_DIRECTORY, 'stories')
    __api_documentation_directory__ = path.join(DATA_DIRECTORY, 'markdown')
    __metadata__ = {
        r'^/apiv1/releases.*': release_fields,
        r'^/apiv1/projects.*': project_fields,
        r'^/apiv1/issues.*': issue_fields,
        r'^/apiv1/items.*': Item.json_metadata()['fields'],
        r'^/apiv1/members.*': Member.json_metadata()['fields'],
        r'^/apiv1/organizations.*': organization_fields,
        r'^/apiv1/invitations.*': invitation_fields,
    }
    __configuration__ = '''
            issue:
              subscription:
                max_length: 5
        '''

    def login(self, email, organization_id=None):
        session = self.create_session()
        member = session.query(Member).filter(Member.email == email).one()
        principal = member.create_jwt_principal()
        principal.payload['organizationId'] = organization_id
        token = principal.dump()
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

            if _oauth_server_status != 'idle':
                raise HTTPStatus(_oauth_server_status)

            if code.startswith('authorization code 2'):
                return dict(accessToken='access token 2', memberId=2)

            return dict(accessToken='access token', memberId=1)

        @json
        def get(self):
            access_token = context.environ['HTTP_AUTHORIZATION']

            if 'access token 2' in access_token:
                return dict(
                    id=2,
                    title='member2',
                    email='member2@example.com',
                    avatar='avatar2',
                    name='full name'
                )

            if 'access token' in access_token:
                return dict(
                    id=1,
                    title='member1',
                    email='member1@example.com',
                    avatar='avatar1',
                    name='full name'
                )

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
                ('/apiv1/targets', self.list_),
                ('/apiv1/members', self.ensure),
            ])

        @json(verbs=['create', 'delete', 'add', 'kick', 'list', 'subscribe'])
        def create(self):
            if _chat_server_status == '615 Room Already Exists' and \
                    context.method == 'list':
                return [dict(id=1, title='First chat room')]

            if _chat_server_status == '604 Already Added To Target' and \
                    context.method in ('create'):
                return dict(id=10, title='New Room')

            if _chat_server_status == '604 Already Added To Target' and \
                    context.method in ('add'):
                raise HTTPStatus(_chat_server_status)

            if _chat_server_status == '615 Room Already Exists' and \
                    context.method == 'add':
                return dict(id=10, title='New Room')

            if _chat_server_status != 'idle':
                raise HTTPStatus(_chat_server_status)

            if context.method == 'subscribe':
                return [dict(id=1, title='First chat room')]

            return dict(id=1, title='First chat room')

        @json
        def ensure(self):
            if _chat_server_status != 'idle':
                raise HTTPStatus(_chat_server_status)

            return dict(id=1, title='member1', email='member@example.com')

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


@contextmanager
def oauth_server_status(status):
    global _oauth_server_status
    _oauth_server_status = status
    yield
    _oauth_server_status = 'idle'


def create_group(title='already exist'):
    group = Group(
        title=title,
    )
    return group


def create_workflow(title='already exist'):
    workflow = Workflow(
        title=title,
    )
    return workflow

