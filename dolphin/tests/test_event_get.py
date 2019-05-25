import datetime

from bddrest import status, response, when

from dolphin.models import Member, Event, EventType
from dolphin.tests.helpers import LocalApplicationTestCase


class TestEvent(LocalApplicationTestCase):

    @classmethod
    def mockup(cls):
        session = cls.create_session()

        cls.member = Member(
            title='First Member',
            email='member1@example.com',
            phone=123456789,
            password='123ABCabc',
        )
        session.add(cls.member)

        event_type = EventType(
            title='First type',
        )

        cls.event1 = Event(
            title='First event',
            start_date=datetime.datetime.now().isoformat(),
            end_date=datetime.datetime.now().isoformat(),
            event_type=event_type,
            repeat='never',
        )
        session.add(cls.event1)
        session.commit()

    def test_get(self):
        self.login(self.member.email, self.member.password)

        with self.given(
            f'Get an event',
            f'/apiv1/events/id: {self.event1.id}',
            f'GET',
        ):
            assert status == 200
            assert response.json['id'] == self.event1.id

            when(
                'Intended group with string type not found',
                url_parameters=dict(id='Alphabetical')
            )
            assert status == 404

            when(
                'Intended group not found',
                url_parameters=dict(id=0)
            )
            assert status == 404

            when(
                'Form parameter is sent with request',
                form=dict(parameter='Invalid form parameter')
            )
            assert status == '709 Form Not Allowed'

            when('Request is not authorized', authorization=None)
            assert status == 401

