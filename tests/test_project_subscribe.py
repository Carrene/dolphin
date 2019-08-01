from auditor.context import Context as AuditLogContext
from bddrest import status, response, when

from .helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status, \
    room_mockup_server
from dolphin.models import Project, Member, Group, Workflow, Release


class TestProject(LocalApplicationTestCase):

    @classmethod
    @AuditLogContext(dict())
    def mockup(cls):
        session = cls.create_session()

        member1 = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2
        )
        session.add(member1)

        workflow = Workflow(title='Default')
        group = Group(title='default')

        release = Release(
            title='My first release',
            description='A decription for my first release',
            cutoff='2030-2-20',
            launch_date='2030-2-20',
            manager=member1,
            room_id=0,
            group=group,
        )

        cls.project1 = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member1,
            title='My first project',
            description='A decription for my project',
            room_id=1001
        )
        session.add(cls.project1)

        project2 = Project(
            release=release,
            workflow=workflow,
            group=group,
            manager=member1,
            title='My second project',
            description='A decription for my project',
            room_id=1002
        )
        session.add(project2)
        session.commit()

    def test_subscribe(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Subscribe project',
            f'/apiv1/projects/id:{self.project1.id}',
            'SUBSCRIBE',
        ):
            assert status == 200
            assert response.json['id'] == self.project1.id
            assert response.json['isSubscribed'] == True

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
                'Project is already subscribed',
                url_parameters=dict(id=2),
            )
            assert status == '611 Already Subscribed'

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

            with room_mockup_server():
                when(
                    'Room member is already added to room',
                    url_parameters=dict(id=3)
                )
                assert status == 200

