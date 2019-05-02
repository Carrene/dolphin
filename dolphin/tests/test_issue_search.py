from nanohttp import context
from nanohttp.contexts import Context
from bddrest.authoring import status, response
from auditor.context import Context as AuditLogContext

from dolphin.models import Member, Release, Project, Issue, Group, Workflow, \
    Skill
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

            cls.issue2 = Issue(
                project=cls.project,
                title='Second issue',
                description='This is description of second issue',
                status='to-do',
                due_date='2016-2-20',
                kind='feature',
                days=2,
                room_id=3,
            )
            session.add(cls.issue2)

            cls.issue3 = Issue(
                project=cls.project,
                title='Third issue',
                description='This is description of third issue',
                status='on-hold',
                due_date='2020-2-20',
                kind='feature',
                days=3,
                room_id=4,
            )
            session.add(cls.issue3)

            cls.issue4 = Issue(
                project=cls.project,
                title='Fourth issue',
                description='This is description of fourth issue',
                status='complete',
                due_date='2020-2-20',
                kind='feature',
                days=3,
                room_id=4,
            )
            session.add(cls.issue4)
        session.commit()

    def test_search_user(self):
        self.login(self.member.email)

        import pudb; pudb.set_trace()  # XXX BREAKPOINT
        with oauth_mockup_server(), self.given(
            'Search for a issue by submitting form',
            '/apiv1/issues',
            'SEARCH',
            form=dict(query='First'),
        ):
            assert status == 200
            assert response.json[0]['title'] == self.user2.title
            assert len(response.json) == 2

#            when('Search using email', form=Update(query='exam'))
#            assert status == 200
#            assert len(response.json) == 1
#
#            when('Search without query parameter', form=Remove('query'))
#            assert status == '708 Search Query Is Required'
#
#            when(
#                'Search string must be less than 20 charecters',
#                form=Update(
#                    query= \
#                        'The search string should be less than 20 charecters'
#                )
#            )
#            assert status == '702 Must Be Less Than 20 Charecters'
#
#            when('Try to sort the respone', query=dict(sort='id'))
#            assert len(response.json) == 2
#            assert response.json[0]['id'] == 1
#
#            when(
#                'Trying ro sort the response in descend ordering',
#                 query=dict(sort='-id')
#            )
#            assert response.json[0]['id'] == 2
#
#            when('Filtering the response', query=dict(title='user2'))
#            assert len(response.json) == 1
#            assert response.json[0]['title'] == 'user2'
#
#            when(
#                'Trying to filter the response ignoring the title',
#                 query=dict(title='!user2')
#            )
#            assert len(response.json) == 1
#            assert response.json[0]['title'] != 'user2'
#
#            when('Testing pagination', query=dict(take=1, skip=1))
#            assert len(response.json) == 1
#            assert response.json[0]['title'] == self.user1.title
#
#            when(
#                'Sort before pagination',
#                query=dict(sort='-id', take=3, skip=1)
#            )
#            assert len(response.json) == 1
#            assert response.json[0]['title'] == 'user1'
#
#    def test_request_with_query_string(self):
#        self.login('user1@example.com')
#
#        with cas_mockup_server(), self.given(
#            'Test request using query string',
#            '/apiv1/members',
#            'SEARCH',
#            query=dict(query='user')
#        ):
#            assert status == 200
#            assert len(response.json) == 2
#
#            when('An unauthorized search', authorization=None)
#            assert status == 401
#
#
