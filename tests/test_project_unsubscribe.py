from auditor.context import Context as AuditLogContext
from bddrest import status, when, response

from .helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status
from dolphin.models import Project, Member, Group, Subscription, Workflow, \
    Release


class TestProject(LocalApplicationTestCase):

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

        cls.project1 = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(cls.project1)
        session.flush()

        project2 = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member,
            title='My second project',
            description='A decription for my project',
            room_id=1002
        )
        session.add(project2)
        session.flush()

        subscription1 = Subscription(
            subscribable_id=cls.project1.id,
            member_id=member.id
        )
        session.add(subscription1)

        subscription2 = Subscription(
            subscribable_id=project2.id,
            member_id=member.id
        )
        session.add(subscription2)
        session.commit()

    def test_unsubscribe(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Unsubscribe an project',
            f'/apiv1/projects/id:{self.project1.id}',
            'UNSUBSCRIBE',
        ):
            assert status == 200
            assert response.json['id'] == self.project1.id
            assert response.json['isSubscribed'] == False

            when(
                'Intended project with string type not found',
                url_parameters=dict(id='Alphabetical'),
            )
            assert status == 404

            when(
                'Intended project with integer type not found',
                url_parameters=dict(id=100),
            )
            assert status == 404

            when(
                'Issue is not subscribed yet',
                url_parameters=dict(id=2),
            )
            assert status == '612 Not Subscribed Yet'

            when(
                'There is parameter in form',
                form=dict(parameter='Any parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

            with chat_server_status('404 Not Found'):
                when(
                    'Chat server is not found',
                    url_parameters=dict(id=3)
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    url_parameters=dict(id=3)
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    url_parameters=dict(id=3)
                )
                assert status == '801 Chat Server Internal Error'

            with chat_server_status('611 Room Member Not Found'):
                when(
                    'Room member not found',
                    url_parameters=dict(id=3)
                )
                assert status == 200

