import datetime

from bddrest import when, response, status

from dolphin.models import Member, Event, EventType
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestEvent(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()
        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            access_token='access token 1',
            phone=123456789,
            reference_id=2,
        )
        session.add(cls.member)

        event_type = EventType(
            title='First type',
        )

        event1 = Event(
            title='First event',
            start_date=datetime.datetime.now().isoformat(),
            end_date=datetime.datetime.now().isoformat(),
            event_type=event_type,
        )
        session.add(event1)

        event2 = Event(
            title='Second event',
            start_date=datetime.datetime.now().isoformat(),
            end_date=datetime.datetime.now().isoformat(),
            event_type=event_type,
        )
        session.add(event2)

        event3 = Event(
            title='Third event',
            start_date=datetime.datetime.now().isoformat(),
            end_date=datetime.datetime.now().isoformat(),
            event_type=event_type,
        )
        session.add(event3)
        session.commit()

    def test_list(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            'List of events',
            '/apiv1/events',
            'LIST',
        ):
            assert status == 200
            assert len(response.json) == 3

            when('The request with form parameter', form=dict(param='param'))
            assert status == '709 Form Not Allowed'

            when('Trying to sorting response', query=dict(sort='id'))
            assert response.json[0]['id'] < response.json[1]['id'] == 2

            when('Sorting the response descending', query=dict(sort='-id'))
            assert response.json[0]['id'] > response.json[1]['id'] == 2

            when('Trying pagination response', query=dict(take=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            when('Trying pagination with skip', query=dict(take=1, skip=1))
            assert response.json[0]['id'] == 2
            assert len(response.json) == 1

            when('Trying filtering response', query=dict(id=1))
            assert response.json[0]['id'] == 1
            assert len(response.json) == 1

            when('Request is not authorized', authorization=None)
            assert status == 401

