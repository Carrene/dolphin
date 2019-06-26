from auditor.context import Context as AuditLogContext
from bddrest import status, when, response
from nanohttp import context
from nanohttp.contexts import Context

from dolphin.models import Issue, Project, Member, Workflow, Group, Release, \
    Subscription
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


class TestIssue(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(member)
        session.commit()

        workflow = Workflow(title='Default')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member,
            room_id=0,
            group=group,
        )

        project = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project)

        with Context(dict()):
            context.identity = member

            cls.issue1 = Issue(
                project=project,
                title='First issue',
                description='This is description of first issue',
                kind='feature',
                days=1,
                room_id=2
            )
            session.add(cls.issue1)

            cls.issue2 = Issue(
                project=project,
                title='Second issue',
                description='This is description of second issue',
                kind='feature',
                days=2,
                room_id=3
            )
            session.add(cls.issue2)

            cls.issue3 = Issue(
                project=project,
                title='Third issue',
                description='This is description of third issue',
                kind='feature',
                days=3,
                room_id=4
            )
            session.add(cls.issue2)

            session.flush()
            subscription1 = Subscription(
                member_id=member.id,
                subscribable_id=cls.issue2.id,
                one_shot=True,
            )
            session.add(subscription1)
            session.commit()

    def test_subscribe(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Subscribe an issue',
            f'/apiv1/issues/id: {self.issue1.id}',
            'SUBSCRIBE',
        ):
            assert status == 200
            assert response.json['id'] == self.issue1.id

            when(
                'There is a subscription between member and issue '
                'but not subscribed yet',
                url_parameters=dict(id=self.issue2.id),
            )
            assert status == 200

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
            )
            assert status == 404

            when(
                'Intended issue with integer type not found',
                url_parameters=dict(id=100),
            )
            assert status == 404

            when(
                'There is parameter in form',
                form=dict(parameter='Any parameter')
            )
            assert status == '709 Form Not Allowed'

            when(
                'Issue is already subscribed',
                url_parameters=dict(id=3),
            )
            assert status == '611 Already Subscribed'

            when('Request is not authorized',authorization=None)
            assert status == 401

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    url_parameters=dict(id=self.issue3.id)
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    url_parameters=dict(id=self.issue3.id)
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    url_parameters=dict(id=self.issue3.id)
                )
                assert status == '801 Chat Server Internal Error'

            with chat_server_status('604 Already Added To Target'):
                when(
                    'Member is already added to room',
                    url_parameters=dict(id=self.issue3.id)
                )
                assert status == 200

