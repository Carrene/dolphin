from bddrest import status, response, when

from dolphin.models import Member, EventType
from dolphin.tests.helpers import LocalApplicationTestCase


class TestEventType(LocalApplicationTestCase):

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

        cls.event_type = EventType(
            title='Type',
        )
        session.add(cls.event_type)
        session.commit()

    def test_get(self):
        self.login(self.member.email, self.member.password)

        with self.given(
            f'Getting a event type',
            f'/apiv1/eventtypes/id: {self.event_type.id}',
            f'GET',
        ):
            assert status == 200
            assert response.json['id'] == self.event_type.id
            assert response.json['description'] == self.event_type.description
            assert response.json['title'] == self.event_type.title

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

