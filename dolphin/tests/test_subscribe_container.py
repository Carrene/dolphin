from bddrest import status, response, Update, when, Remove, given

from dolphin.models import Container, Member, Release, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, \
    oauth_mockup_server, chat_mockup_server, chat_server_status, \
    room_mockup_server


class TestContainer(LocalApplicationTestCase):

    @classmethod
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

        container1 = Container(
            member=member1,
            title='My first container',
            description='A decription for my container',
            room_id=1001
        )
        session.add(container1)

        container2 = Container(
            member=member1,
            title='My second container',
            description='A decription for my container',
            room_id=1002
        )
        session.add(container2)
        session.commit()

    def test_subscribe(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), chat_mockup_server(), self.given(
            'Subscribe container',
            '/apiv1/containers/id:1',
            'SUBSCRIBE',
        ):
            assert status == 200
            assert response.json['id'] == 1
            assert response.json['isSubscribed'] == True

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
                'Container is already subscribed',
                url_parameters=dict(id=1),
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

            with room_mockup_server():
                when(
                    'Room member is already added to room',
                    url_parameters=dict(id=2)
                )
                assert status == 200

