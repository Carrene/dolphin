from bddrest import status, when, given, response

from dolphin.models import Container, Member, Release, Subscription, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status


class TestContainer(LocalApplicationTestCase):

    @classmethod
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

        workflow1 = Workflow(title='First Workflow')

        container1 = Container(
            member=member,
            workflow=workflow1,
            title='My first container',
            description='A decription for my container',
            room_id=1001
        )
        session.add(container1)
        session.flush()

        container2 = Container(
            member=member,
            workflow=workflow1,
            title='My second container',
            description='A decription for my container',
            room_id=1002
        )
        session.add(container2)
        session.flush()

        subscription1 = Subscription(
            subscribable=container1.id,
            member=member.id
        )
        session.add(subscription1)

        subscription2 = Subscription(
            subscribable=container2.id,
            member=member.id
        )
        session.add(subscription2)
        session.commit()

    def test_unsubscribe(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Unsubscribe an container',
            '/apiv1/containers/id:1',
            'UNSUBSCRIBE',
        ):
            assert status == 200
            assert response.json['id'] == 1
            assert response.json['isSubscribed'] == False

            when(
                'Intended container with string type not found',
                url_parameters=dict(id='Alphabetical'),
            )
            assert status == 404

            when(
                'Intended container with integer type not found',
                url_parameters=dict(id=100),
            )
            assert status == 404

            when(
                'Issue is not subscribed yet',
                url_parameters=dict(id=1),
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
                    url_parameters=dict(id=2)
                )
                assert status == '617 Chat Server Not Found'

            with chat_server_status('503 Service Not Available'):
                when(
                    'Chat server is not available',
                    url_parameters=dict(id=2)
                )
                assert status == '800 Chat Server Not Available'

            with chat_server_status('500 Internal Service Error'):
                when(
                    'Chat server faces with internal error',
                    url_parameters=dict(id=2)
                )
                assert status == '801 Chat Server Internal Error'

            with chat_server_status('611 Room Member Not Found'):
                when(
                    'Room member not found',
                    url_parameters=dict(id=2)
                )
                assert status == 200

