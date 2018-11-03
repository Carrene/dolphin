from bddrest import status, when, given, response

from dolphin.models import Issue, Project, Member, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


class TestIssue(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )

        workflow = Workflow(title='First Workflow')

        project = Project(
            member=member,
            workflow=workflow,
            title='My first project',
            description='A decription for my project',
            room_id=1
        )
        session.add(project)

        issue1 = Issue(
            project=project,
            title='First issue',
            description='This is description of first issue',
            due_date='2020-2-20',
            kind='feature',
            days=1,
            room_id=2
        )
        session.add(issue1)

        issue2 = Issue(
            project=project,
            title='Second issue',
            description='This is description of second issue',
            due_date='2020-2-20',
            kind='feature',
            days=2,
            room_id=3
        )
        session.add(issue2)
        session.commit()

    def test_subscribe(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Subscribe an issue',
            '/apiv1/issues/id:2',
            'SUBSCRIBE',
        ):
            assert status == 200
            assert response.json['id'] == 2

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
                url_parameters=dict(id=2),
            )
            assert status == '611 Already Subscribed'

            when('Request is not authorized',authorization=None)
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

            with chat_server_status('604 Already Added To Target'):
                when(
                    'Member is already added to room',
                    url_parameters=dict(id=3)
                )
                assert status == 200

