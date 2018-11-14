from bddrest import status, when, response

from dolphin.models import Container, Member, Workflow
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


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

        hidden_container = Container(
            member=member1,
            title='My hidden container',
            description='A decription for my container',
            removed_at='2020-2-20',
            room_id=1000
        )
        session.add(hidden_container)
        session.commit()

    def test_show(self):
        self.login('member1@example.com')

        with oauth_mockup_server(), self.given(
            'Showing a unhidden container',
            '/apiv1/containers/id:2',
            'SHOW'
        ):
            assert status == 200
            assert response.json['removedAt'] == None

            when(
                'Container not found',
                url_parameters=dict(id=100)
            )
            assert status == 404

            when(
                'Intended issue with string type not found',
                url_parameters=dict(id='Alphabetical'),
            )
            assert status == 404

            when(
                'There is parameter is form',
                form=dict(any_parameter='A parameter in the form')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

