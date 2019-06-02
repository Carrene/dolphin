from contextlib import contextmanager

from bddrest import when, response, status, given
from nanohttp import RegexRouteController, settings, context, json
from nanohttp.contexts import Context
from restfulpy.mockup import mockup_http_server, MockupApplication
from auditor.context import Context as AuditLogContext

from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Issue, Project, Member, Workflow, Item, Phase, \
    Group, Subscription, Release, Skill, Organization, Tag


accesstoken = '5391b0c60b7d2d1bfb0f73d18f82313c9fce9995'

@contextmanager
def github_mockup_server():
    class GithubMockupServer(RegexRouteController):
        def __init__(self):
            super().__init__([
                (
                    'repos/Carrene/wolf/issues',
                    self.create_issue
                ),
#                (
#                    'http://api.githup.com/repos/my-orgs/myrepos/issues/num/assignees',
#                     self.assigne
#                ),
            ])

        @json(verbs='POST')
        def create_issue(self, id):
            import pudb; pudb.set_trace()  # XXX BREAKPOINT
            json = context.form.get('json')
            if json['title'] is None:
                return '400 Bad request'

            return json

    app = MockupApplication('github_mockup', GithubMockupServer())
    with mockup_http_server(app) as (server, url):
        settings.merge(f'''
            github:
              base_url: {url}
        ''')
        yield app


class TestGithub(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        cls.organization = Organization(
            title='organization title',
        )
        session.add(cls.organization)
        session.flush()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(cls.member)

        cls.tag1 = Tag(
            title='First tag',
            organization_id=cls.organization.id,
        )
        session.add(cls.tag1)
        session.flush()

        cls.tag2 = Tag(
            title='Second tag',
            organization_id=cls.organization.id,
        )
        session.add(cls.tag2)
        session.flush()

        workflow = Workflow(title='Default')
        skill = Skill(title='First Skill')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member,
            room_id=0,
            group=group,
        )

        cls.project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )

        with Context(dict()):
            context.identity = cls.member

            cls.issue1 = Issue(
                project=cls.project,
                title='First issue',
                description='This is description of first issue',
                status='in-progress',
                due_date='2020-2-20',
                kind='feature',
                days=1,
                room_id=2,
            )
            session.add(cls.issue1)

        session.commit()

    def test_create_issue(self):
        self.login(self.member.email)

        with oauth_mockup_server(), github_mockup_server(), self.given(
            'Create issue',
            f'/apiv1/issues/id: {self.issue1.id}',
            'TRANSFER',
            json={
                'repositories': {
                    'Carrene/wolf': {
                        'title': 'First title',
                        'body': 'Issue body',
                    }
                }
            }
        ):
            assert status == 200

   # def test_assign_issue():
   #     git = Github(accesstoken, 'send-message')
   #     response = git.assign_issue(
   #         'smarthomeofus',
   #         '1',
   #         ['farzaneka']
   #     )
   #     assert response.status_code in [200, 201, 204]

   # def test_list_repository():
   #     git = Github(accesstoken, 'send-message')
   #     response = git.list_repository(
   #         'smarthomeofus'
   #     )
   #     assert response.status_code in [200, 201, 204]

   # def test_list_orgamization_member():
   #     git = Github(accesstoken, 'send-message')
   #     response = git.list_organizationmember(
   #         'smarthomeofus'
   #     )
   #     assert response.status_code in [200, 201, 204]

