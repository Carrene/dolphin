from nanohttp import context
from nanohttp.contexts import Context
from bddrest.authoring import status, response, when, given
from auditor.context import Context as AuditLogContext

from dolphin.models import Member, Release, Project, Issue, Group, Workflow, \
    Skill, Subscription
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()
        cls.member = Member(
            email='member@example.com',
            title='member',
            access_token='access token 1',
            reference_id=2
        )
        session.add(cls.member)
        session.commit()

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
                kind='feature',
                days=1,
                room_id=2,
            )
            session.add(cls.issue1)

            cls.issue2 = Issue(
                project=cls.project,
                title='Second issue',
                description='This is description of second issue',
                kind='feature',
                days=2,
                room_id=3,
            )
            session.add(cls.issue2)

            cls.issue3 = Issue(
                project=cls.project,
                title='Third issue',
                description='This is description of third issue',
                kind='feature',
                days=3,
                room_id=4,
            )
            session.add(cls.issue3)

            cls.issue4 = Issue(
                project=cls.project,
                title='Fourth issue',
                description='This is description of fourth issue',
                kind='feature',
                days=3,
                room_id=4,
            )
            session.add(cls.issue4)
            session.flush()

            subscription1 = Subscription(
                subscribable_id=cls.issue1.id,
                member_id=cls.member.id,
            )
            session.add(subscription1)
            session.commit()

    def test_search_issue(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            'Search for a issue by submitting form',
            '/apiv1/issues',
            'SEARCH',
            form=dict(query='Fir'),
        ):
            assert status == 200
            assert len(response.json) == 1
            assert response.json[0]['title'] == self.issue1.title

            when('Search without query parameter', form=given - 'query')
            assert status == '912 Query Parameter Not In Form Or Query String'

            when(
                'Search string must be less than 20 charecters',
                form=given | dict(query=(50 + 1) * 'a')
            )
            assert status == '704 At Most 50 Characters Valid For Title'

            when(
                'Try to sort the response',
                query=dict(sort='id'),
                form=given | dict(query='issue')
            )
            assert len(response.json) == 4
            assert response.json[0]['id'] < response.json[1]['id']

            when(
                'Trying ro sort the response in descend ordering',
                query=dict(sort='-id'),
                form=given | dict(query='issue')
            )
            assert len(response.json) == 4
            assert response.json[0]['id'] > response.json[1]['id']

            when('Filtering the response', query=dict(title=self.issue1.title))
            assert len(response.json) == 1
            assert response.json[0]['title'] == self.issue1.title

            when(
                'Trying to filter the response ignoring the title',
                query=dict(title=f'!{self.issue1.title}'),
                form=given | dict(query='issue')
            )
            assert len(response.json) == 3

            when(
                'Testing pagination',
                query=dict(take=1, skip=1),
                form=given | dict(query='issue')
            )
            assert len(response.json) == 1

            when(
                'Sort before pagination',
                query=dict(sort='-id', take=3, skip=1),
                form=given | dict(query='issue')
            )
            assert len(response.json) == 3
            assert response.json[0]['id'] > response.json[1]['id']

            when(
                'Filtering unread issues',
                query=dict(unread='true'),
                form=given | dict(query='issue')
            )
            assert len(response.json) == 1
            assert response.json[0]['id'] == self.issue1.id

    def test_request_with_query_string(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            'Test request using query string',
            '/apiv1/issues',
            'SEARCH',
            query=dict(query='Sec')
        ):
            assert status == 200
            assert len(response.json) == 1

            when('An unauthorized search', authorization=None)
            assert status == 401

