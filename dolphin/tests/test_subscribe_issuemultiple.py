from datetime import datetime

from nanohttp import context
from nanohttp.contexts import Context
from auditor.context import Context as AuditLogContext
from bddrest.authoring import response, when, Update, Remove, status

from dolphin.models import Member, Issue, Workflow, Group, Project, \
    Release, Subscription
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


class TestSubscribeIssues(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()
        cls.member1 = Member(
            email='member1@example.com',
            title='member1',
            access_token='access token1',
            reference_id=2
        )
        session.add(cls.member1)

        cls.member2 = Member(
            email='member2@example.com',
            title='member2',
            access_token='access token2',
            reference_id=3
        )
        session.add(cls.member2)
        session.flush()

        workflow = Workflow(title='Default')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=cls.member1,
            room_id=0,
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=cls.member1,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project)

        with Context(dict()):
            context.identity = cls.member1

            cls.issue1 = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
                due_date='2020-2-20',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue1)
            session.flush()

            subscription_issue1 = Subscription(
                subscribable_id=cls.issue1.id,
                member_id=cls.member2.id,
                seen_at=datetime.utcnow(),
            )
            session.add(subscription_issue1)

            cls.issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of second issue',
                due_date='2016-2-20',
                kind='feature',
                days=2,
                room_id=3
            )
            session.add(cls.issue2)

            cls.issue3 = Issue(
                project=project,
                title='Third issue',
                description='This is description of third issue',
                due_date='2020-2-20',
                kind='feature',
                days=3,
                room_id=4,
            )
            session.add(cls.issue3)

            cls.issue4 = Issue(
                project=project,
                title='Fourth issue',
                description='This is description of fourth issue',
                due_date='2020-2-20',
                kind='feature',
                days=3,
                room_id=5,
            )
            session.add(cls.issue4)

            cls.issue5 = Issue(
                project=project,
                title='Fifth issue',
                description='This is description of fifth issue',
                due_date='2020-2-20',
                kind='feature',
                days=3,
                room_id=6,
            )
            session.add(cls.issue5)

            cls.issue6 = Issue(
                project=project,
                title='Sixth issue',
                description='This is description of sixth issue',
                due_date='2020-2-20',
                kind='feature',
                days=3,
                room_id=7,
            )
            session.add(cls.issue6)
            session.commit()

    def test_subscribe_multiple_issues(self):
         self.login('member1@example.com')
         issues = (str(i) for i in range(self.issue1.id, self.issue6.id))
         issues_string = ', '.join(issues)

         with oauth_mockup_server(), chat_mockup_server(), self.given(
             'Subscribe multiple issues',
             f'/apiv1/issues?id=IN({self.issue2.id},{self.issue3.id})',
             'SUBSCRIBE',
         ):
             assert status == 200
             assert len(response.json) == 2
             assert response.json[0]['title'] == self.issue2.title

             when(
                 'The number of issues to subscribe is more than limit',
                 query=dict(id=f'IN({issues_string})')
             )
             assert status == '776 Maximum 5 Issues To Subscribe At A Time'

             when('Try to pass unauthorize request', authorization=None)
             assert status == 401

             with chat_server_status('404 Not Found'):
                 when('Chat server is not found')
                 assert status == '617 Chat Server Not Found'

             with chat_server_status('503 Service Not Available'):
                 when('Chat server is not available')
                 assert status == '800 Chat Server Not Available'

             with chat_server_status('500 Internal Service Error'):
                 when('Chat server faces with internal error')
                 assert status == '801 Chat Server Internal Error'

             with chat_server_status(
                 '716 Maximum 100 Rooms To Subscribe At A Time'
             ):
                 when('Number of requesed rooms to subscribe is more tha limit')
                 assert status == '804 Number Of Chat Room Subscription Is ' \
                     'Out Of Limit'

