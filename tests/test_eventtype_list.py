from bddrest import status, response, when

from .helpers import LocalApplicationTestCase, oauth_mockup_server
from dolphin.models import Member, EventType


class TestEventType(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=1
        )
        session.add(cls.member)

        event_type1 = EventType(
            title='Type1',
        )
        session.add(event_type1)

        event_type2 = EventType(
            title='Type2',
        )
        session.add(event_type2)
        session.commit()

    def test_list(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            'List event types',
            '/apiv1/eventtypes',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 2

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

            when('Trying to sorting response', query=dict(sort='id'))
            assert response.json[0]['id'] < response.json[1]['id']

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] > response.json[1]['id']

            when('Trying pagination response', query=dict(take=1))
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
            assert len(response.json) == 1

            when('Trying filtering response', query=dict(id=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            when('Request is not authorized', authorization=None)
            assert status == 401

