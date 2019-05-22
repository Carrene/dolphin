import datetime

from bddrest import status, response, when

from dolphin.models import Member, EventType, Event
from dolphin.tests.helpers import LocalApplicationTestCase, oauth_mockup_server


class TestEventType(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
        )
        session.add(cls.member)

        cls.event_type = EventType(
            title='Type1',
        )
        session.add(cls.event_type)

        cls.event = Event(
            title='Event1',
            event_type=cls.event_type,
            start_date=datetime.datetime.now().isoformat(),
            end_date=datetime.datetime.now().isoformat(),
            repeat='never',
        )
        session.add(cls.event)
        session.commit()

    def test_delete(self):
        self.login(self.member.email)

        with oauth_mockup_server(), self.given(
            f'Deleting an event type',
            f'/apiv1/eventtypes/id: {self.event_type.id}',
            f'DELETE',
        ):
            assert status == 200
            assert response.json['id'] == self.event_type.id

            session = self.create_session()
            assert not session.query(EventType) \
                .filter(EventType.id == self.event_type.id) \
                .one_or_none()

            assert not session.query(Event) \
                .filter(Event.id == self.event.id) \
                .one_or_none()

            when(
                'Intended event type with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended event type not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(a='a')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

